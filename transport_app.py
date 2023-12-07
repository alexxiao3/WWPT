# Transport App
import sys
import time
import pandas as pd

from app_ui import Ui_MainWindow
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

import config
from import_data import ImportData
from retrieve_bus_info import BusRetriever
from map_plot import create_stop_plot
from PandasModel import PandasModel

import logger

class DataHolder():
    '''To hold data generated by worker threads'''
    def __init__(self):
        pass

class ImportWorker(QThread):
    '''Thread to import data from server'''
    initialised = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, data_holder):
        super().__init__()
        self.data_holder = data_holder
    
    def run(self):
        self.initialised.emit()
        self.importer = ImportData(config.api_tok, static = True)
        self.data_holder.importer = self.importer
        self.data_holder.importer.import_all()

        self.data_holder.timetable_retriever =\
            BusRetriever(self.data_holder.importer.imported_dataframes['bus_pos'])

        self.finished.emit()

# class ScheduleWorker(QThread):
#     '''Thread to calculate schedule without disrupting UI'''
#     initialised = pyqtSignal()
#     loading_output = pyqtSignal()

#     def __init__(self, data_holder, from_stop, to_stop):
#         super().__init__()
#         self.data_holder=data_holder
#         self.from_stop = from_stop
#         self.to_stop = to_stop

#     def run(self):
#         self.initialised.emit()

#         self.data_holder.
    
    

class Transport_App():
    def __init__(self):
        self.main_win = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.front_end_setup()

        # initialise data app
        self.data_holder = DataHolder()


    def front_end_setup(self):
        '''Set up front end'''
        self.ui.setupUi(self.main_win)
        
        ############### Connecting front end elements to backend ############
        # initial settings
        self.ui.search_schedule_btn.setEnabled(False)
        self.ui.refresh_btn.setEnabled(False)

        # Entering bus number
        self.ui.bus_no_input.textEdited.connect(lambda: 
                                                self.get_route_directions(self.ui.bus_no_input.text()))

        # Selecting route direction
        self.ui.route_dir_input.activated.connect(self.load_trip_data)

        # search button
        self.ui.search_schedule_btn.clicked.connect(self.show_schedule)

        # refresh button
        self.ui.refresh_btn.clicked.connect(self.refresh_schedule)

    # Helper functions
    def console_update(self, text: str):
        '''Output message to console'''
        self.ui.log_text_output.insertPlainText(logger.log_info(text + '\n'))


    def show(self):
        '''Show app and set up'''
        self.main_win.show()

        time.sleep(2)
        self.console_update('Transport app initiated')

        # executed in a thread
        self.import_setups()

    def import_setups(self):
        self.worker = ImportWorker(self.data_holder)
        self.worker.start()
        self.worker.initialised.connect(lambda: self.console_update('Starting import of data from server....'))
        self.worker.finished.connect(lambda: self.console_update('Completed data import from server'))


    ################# Backend Functions ####################
    def get_route_directions(self, bus_no: str):
        '''Get route directions from entered bus number'''
        # disable search schedule
        self.ui.search_schedule_btn.setEnabled(False)
        self.ui.refresh_btn.setEnabled(False)

        try:
            route_ids = self.data_holder.timetable_retriever.get_route_directions(bus_no)
        except:
            return()

        # output route ids to combination 
        self.ui.route_dir_input.clear()
        self.ui.route_dir_input.addItems(route_ids)

    def load_trip_data(self):
        '''Load trip data for selected route direction - no to and from stops'''
        self.ui.refresh_btn.setEnabled(False)

        bus_no = self.ui.bus_no_input.text()
        route_dir = self.ui.route_dir_input.currentText()

        self.stop_times_data = self.data_holder.timetable_retriever.get_stop_times(bus_no, route_dir)

        # Get unique stops
        unique_stops = self.stop_times_data.drop_duplicates('stop_name').sort_values('stop_sequence').reset_index(drop = True)['stop_name']
        self.ui.from_stop_input.clear()
        self.ui.from_stop_input.addItems(unique_stops)
        
        self.ui.to_stop_input.clear()
        self.ui.to_stop_input.addItems(unique_stops)

        # Plot map with all stops
        fig = create_stop_plot(self.stop_times_data)
        self.ui.map_holder.setHtml(fig.to_html(include_plotlyjs='cdn'))

        # Activate the search button
        self.ui.search_schedule_btn.setEnabled(True)
    
    def show_schedule(self):
        '''Show schedule in app'''
        from_stop = self.ui.from_stop_input.currentText()
        to_stop = self.ui.to_stop_input.currentText()

        self.stop_schedule = self.data_holder.timetable_retriever.get_schedule_output(
            self.stop_times_data, to_stop, from_stop
        )

        self.output_live_schedule = self.data_holder.timetable_retriever.output_live_schedule(
            self.stop_schedule
        )

        # Output
        self.ui.schedule_viewer.setModel(PandasModel(self.app_output_view(self.output_live_schedule)))

        self.ui.refresh_btn.setEnabled(True)
    
    def refresh_schedule(self):
        self.data_holder.importer.refresh_live_data()
        self.data_holder.timetable_retriever.refresh_live_data(
            self.data_holder.importer.imported_dataframes['bus_pos']
        )
        self.output_live_schedule = self.data_holder.timetable_retriever.output_live_schedule(
            self.stop_schedule
        )

        # Output
        self.ui.schedule_viewer.setModel(PandasModel(self.app_output_view(self.output_live_schedule)))

    def app_output_view(self, output_table: pd.DataFrame):
        '''Get output dataframe in a nicer view for app'''
        app_output = output_table[['stop_name', 'departure_time', 'departure_time_dest', 
                                   'stop_name_dest', 'Info_type']]
        app_output = app_output.rename({'stop_name':'From Stop', 
                                        'departure_time':'Departing', 
                                        'departure_time_dest':'Arriving', 
                                        'stop_name_dest':'To Stop',
                                        'Info_type':'Timing'})
        
        return(app_output)
        






    


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    transport_win = Transport_App()
    transport_win.show()
    sys.exit(app.exec_()) 

    