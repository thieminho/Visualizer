import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QLabel, QFileDialog, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import glob
from pathlib import Path
import importlib
import importlib.util
from app.visualizer.visualizer import Visualizer
from pyvis.network import Network
import networkx as nx


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.list_of_files = glob.glob("plugins\*.py")
        # print(list_of_files)
        self.list_of_files = [x.split('.')[0] for x in self.list_of_files]
        # print(list_of_files)
        self.list_of_files = [x.split('\\')[-1] for x in self.list_of_files]
        # print(list_of_files)
        self.PLUGIN_NAME = "plugins."
        self.fileName = ""
        self.title = 'Visualizer'
        self.left = 10
        self.top = 10
        self.width = 500
        self.height = 400

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        grid = QGridLayout(self)

        self.button_load = QPushButton('Wybierz plik', self)
        grid.addWidget(self.button_load, 0, 0)
        self.button_load.clicked.connect(self.on_click)
        self.label_file = QLabel(self)
        grid.addWidget(self.label_file, 1, 0)
        self.label_file.setText("Nie wybrano pliku")
        self.label_file.adjustSize()

        # jakos te nazwy wyswietlac potem w ladniejszej formie
        self.combo = QComboBox(self)
        self.combo.addItem(" ")
        self.combo.addItems(self.list_of_files)
        grid.addWidget(self.combo, 2, 0)
        self.qlabel = QLabel(self)
        grid.addWidget(self.qlabel, 3, 0)
        self.qlabel.setText("Nie wybrano modułu")
        self.qlabel.adjustSize()
        self.combo.activated[str].connect(self.onChanged)

        self.load_graph = QPushButton('Load Test Graph', self)
        grid.addWidget(self.load_graph, 4, 0)
        self.load_graph.clicked.connect(self.on_load_clicked)
        # TEMPORARY TO CHECK LAYOUT OPTIONS
        data = pd.read_csv("https://www.macalester.edu/~abeverid/data/stormofswords.csv")
        graph = nx.DiGraph()
        self.G = nx.from_pandas_edgelist(data, source='Source', target='Target', edge_attr='Weight', create_using=graph)
        self.visualizer = Visualizer(self.G)
        self.visualizer.set_graph_to_network()
        grid.addWidget(self.visualizer, 0, 1, 4, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 4)
        self.setLayout(grid)
        '''self.button_start = QPushButton("Uruchom", self)
        self.button_start.move(20, 180)
        self.button_start.clicked.connect(self.analyze_data)
        self.label = QLabel(self)
        self.label.setGeometry(200, 200, 200, 30)'''
        self.show()

    @pyqtSlot()
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
            # tu by trzeba ten plik do czegos wczytac jak ustalimy czym on jest
            print(self.fileName)
            with open(self.fileName) as file:
                self.loaded_file = pd.read_csv(self.fileName)
        print(self.loaded_file)
        self.label_file.setText("Wybrany plik: " + self.fileName)
        self.label_file.adjustSize()

    def onChanged(self, text):
        self.qlabel.setText("Wybrany moduł: " + text)
        self.qlabel.adjustSize()
        self.PLUGIN_NAME = "plugins."
        self.PLUGIN_NAME += text
        print(self.PLUGIN_NAME)
        self.plugin_module = importlib.import_module(self.PLUGIN_NAME, ".")
        self.plugin = self.plugin_module.Plugin("hello", key=1)
        result = self.plugin.execute(7, 2)
        print(result)


'''
    def analyze_data(self, text):
        self.qlabel.setText("Wybrany moduł: " + text)
        self.qlabel.adjustSize()
'''

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    # data = pd.read_csv("https://www.macalester.edu/~abeverid/data/stormofswords.csv")
    # graph = nx.DiGraph()
    # G = nx.from_pandas_edgelist(data, source='Source', target='Target', edge_attr='Weight', create_using=graph)
    # got_net = Network(height="80%", width="100%", bgcolor="#222222", font_color="white")
    # got_net.from_nx(G)
    # got_net.save_graph("gameofthrones.html")
    # web = Visualizer(G)
    # web.set_graph_to_network()
    # web.show()
    sys.exit(app.exec_())
