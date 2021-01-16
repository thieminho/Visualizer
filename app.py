import sys

'''current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)'''
# from application import mainWindow
import glob
import importlib
import importlib.util
import shutil
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QComboBox, QLabel, QFileDialog, QGridLayout, \
    QMessageBox, QVBoxLayout, QListWidget, QApplication
from visualizer.visualizer import Visualizer
import timeit


class App(QWidget):
    def __init__(self):
        super().__init__()
        # self.mutex = QMutex()
        self.setStyleSheet("background-color: #E7ECFA;")
        # generating list of available plugins
        self.list_of_files = glob.glob("plugins\*.py")
        self.list_of_files = [x.split('.')[0] for x in self.list_of_files]
        self.list_of_files = [x.split('\\')[-1] for x in self.list_of_files]
        self.PLUGIN_NAME = "plugins."
        self.filename = None
        self.last_filename_from_filedialog = None
        self.result_file = ""
        # set size and title of main window
        self.title = 'Visualizer'
        self.left = 10
        self.top = 10
        self.width = 500
        self.height = 400
        self.init_ui()
        self.param_dialog = QFileDialog(self)

    def init_ui(self):
        # main window
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.parameters = None
        self.grid = QGridLayout(self)
        # self.grid.addLayout(self.parameters, 0, 2, 4, 1)

        # button to load xes/csv file
        self.button_load = QPushButton('Dodaj plik', self)
        self.button_load.setStyleSheet("background-color: #8FAAF7;")
        self.grid.addWidget(self.button_load, 1, 0)
        self.button_load.clicked.connect(self.on_click)
        self.label_file = QLabel(self)
        self.grid.addWidget(self.label_file, 0, 0)
        self.label_file.setText("Dodaj/upuść plik:")
        self.label_file.adjustSize()

        self.listbox_view = ListBoxWidget(self)
        self.listbox_view.setStyleSheet("background-color: #BBCCFB;")
        self.grid.addWidget(self.listbox_view, 2, 0)
        self.btn = QPushButton('Usuń plik z listy', self)
        self.grid.addWidget(self.btn, 3, 0)
        self.btn.clicked.connect(self.remove_file_from_list)
        # combobox to choose plugin
        self.combo = QComboBox(self)
        self.combo.setStyleSheet("background-color: #8FAAF7;")
        self.combo.addItem(" ")
        self.combo.addItems(self.list_of_files)
        self.grid.addWidget(self.combo, 6, 0)
        self.qlabel = QLabel(self)
        self.grid.addWidget(self.qlabel, 5, 0)
        self.qlabel.setText("Wybierz moduł:")
        self.qlabel.adjustSize()
        # run on_changed function after click on name of plugin
        self.combo.activated[str].connect(self.on_changed)

        # create object of visualizer and add it to window
        self.visualizer = Visualizer()
        self.visualizer.setStyleSheet("background-color: #8FAAF7;")
        self.grid.addWidget(self.visualizer, 0, 1, -1, 1)
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 4)
        self.setLayout(self.grid)

        # button to start processing
        self.button_start = QPushButton("Uruchom", self)
        self.button_start.setStyleSheet("background-color: #8FAAF7;")
        self.button_start.resize(30, 10)
        self.grid.addWidget(self.button_start, 7, 0)
        # run analyze_data after click on button
        self.button_start.clicked.connect(self.analyze_data)
        self.label = QLabel(self)
        # self.label.setFixedSize(100, 50)
        self.grid.addWidget(self.label, 8, 1)

        self.button_new_plugin = QPushButton("Dodaj nowy moduł", self)
        self.button_new_plugin.setStyleSheet("background-color: #8FAAF7;")
        self.button_new_plugin.resize(30, 10)
        self.grid.addWidget(self.button_new_plugin, 8, 0)
        self.button_new_plugin.clicked.connect(self.add_plugin)
        self.show()

    def add_plugin(self):
        self.options = QFileDialog.Options()
        self.options |= QFileDialog.DontUseNativeDialog
        self.new_plugin_path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik modułu", "",
                                                              "All Files (*);;Python Files (*.py)",
                                                              options=self.options)
        # albo my_dir = QtGui.QFileDialog.getExistingDirectory jak chcemy foldery
        if self.new_plugin_path:
            '''
            self.temp_path = os.path.dirname(os.path.abspath(__file__))
            self.temp_path = PurePath(self.temp_path).parts[0:-1]
            print(self.temp_path)
            self.to_directory = os.path.join(*self.temp_path, "/plugins")
            print("to" + self.to_directory)
            print(self.new_plugin_path)'''
            shutil.copy(self.new_plugin_path, "./plugins")
            self.list_of_files = glob.glob("plugins\*.py")
            self.list_of_files = [x.split('.')[0] for x in self.list_of_files]
            self.list_of_files = [x.split('\\')[-1] for x in self.list_of_files]
            print(self.list_of_files)
            self.combo.clear()
            self.combo.addItem(" ")
            self.combo.addItems(self.list_of_files)

    def remove_file_from_list(self):
        for item in self.listbox_view.selectedItems():
            self.listbox_view.takeItem(self.listbox_view.row(item))

    @pyqtSlot()
    def on_click(self):
        # select file for processing and assign name to self.filename
        self.options = QFileDialog.Options()
        self.options |= QFileDialog.DontUseNativeDialog
        self.filename, _ = QFileDialog.getOpenFileName(self, "Wybierz plik", "",
                                                       "All Files (*);;Python Files (*.py)", options=self.options)
        if self.filename != "":
            self.listbox_view.addItem(self.filename)
            self.last_filename_from_filedialog = self.filename

    def on_changed(self, text):
        # select plugin from combobox
        self.qlabel.setText("Wybrany moduł: " + text)
        self.qlabel.adjustSize()

        # print(self.filename)
        self.PLUGIN_NAME = "plugins."
        self.PLUGIN_NAME += text
        self.plugin_module = importlib.import_module(self.PLUGIN_NAME, ".")
        plugin = self.plugin_module.Plugin()
        # print(self.grid.columnCount())
        # load parameters from plugin using fill_my_parameters() class function
        if self.parameters == None:
            print('Adding parameters to window')
            self.parameters = QVBoxLayout()
            self.grid.addLayout(self.parameters, 0, 2, 4, 1)
            self.fill_base_parameters()
            # add fill_specific_parameters()
            print('Checking alg parameters')
            if plugin.hasParameters:
                print('Calling fillmyparameters from first if')
                self.add_parameters_button.setEnabled(True)
                self.param_dialog = plugin.myDialog
                self.add_parameters_button.clicked.connect(self.param_dialog.exec_)
                #connect add_parameters_button with function fill_my_parameters to show new widget
                # plugin.fill_my_parameters(self, self.add_parameters_button)
            else:
                self.add_parameters_button.setEnabled(False)
        else:
            self.grid.addLayout(self.parameters, 0, 2, 4, 1)
            self.clearLayout(self.parameters)
            self.fill_base_parameters()
            print('Checking alg parameters')
            if plugin.hasParameters:
                print('Calling fillmyparameters')
                self.add_parameters_button.setEnabled(True)
                self.param_dialog = plugin.myDialog
                #connect add_parameters_button with function fill_my_parameters to show new widget
                self.add_parameters_button.clicked.connect(self.param_dialog.exec_)
                # plugin.fill_my_parameters(self, self.add_parameters_button)
            else:
                self.add_parameters_button.setEnabled(False)
        if not self.button_start.isEnabled():
            self.button_start.setEnabled(True)
        print("end")

    @pyqtSlot()
    def analyze_data(self):
        # checking if plugin and file have been selected
        # print(self.listbox_view.currentItem())
        print("fn" + self.filename)
        if self.listbox_view.currentItem():
            self.filename = self.listbox_view.currentItem().text()
        elif self.filename is not None:
            pass
        else:
            self.filename = self.last_filename_from_filedialog

        self.label_file.setText("Wybrany plik: " + self.filename)
        self.label_file.adjustSize()
        if self.PLUGIN_NAME == "plugins." and self.filename is None:
            msg_plugin_file = QMessageBox()
            msg_plugin_file.setIcon(QMessageBox.Critical)
            msg_plugin_file.setText("Błąd")
            msg_plugin_file.setInformativeText('Nie wybrano modułu i nie wczytano pliku')
            msg_plugin_file.setWindowTitle("Błąd")
            msg_plugin_file.exec_()
        elif self.filename is None and self.PLUGIN_NAME != "plugins.":
            print("wczytaj plik")
            msg_file = QMessageBox()
            msg_file.setIcon(QMessageBox.Critical)
            msg_file.setText("Błąd")
            msg_file.setInformativeText('Nie wczytano pliku do analizy')
            msg_file.setWindowTitle("Błąd")
            msg_file.exec_()
        elif self.PLUGIN_NAME == "plugins." and self.filename is not None:
            msg_plugin = QMessageBox()
            msg_plugin.setIcon(QMessageBox.Critical)
            msg_plugin.setText("Błąd")
            msg_plugin.setInformativeText('Nie wybrano modułu')
            msg_plugin.setWindowTitle("Błąd")
            msg_plugin.exec_()
        else:

            self.plugin = self.plugin_module.Plugin()
            starttime = timeit.default_timer()
            execution = self.plugin.execute(self.filename)
            endtime = timeit.default_timer()
            print(f'Algorithm time execution = {endtime-starttime} ms')
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
            self.grid.addWidget(self.visualizer, 0, 1, -1, -1)
            self.grid.setColumnStretch(0, 1)
            self.grid.setColumnStretch(1, 4)
            self.visualizer.base_color = self.node_color_choice.currentText()
            self.visualizer.base_edge_color = self.edge_color_choice.currentText()
            starttime = timeit.default_timer()
            self.visualizer.set_graph_to_network(filename=self.result_file)
            self.visualizer.show()
            endtime = timeit.default_timer()
            print(f'Visualisation time = {endtime - starttime}ms')
            # self.clearLayout(self.parameters)
            # self.grid.removeItem(self.parameters)
        else:
            # self.visualizer = Visualizer()
            # self.visualizer.set_graph_to_network()
            '''grid.addWidget(self.visualizer, 0, 1, 4, 1)
            grid.setColumnStretch(0, 1)
            grid.setColumnStretch(1, 4)
            self.setLayout(grid)'''
            self.visualizer.base_color = self.node_color_choice.currentText()
            self.visualizer.base_edge_color = self.edge_color_choice.currentText()
            starttime = timeit.default_timer()
            self.visualizer.set_graph_to_network(filename=self.result_file)
            self.visualizer.show()
            endtime = timeit.default_timer()
            print(f'Visualisation time = {endtime - starttime} s')
        self.clearLayout(self.parameters)
        self.grid.removeItem(self.parameters)
        self.button_start.setEnabled(False)

    def fill_base_parameters(self):
        # TODO: Change it to colorPicker
        self.edge_color_choice = QComboBox(self)
        self.node_color_choice = QComboBox(self)
        self.add_parameters_button = QPushButton('Ustaw Parametry', self)
        node_color_label = QLabel('Choose Node Color:')
        colors = ['red', 'green', 'blue', 'purple', 'black', 'white']
        edge_color_label = QLabel('Choose Edge Color:')
        self.parameters.addWidget(node_color_label)
        self.node_color_choice.addItems(colors)
        self.parameters.addWidget(self.node_color_choice)

        # add edge color choice.
        self.parameters.addWidget(edge_color_label)
        self.edge_color_choice.addItems(colors)
        self.parameters.addWidget(self.edge_color_choice)
        self.parameters.addWidget(self.add_parameters_button)
        self.add_parameters_button.setEnabled(False)

    def clearLayout(self, lay):
        while lay.count():
            child = lay.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


class ListBoxWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.resize(100, 50)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    links.append(str(url.toLocalFile()))
                    # mainWindow.label_file.setText("Wybrany no: ")
                    mainWindow.filename = url.toLocalFile()
                else:
                    links.append(str(url.toString()))
            self.addItems(links)
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = App()
    mainWindow.show()
    sys.exit(app.exec_())
