# Module for import data from API 
import config # Need to create locally and add an 'api_tok' to it
import requests
import zipfile
import io
import pandas as pd
from google.protobuf.json_format import MessageToDict


# Testing
# header = {'Authorization' : 'apikey ' + config.api_tok}
# url = 'https://api.transport.nsw.gov.au/v1/gtfs/vehiclepos/buses?debug=true'
# data = requests.get(url, headers = header, verify=False)


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
            'protobuf': ['https://api.transport.nsw.gov.au/v1/gtfs/vehiclepos/buses?debug=true']
            }
    
    # Extract data
    def get_data(self, type, url):
        header = {'Authorization' : 'apikey ' + self.api_key}
        if type == 'zip':
            data = requests.get(url, headers = header, verify = False, stream = True)
            # get zip files
            zfiles = zipfile.ZipFile(io.BytesIO(data.content))

            dataframes = {}
            for name in zfiles.namelist():
                dataframes[name.replace('.txt', '')] = pd.read_csv(zfiles.open(name))
            
            return(dataframes)
        
        elif type == 'protobuf':
            pass

    def tosql(self):
        pass

    def import_all(self):
        # To hold all dataframes from api content
        imported_dataframes = {}
        if self.extract_static:
            for type, urls in self.static_urls.items():
                for url in urls:
                    imported_dataframes.update(self.get_data(type, url))
        
        return(imported_dataframes)

        # INCORPORATE DATAFRAMES FROM PROTOBUF


        # CONVERT TO SQL



if __name__ == '__main__':
    api_key = config.api_tok
    importer = ImportData(api_key, True)

    # Returning dataframes for now
    dfs = importer.import_all()





