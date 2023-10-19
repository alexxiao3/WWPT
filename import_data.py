# Module for import data from API 
import config # Need to create locally and add an 'api_tok' to it
import requests
import zipfile
import io
import pandas as pd
from google.protobuf.json_format import MessageToDict
import gtfs_realtime_pb2




#Testing
# header = {'Authorization' : 'apikey ' + config.api_tok}
# url = 'https://api.transport.nsw.gov.au/v1/gtfs/vehiclepos/buses' # can add debug=true 
# data = requests.get(url, headers = header, verify=False)



# Helper function for unpack dict
def unpack_dict(item):
    if isinstance(item, dict):
        for key, value in item.items():
            yield from unpack_dict(value)
    else:
        yield(item)

#Function to unpack nested dictionary values
# def unpack_dict(item, header_gen=False):
#     if header_gen:
#         headers = []
#         unpacked_rows = list(unpack_helper(item, header_gen, headers))
#         print(headers)
#     else:
#         unpacked_rows = list(unpack_helper(item))
#     if header_gen:
#         return(headers, unpacked_rows)
#     else:
#         return(unpacked_rows)



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
            'protobuf': [['bus_pos','https://api.transport.nsw.gov.au/v1/gtfs/vehiclepos/buses']]
            }
    
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

            # Unpack dictionary
            rows = []
            for i in range(0, len(data_dict)):
                if i == 0:
                    # Generate headers from first iteration
                    headers = []
                    def get_headers(item):
                        if isinstance(item, dict):
                            for key, value in item.items():
                                if not isinstance(value, dict):
                                    headers.append(key)
                                yield from get_headers(value)
                        else:
                            yield(item)
                        
                    rows.append(list(get_headers(data_dict[0])))

                else:
                    rows.append(list(unpack_dict(data_dict[i])))
            
            df = pd.DataFrame(rows, columns=headers)
            return({name:df})


    def tosql(self):
        pass

    def import_all(self):
        # To hold all dataframes from api content
        imported_dataframes = {}
        if self.extract_static:
            for urltype, urls in self.static_urls.items():
                for url in urls:
                    imported_dataframes.update(self.get_data(urltype, url))
        
        for urltype, urls in self.realtime_urls.items():
            for url in urls:
                imported_dataframes.update(self.get_data(urltype, url[1], url[0]))

        return(imported_dataframes)

        # INCORPORATE DATAFRAMES FROM PROTOBUF


        # CONVERT TO SQL



if __name__ == '__main__':
    api_key = config.api_tok
    extract_static = False

    importer = ImportData(api_key, extract_static)

    # Returning dataframes for now
    dfs = importer.import_all()
    print(dfs['bus_pos'])





