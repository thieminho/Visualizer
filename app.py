import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QLabel, QFileDialog, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import glob
from pathlib import Path
import importlib
import importlib.util
from PyQt5.QtWidgets import QMessageBox
from PyQt5.uic.properties import QtWidgets
from visualizer.visualizer import Visualizer
from pyvis.network import Network
import networkx as nx


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.list_of_files = glob.glob("plugins\*.py")
        self.list_of_files = [x.split('.')[0] for x in self.list_of_files]
        self.list_of_files = [x.split('\\')[-1] for x in self.list_of_files]
        self.PLUGIN_NAME = "plugins."
        self.fileName = None
        self.result_file = ""
        self.title = 'Visualizer'
        self.left = 10
        self.top = 10
        self.width = 500
        self.height = 400

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.grid = QGridLayout(self)

        self.button_load = QPushButton('Wybierz plik', self)
        self.grid.addWidget(self.button_load, 0, 0)
        self.button_load.clicked.connect(self.on_click)
        self.label_file = QLabel(self)
        self.grid.addWidget(self.label_file, 1, 0)
        self.label_file.setText("Nie wybrano pliku")
        self.label_file.adjustSize()

        self.combo = QComboBox(self)
        self.combo.addItem(" ")
        self.combo.addItems(self.list_of_files)
        self.grid.addWidget(self.combo, 2, 0)
        self.qlabel = QLabel(self)
        self.grid.addWidget(self.qlabel, 3, 0)
        self.qlabel.setText("Nie wybrano modułu")
        self.qlabel.adjustSize()
        self.combo.activated[str].connect(self.onChanged)



        #self.load_graph = QPushButton('Load Test Graph', self)
        #grid.addWidget(self.load_graph, 4, 0)
        #self.load_graph.clicked.connect(self.on_load_clicked)
        #file_name = "transition_result.csv"
        self.visualizer = Visualizer()
        #self.visualizer.set_graph_to_network()
        self.grid.addWidget(self.visualizer, 0, 1, 4, 1)
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 4)
        self.setLayout(self.grid)

        self.button_start = QPushButton("Uruchom", self)
        self.button_start.resize(30, 10)
        self.grid.addWidget(self.button_start, 5, 0)
        self.button_start.clicked.connect(self.analyze_data)
        self.label = QLabel(self)
        #self.label.setFixedSize(100, 50)
        self.grid.addWidget(self.label)
        self.show()


    def on_load_clicked(self):
        print('Loading the test graph')
        self.visualizer.show()

    @pyqtSlot()
    def on_click(self):
        self.options = QFileDialog.Options()
        self.options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                       "All Files (*);;Python Files (*.py)", options=self.options)
        if self.fileName:
            print(self.fileName)
            with open(self.fileName) as file:
                self.loaded_file = pd.read_csv(self.fileName)
        #print(self.loaded_file)
        self.label_file.setText("Wybrany plik: " + self.fileName)
        self.label_file.adjustSize()

    def onChanged(self, text):
        self.qlabel.setText("Wybrany moduł: " + text)
        self.qlabel.adjustSize()
        self.PLUGIN_NAME = "plugins."
        self.PLUGIN_NAME += text
        print(self.PLUGIN_NAME)
        self.plugin_module = importlib.import_module(self.PLUGIN_NAME, ".")


    @pyqtSlot()
    def analyze_data(self):
        if self.PLUGIN_NAME == "plugins." and self.fileName is None:
            msg_plugin_file = QMessageBox()
            msg_plugin_file.setIcon(QMessageBox.Critical)
            msg_plugin_file.setText("Błąd")
            msg_plugin_file.setInformativeText('Nie wybrano modułu i nie wczytano pliku')
            msg_plugin_file.setWindowTitle("Błąd")
            msg_plugin_file.exec_()
        elif self.fileName is None and self.PLUGIN_NAME != "plugins.":
            print("wczytaj plik")
            msg_file = QMessageBox()
            msg_file.setIcon(QMessageBox.Critical)
            msg_file.setText("Błąd")
            msg_file.setInformativeText('Nie wczytano pliku do analizy')
            msg_file.setWindowTitle("Błąd")
            msg_file.exec_()
        elif self.PLUGIN_NAME == "plugins." and self.fileName is not None:
            msg_plugin = QMessageBox()
            msg_plugin.setIcon(QMessageBox.Critical)
            msg_plugin.setText("Błąd")
            msg_plugin.setInformativeText('Nie wybrano modułu')
            msg_plugin.setWindowTitle("Błąd")
            msg_plugin.exec_()
        else:
            self.plugin = self.plugin_module.Plugin(self.fileName)
            execution = self.plugin.execute()
            self.result_file = execution[1]
            if execution[0] == "success":
                self.label.setText("Success, file saved in {}".format(execution[1]))
                self.label.adjustSize()
            else:
                self.label.setText("Error")
                self.label.adjustSize()
        if self.visualizer.used is True:
            del self.visualizer
            self.visualizer = Visualizer()
            self.grid.addWidget(self.visualizer, 0, 1, 4, 1)
            self.visualizer.set_graph_to_network(filename=self.result_file)
            self.visualizer.show()
            #del self.visualizer
        else:
            #self.visualizer = Visualizer()
            # self.visualizer.set_graph_to_network()
            '''grid.addWidget(self.visualizer, 0, 1, 4, 1)
            grid.setColumnStretch(0, 1)
            grid.setColumnStretch(1, 4)
            self.setLayout(grid)'''
            self.visualizer.set_graph_to_network(filename=self.result_file)
            self.visualizer.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
