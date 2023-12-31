# Module for import data from API 
import config # Need to create locally and add an 'api_tok' to it
import requests
import zipfile
import io
import pandas as pd
from google.protobuf.json_format import MessageToDict
import gtfs_realtime_pb2
import sqlite3

import logger



#Testing
# header = {'Authorization' : 'apikey ' + config.api_tok}
# url = 'https://api.transport.nsw.gov.au/v1/gtfs/vehiclepos/buses' # can add debug=true 
# data = requests.get(url, headers = header, verify=False)



# Helper function for unpack dict
# def unpack_dict(item):
#     if isinstance(item, dict):
#         for key, value in item.items():
#             yield from unpack_dict(value)
#     else:
#         yield(item)


def rewrite_file(file_path: str, msg: str):
    '''Save Last Modified date of static tables from server
    
    Parameters:
    file_path (str): Destination file path 
    msg (str): Message to write into file

    '''
    with open(file_path, 'w') as writer:
        writer.write(msg)


class ImportData():
    def __init__(self, api_key, static = False):
        self.api_key = api_key
        self.extract_static = static 

        # Collection of urls added here
        # in the format of {content_type : [urls]}
        self.static_urls = {
            'zip' : ['https://api.transport.nsw.gov.au/v1/gtfs/schedule/buses']
            }
        self.realtime_urls = {
            'protobuf': [['bus_pos','https://api.transport.nsw.gov.au/v1/gtfs/realtime/buses']]
            }
        
        # Sql database
        self.db = 'TransportDB.sqlite'
        # This is a constant used to determine when the last save date 
        # of modified is
        self.lastmodified = 'lastmodified.txt'
    
    # Extract data
    def get_data(self, urltype, url, name = None):
        header = {'Authorization' : 'apikey ' + self.api_key}
        if urltype == 'zip':
            data_head = requests.head(url, headers = header, verify = False)
            # Check last save date
            try: # if no last save file, then request
                with open(self.lastmodified, 'r') as file:
                    last_mod = file.read()
                if last_mod != data_head.headers['Last-Modified']:
                    data = requests.get(url, headers = header, verify = False, stream = True)

                    # get zip files
                    zfiles = zipfile.ZipFile(io.BytesIO(data.content))

                    dataframes = {}
                    for name in zfiles.namelist():
                        dataframes[name.replace('.txt', '')] = pd.read_csv(zfiles.open(name))

                    rewrite_file(self.lastmodified, data_head.headers['Last-Modified'])
                    
                    return(dataframes)
                else:
                    return({})
            except: # also download
                data = requests.get(url, headers = header, verify = False, stream = True)

                # get zip files
                zfiles = zipfile.ZipFile(io.BytesIO(data.content))

                dataframes = {}
                for name in zfiles.namelist():
                    dataframes[name.replace('.txt', '')] = pd.read_csv(zfiles.open(name))
                
                rewrite_file(self.lastmodified, data.headers['Last-Modified'])

                return(dataframes)
                
        
        elif urltype == 'protobuf':
            data = requests.get(url, headers = header, verify = False)

            # Decode data
            reader = gtfs_realtime_pb2.FeedMessage()
            reader.ParseFromString(data.content)
            # Convert to dict
            data_dict = MessageToDict(reader)

            return({name:data_dict})


    def tosql(self, imported_dataframes):
        conn = sqlite3.connect(self.db)

        # real time url names
        realtime_names = []
        for key, value in self.realtime_urls.items():
            names = [x[0] for x in value]
            realtime_names += names

        for name, df in imported_dataframes.items():
            if name not in  realtime_names: # don't save down live data
                df.to_sql(name = name, con = conn, if_exists = 'replace')
        conn.close()


    def import_all(self):
        # To hold all dataframes from api content
        self.imported_dataframes = {}
        
        logger.log_info('Starting extraction of static data...')
        if self.extract_static:
            for urltype, urls in self.static_urls.items():
                for url in urls:
                    self.imported_dataframes.update(self.get_data(urltype, url))
        
        logger.log_info('Starting extraction of live data...')
        for urltype, urls in self.realtime_urls.items():
            for url in urls:
                self.imported_dataframes.update(self.get_data(urltype, url[1], url[0]))

        # upload statics to sql
        self.tosql(self.imported_dataframes)
    
    def refresh_live_data(self):
        '''Update live data'''
        for urltype, urls in self.realtime_urls.items():
            for url in urls:
                new_data = self.get_data(urltype, url[1], url[0])[url[0]]
                if new_data['header']['timestamp'] != \
                    self.imported_dataframes['bus_pos']['header']['timestamp']:
                    self.imported_dataframes.update({url[0]:new_data})


if __name__ == '__main__':
    api_key = config.api_tok
    extract_static = True

    importer = ImportData(api_key, extract_static)
    importer.import_all()






