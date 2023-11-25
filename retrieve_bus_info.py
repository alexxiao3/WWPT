# Used to return bus information
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

class BusInformation():
    def __init__(self):
        # Create sql engine and store static tables
        self.engine = create_engine('sqlite:///TransportDB.sqlite')
        self.routes = pd.read_sql('select * from routes', self.engine)
        self.trips = pd.read_sql('select * from trips', self.engine)

        # Set up tables
        #self.routes['lookup'] = self.routes['route_short_name'] + self.routes['route_long_name']
        #self.trips['lookup'] = self.trips['route_id'] + self.trips['route_direction']

    def get_route_id(self, bus_number : str) -> list:
        # possible for function to return multiple route ids
        return(self.routes['route_id'][self.routes['route_short_name'] == bus_number].values)
    
    def get_trip_list(self, bus_number: str, route_direction: str):
        '''Get list of trip IDs from a route number and direction.'''
        route_ids = self.get_route_id(bus_number)
        trip_list = self.trips.loc[np.isin(self.trips['route_id'],route_ids) &
                                    (self.trips['route_direction']==route_direction)]
        return(trip_list)




class BusRetriever(BusInformation):
    def __init__(self, busdata : pd.DataFrame):
        super().__init__()
        self.busdata = busdata['entity']
        
        # get bus list 
        self.lookup_directory()

    # not intended to be user function
    def lookup_directory(self):
        for i in range(len(self.busdata)):
            bus_info = self.busdata[i]
            data_dict = {'id': bus_info['id']}
            data_dict.update(bus_info['tripUpdate']['trip'])

            if i == 0: # initialise lookup df
                self.bus_list = pd.DataFrame([data_dict])
            else:
                self.bus_list = pd.concat([self.bus_list, pd.DataFrame([data_dict])])
    

if __name__ == '__main__':
    pass
            
