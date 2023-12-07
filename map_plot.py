import plotly.express as px
import config
import pandas as pd


def create_stop_plot(stop_times_data: pd.DataFrame):
    '''Create plot of stop ids for selected bus'''
    px.set_mapbox_access_token(config.mapbox_tok)
    df = stop_times_data.drop_duplicates('stop_name').sort_values('stop_sequence').reset_index(drop=True)
    fig = px.scatter_mapbox(df, lat = 'stop_lat', lon = 'stop_lon', hover_name = 'stop_name')
    return(fig)