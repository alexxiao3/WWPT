# Used to return bus information
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import create_engine
import time
from datetime import timedelta

# Weekday converter constant
WEEKDAY = {0:'monday', 1:'tuesday', 2:'wednesday', 3: 'thursday', 4:'friday', 5:'saturday', 6:'sunday',
           -1:'sunday', 7:'monday'}

# custom time function
def to_time(time_str: str):
    '''Change string to time object'''
    try:
        return(datetime.strptime(time_str, '%H:%M:%S').time())
    except: # incorrect format when 24 hour time goes past 24 (next day)
        hour = int(time_str[0:2])
        hour -= 24
        time_str = str(hour)+time_str[2:]
        return(datetime.strptime(time_str, '%H:%M:%S').time())

def addtime(time_obj: time, delay: int):
    '''Add delay to time object'''
    old_date = datetime.strptime('2018-10-10' + ' ' +str(time_obj), '%Y-%m-%d %H:%M:%S')
    new_date = old_date + timedelta(seconds = delay)
    return(new_date.time())


class BusInformation():
    def __init__(self):
        # Create sql engine and store static tables
        self.engine = create_engine('sqlite:///TransportDB.sqlite')
        self.routes = pd.read_sql('select * from routes', self.engine)
        self.trips = pd.read_sql('select * from trips', self.engine)
        self.calendar = pd.read_sql('select * from calendar', self.engine)
        self.stops = pd.read_sql('select * from stops', self.engine)

        # Set up tables
        #self.routes['lookup'] = self.routes['route_short_name'] + self.routes['route_long_name']
        #self.trips['lookup'] = self.trips['route_id'] + self.trips['route_direction']

    def get_route_id(self, bus_number : str) -> list:
        '''Get list of route ids given a bus number'''
        # possible for function to return multiple route ids
        return(self.routes['route_id'][self.routes['route_short_name'] == bus_number].values)
    
    def get_route_directions(self, bus_number : str):
        '''Get list of route directions given a bus number - both directions included'''
        route_ids = self.get_route_id(bus_number)
        route_directions = self.trips.loc[np.isin(self.trips['route_id'], route_ids), 'route_direction']
        return(np.unique(route_directions))


    def get_trip_list(self, bus_number: str, route_direction: str):
        '''Get list of trip IDs from a route number and direction.'''
        route_ids = self.get_route_id(bus_number)
        trip_list = self.trips.loc[np.isin(self.trips['route_id'],route_ids) &
                                    (self.trips['route_direction']==route_direction)]
        return(trip_list.reset_index(drop=True))
    
    def get_stop_times(self, bus_number: str, route_direction:str):
        '''Get all stops of a selected bus number and route direction'''
        trip_list = self.get_trip_list(bus_number, route_direction)
        trip_list['trip_id'] = trip_list['trip_id'].astype(str)
        trip_query = ','.join(trip_list['trip_id'])
        stop_times_data = pd.read_sql(f'select * from stop_times where trip_id in ({trip_query})', self.engine)
        
        # merge on stop information
        stop_times_data = stop_times_data.merge(self.stops, how = 'left', on = 'stop_id')
        stop_times_data['trip_id'] = stop_times_data['trip_id'].astype(str)
        return(stop_times_data)
    
    def append_calendar_info(self, stop_schedule: pd.DataFrame):
        '''Function to add operating days to a schedule'''
        if 'service_id' in stop_schedule.columns:
            stop_schedule = stop_schedule.merge(self.calendar, how = 'left', on = 'service_id')
        else:
            # add service id column on stop schedule 
            stop_schedule['service_id'] = self.trips['service_id'][[list(self.trips['trip_id'].astype(str)).index(stop_schedule['trip_id'][i])
                                                for i in range(len(stop_schedule))]].reset_index(drop = True)
            stop_schedule = stop_schedule.merge(self.calendar, how = 'left', on = 'service_id')
        return(stop_schedule)

    
    def prep_timetable(self, stop_schedule: pd.DataFrame):
        '''Prep timetable for output calculation'''
        # create flag for if departure time at from stop ticked over to next day
        stop_schedule['next_day'] = [1 if int(stop_schedule['departure_time'][i][0:2])>=24 else 0
                                     for i in range(len(stop_schedule))]
        
        # change departure time columns to time objects
        stop_schedule[['departure_time', 'departure_time_dest']] = np.vectorize(to_time)(stop_schedule[['departure_time', 'departure_time_dest']])
        
        # order by departure time of from stop
        stop_schedule = stop_schedule.sort_values('departure_time').reset_index(drop = True)
        
        return(stop_schedule)
        
    
    def get_schedule_output(self, stop_times_data, to_stop, from_stop):
        # only take rows that have the to and from stop
        stop_schedule = stop_times_data[np.isin(stop_times_data['stop_name'], [to_stop, from_stop])].reset_index(drop = True)
        
        # filter for trips that have both stops
        unique_trip_ids, count = np.unique(stop_schedule['trip_id'], return_counts=True)
        keep_trip_ids = unique_trip_ids[count==2]
        stop_schedule = stop_schedule[np.isin(stop_schedule['trip_id'], keep_trip_ids)].reset_index(drop = True)
        
        # change structure of stop_schedule have to and from stop information in one row
        stop_info = ['trip_id', 'stop_id', 'stop_sequence', 'stop_name', 'departure_time', 'stop_lat', 'stop_lon'] # required cols
        stop_info_dest = [x + '_dest' for x in stop_info]

        stop_schedule_final = stop_schedule[np.arange(len(stop_schedule))%2 == 0].reset_index(drop = True)
        stop_schedule_final[stop_info_dest] = stop_schedule.loc[np.arange(len(stop_schedule))%2 == 1, stop_info].reset_index(drop = True)
        
        # add calendar data
        stop_schedule_final = self.append_calendar_info(stop_schedule_final)
        
        self.prep_timetable(stop_schedule_final)
        
        return(stop_schedule_final)
    

        
    def output_timetable(self, stop_schedule: pd.DataFrame):
        '''Function that outputs timetable based on current time information'''
        # wanted columns in output
        output_cols = ['stop_name', 'departure_time', 'departure_time_dest', 'stop_name_dest', 'trip_id',
                       'stop_sequence', 'stop_sequence_dest']
        
        # time information regarding now
        time_now = datetime.now().time()
        today = WEEKDAY[datetime.today().weekday()]
        yesterday = WEEKDAY[datetime.today().weekday()-1]
        tomorrow = WEEKDAY[datetime.today().weekday()-1]
        
        # segment 1: scheduled stops today past current time
        segment1 = stop_schedule.loc[(stop_schedule['departure_time']>=time_now)&(stop_schedule[today]==1),
                                     output_cols].reset_index(drop = True)
        
        # segment 2: scheduled stops yesterday with departure time past current time today 
        segment2 = stop_schedule.loc[(stop_schedule['departure_time']>=time_now)&(stop_schedule[yesterday]==1)&
                                 (stop_schedule['next_day'] == 1), 
                                 output_cols].reset_index(drop = True)
        
        output_schedule = pd.concat([segment1, segment2], ignore_index=True)
        output_schedule = output_schedule.sort_values('departure_time').reset_index(drop = True)
        
        # segment 3 is optional only if length of last 2 stops isn't past 20
        if len(output_schedule) < 30: # want to output 30 buses
            # this suggests that we are at the end of the day, so we need to output 2 types:
            #       - bus scheduled tomorrow
            #       - bus scheduled today that has departure time at the stop on the next day
            segment3 = stop_schedule.loc[(stop_schedule[tomorrow]==1)| # first cond
                                         ((stop_schedule[today]==1)&(stop_schedule['next_day']==1)), # second cond
                                         output_cols].reset_index(drop = True) 

            segment3 = segment3.sort_values('departure_time').reset_index(drop = True)
            segment3 = segment3[0:(30-len(output_schedule))]
            
            # join on output_schedule
            output_schedule = pd.concat([output_schedule, segment3], ignore_index=True)
        else:
            output_schedule = output_schedule[0:30]
        
        output_schedule['Info_type'] = ['Scheduled']*len(output_schedule)

        return(output_schedule)
            
        
        
        
        




class BusRetriever(BusInformation):
    def __init__(self, busdata : pd.DataFrame):
        super().__init__()
        self.busdata = busdata['entity']
        
        # get bus list 
        self.bus_directory()

    # not intended to be user function
    def bus_directory(self):
        '''Create a directory for the current buses'''
        for i in range(len(self.busdata)):
            bus_info = self.busdata[i]
            data_dict = {'id': bus_info['id']}
            data_dict.update(bus_info['tripUpdate']['trip'])

            if i == 0: # initialise lookup df
                self.bus_list = pd.DataFrame([data_dict])
            else:
                self.bus_list = pd.concat([self.bus_list, pd.DataFrame([data_dict])])
        
        self.bus_list = self.bus_list.reset_index(drop = True)
    
    # Get bus schedule 
    def get_live_trips(self, trip_ids: list):
        '''Return live trips for selected trip ids'''
        # Existing trips
        live_trips = self.bus_list.loc[np.isin(self.bus_list['tripId'], trip_ids)]
        
        if len(live_trips) == 0: # no live trips of inserted trip ids
            return(None)
        else:
            live_trips = live_trips.reset_index(drop=True)
            return(live_trips)
    

    def unpack_live_schedule(self, bus_data: dict, from_stop_seq: int, 
                             to_stop_seq: int):
        '''Get live departure times at to and from stop sequence for given live bus'''
        # Get list of sequences
        stop_updates = bus_data['tripUpdate']['stopTimeUpdate']
        stop_sequences = np.array([stop_updates[i]['stopSequence'] for i in 
                                   range(len(stop_updates))])

        if from_stop_seq in stop_sequences and to_stop_seq in stop_sequences:
            # Get time of departure at the from and to stop 
            # from stop:
            from_stop = np.array(stop_updates)[stop_sequences==from_stop_seq][0]
            if from_stop['scheduleRelationship'] == 'SCHEDULED':
                from_delay = from_stop['departure']['delay']
            else:
                return() # no schedule

            # to stop:
            to_stop = np.array(stop_updates)[stop_sequences==to_stop_seq][0]
            if to_stop['scheduleRelationship'] == 'SCHEDULED':
                to_delay = to_stop['departure']['delay']
            else:
                return() # no schedule
            
            return(from_delay, to_delay)

        else:
            return() # live trip doesn't stop at required stops


    def update_live_schedule(self, output_schedule: pd.DataFrame):
        '''Update scheduled information with live transport information 
        if it exists
        '''
        output_schedule = output_schedule.copy()
        
        # get list of trip ids from output schedule (assuming unique here)
        trip_ids = np.unique(output_schedule['trip_id'])
        live_trips = self.get_live_trips(trip_ids)

        if live_trips is not None:
            # for live trips, update schedule information with that 
            for trip_id in live_trips['tripId']:
                # get live bus data associated with trip id
                bus_data = np.array(self.busdata)[self.bus_list['tripId'] == trip_id][0]
                
                # get from and to stop
                from_stop_seq = output_schedule.loc[output_schedule['trip_id'] == trip_id, 'stop_sequence'].values[0]
                to_stop_seq = output_schedule.loc[output_schedule['trip_id'] == trip_id, 'stop_sequence_dest'].values[0]
                
                # get delay times
                # try:
                from_delay, to_delay = self.unpack_live_schedule(bus_data, from_stop_seq, to_stop_seq)
                output_schedule.loc[output_schedule['trip_id']==trip_id, 'departure_time'] = \
                    addtime(output_schedule.loc[output_schedule['trip_id']==trip_id, 'departure_time'].values[0], from_delay)
                output_schedule.loc[output_schedule['trip_id']==trip_id, 'departure_time_dest'] = \
                    addtime(output_schedule.loc[output_schedule['trip_id']==trip_id, 'departure_time_dest'].values[0], to_delay)
                
                # update flag
                early_late = 'early' if from_delay < 0 else 'late'
                output_schedule.loc[output_schedule['trip_id']==trip_id,'Info_type'] = \
                    f'{abs(round(from_delay/60))} minutes {early_late}'
                
                    
                # except:
                #     print(f'{trip_id} live data could not be updated.')
            
            return(output_schedule)
        else:
            return(output_schedule)
    
    def output_live_schedule(self, stop_schedule: pd.DataFrame):
        '''Outputs bus schedule with live data update'''
        output_schedule = self.output_timetable(stop_schedule)
        live_output_schedule = self.update_live_schedule(output_schedule)
        
        return(live_output_schedule)
            
        

if __name__ == '__main__':
    pass
            
