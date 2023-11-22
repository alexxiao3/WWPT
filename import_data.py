# Module for import data from API 
import config # Need to create locally and add an 'api_tok' to it
import requests
import zipfile
import io
import pandas as pd
from google.protobuf.json_format import MessageToDict
import gtfs_realtime_pb2
import sqlite3




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
    
    # Extract data
    def get_data(self, urltype, url, name = None):
        header = {'Authorization' : 'apikey ' + self.api_key}
        if urltype == 'zip':
            data = requests.get(url, headers = header, verify = False, stream = True)
            # get zip files
            zfiles = zipfile.ZipFile(io.BytesIO(data.content))

            dataframes = {}
            for name in zfiles.namelist():
                dataframes[name.replace('.txt', '')] = pd.read_csv(zfiles.open(name))
            
            return(dataframes)
        
        elif urltype == 'protobuf':
            data = requests.get(url, headers = header, verify = False)

            # Decode data
            reader = gtfs_realtime_pb2.FeedMessage()
            reader.ParseFromString(data.content)
            # Convert to dict
            data_dict = MessageToDict(reader)['entity']

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
        if self.extract_static:
            for urltype, urls in self.static_urls.items():
                for url in urls:
                    self.imported_dataframes.update(self.get_data(urltype, url))
        
        for urltype, urls in self.realtime_urls.items():
            for url in urls:
                self.imported_dataframes.update(self.get_data(urltype, url[1], url[0]))

        # upload statics to sql
        self.tosql(self.imported_dataframes)


if __name__ == '__main__':
    api_key = config.api_tok
    extract_static = False

    importer = ImportData(api_key, extract_static)
    importer.import_all()






