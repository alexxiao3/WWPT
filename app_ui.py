# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\axiao3\OneDrive - KPMG\Documents\PyQt\WWPT\transport_app.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1099, 882)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.schedule_viewer = QtWidgets.QTableView(self.centralwidget)
        self.schedule_viewer.setObjectName("schedule_viewer")
        self.schedule_viewer.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.gridLayout.addWidget(self.schedule_viewer, 1, 0, 1, 2)
        self.refresh_btn = QtWidgets.QPushButton(self.centralwidget)
        self.refresh_btn.setObjectName("refresh_btn")
        self.gridLayout.addWidget(self.refresh_btn, 2, 0, 1, 2)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.bus_no_label = QtWidgets.QLabel(self.centralwidget)
        self.bus_no_label.setObjectName("bus_no_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.bus_no_label)
        self.bus_no_input = QtWidgets.QLineEdit(self.centralwidget)
        self.bus_no_input.setObjectName("bus_no_input")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.bus_no_input)
        self.select_trip_label = QtWidgets.QLabel(self.centralwidget)
        self.select_trip_label.setObjectName("select_trip_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.select_trip_label)
        self.route_dir_input = QtWidgets.QComboBox(self.centralwidget)
        self.route_dir_input.setObjectName("route_dir_input")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.route_dir_input)
        self.from_stop_label = QtWidgets.QLabel(self.centralwidget)
        self.from_stop_label.setObjectName("from_stop_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.from_stop_label)
        self.from_stop_input = QtWidgets.QComboBox(self.centralwidget)
        self.from_stop_input.setObjectName("from_stop_input")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.from_stop_input)
        self.to_stop_label = QtWidgets.QLabel(self.centralwidget)
        self.to_stop_label.setObjectName("to_stop_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.to_stop_label)
        self.to_stop_input = QtWidgets.QComboBox(self.centralwidget)
        self.to_stop_input.setObjectName("to_stop_input")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.to_stop_input)
        self.log_text_output = QtWidgets.QTextBrowser(self.centralwidget)
        self.log_text_output.setObjectName("log_text_output")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.log_text_output)
        self.search_schedule_btn = QtWidgets.QPushButton(self.centralwidget)
        self.search_schedule_btn.setObjectName("search_schedule_btn")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.search_schedule_btn)
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)
        self.map_holder = QtWebEngineWidgets.QWebEngineView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.map_holder.sizePolicy().hasHeightForWidth())
        self.map_holder.setSizePolicy(sizePolicy)
        self.map_holder.setObjectName("map_holder")
        self.gridLayout.addWidget(self.map_holder, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1099, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.refresh_btn.setText(_translate("MainWindow", "Refresh live data"))
        self.bus_no_label.setText(_translate("MainWindow", "Enter Bus Number: "))
        self.select_trip_label.setText(_translate("MainWindow", "Select trip:"))
        self.from_stop_label.setText(_translate("MainWindow", "From Stop:"))
        self.to_stop_label.setText(_translate("MainWindow", "To Stop:"))
        self.search_schedule_btn.setText(_translate("MainWindow", "Search schedule"))
