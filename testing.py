# testing
import pandas as pd
import requests
from google.protobuf.json_format import MessageToDict
import gtfs_realtime_pb2
import numpy as np
from sqlalchemy import create_engine

from import_data import ImportData
from retrieve_bus_info import BusRetriever
import config


# sql engine
engine = create_engine("sqlite:///TransportDB.sqlite")

# Import data
api_key = config.api_tok
extract_static = True

importer = ImportData(api_key, extract_static)
importer.import_all()

# Bus retriever
bus_no = '501'
route_dir = 'Central Pitt St to Parramatta via Pyrmont & Victoria Rd'
from_stop = 'Victoria Rd at Hughes Ave'
to_stop = 'Parramatta Station, Stand B3'

retriever = BusRetriever(importer.imported_dataframes['bus_pos'])

# Get associated trip list 
# trip_list = retriever.get_trip_list(bus_no, route_dir).astype(str)
# live_trips = retriever.get_live_trips(trip_list['trip_id'])


# # trip list is used to get scheduled information
# # live trips used to get live information to replace scheduled


# # read in stop times data
# query = ','.join(trip_list['trip_id'])

# # import stop times data
# stop_times_data = pd.read_sql(f'select * from stop_times where trip_id in ({query})', engine)
# stop_times_data['trip_id'] = stop_times_data['trip_id'].astype(str)

# # get individual stop data
# stop_data = pd.read_sql('select * from stops', engine)
# stop_times_data = stop_times_data.merge(stop_data, how = 'left', on = 'stop_id')


# # filter stop time data for required stops
# stop_times_data = stop_times_data[np.isin(stop_times_data['stop_name'], [from_stop, to_stop])].reset_index(drop = True)

# # only include trips with both from and to stops
# unique_trip_ids, count = np.unique(stop_times_data['trip_id'], return_counts=True)
# keep_trip_ids = unique_trip_ids[count==2]
# stop_times_data = stop_times_data[np.isin(stop_times_data['trip_id'], keep_trip_ids)].reset_index(drop = True)


# stop_info = ['trip_id', 'stop_id', 'stop_name', 'departure_time', 'stop_lat', 'stop_lon']
# stop_info_dest = [x + '_dest' for x in stop_info]

# stop_schedule = stop_times_data[np.arange(len(stop_times_data))%2 == 0].reset_index(drop=True)
# stop_schedule[stop_info_dest] = stop_times_data.loc[np.arange(len(stop_times_data))%2==1, stop_info].reset_index(drop = True)

# # add service id
# stop_schedule['service_id'] = trip_list['service_id'][[list(trip_list['trip_id']).index(stop_schedule['trip_id'][i])
#                                                         for i in range(len(stop_schedule))]].reset_index(drop = True)

# # join on calendar
# stop_schedule = stop_schedule.merge(calendar_data, how = 'left', on = 'service_id')



stop_times_data = retriever.get_stop_times(bus_no, route_dir)
stop_schedule = retriever.get_schedule_output(stop_times_data, to_stop, from_stop)

# output schedule
output_schedule = retriever.output_timetable(stop_schedule)

#1878422