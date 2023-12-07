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

import plotly.express as px


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


stop_times_data = retriever.get_stop_times(bus_no, route_dir)
stop_schedule = retriever.get_schedule_output(stop_times_data, to_stop, from_stop)
output_schedule = retriever.output_timetable(stop_schedule)

# output schedule
live_output = retriever.output_live_schedule(stop_schedule)

# refresh
importer.refresh_live_data()
retriever.refresh_live_data(importer.imported_dataframes['bus_pos'])
live_output_refreshed = retriever.output_live_schedule(stop_schedule)

#1878422


# PLOTLY 
px.set_mapbox_access_token(config.mapbox_tok)
df = stop_times_data.drop_duplicates('stop_name').sort_values('stop_sequence').reset_index(drop=True)
fig = px.scatter_mapbox(df, lat = 'stop_lat', lon = 'stop_lon', hover_name = 'stop_name')