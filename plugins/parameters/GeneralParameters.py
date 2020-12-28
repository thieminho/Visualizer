from PyQt5.QtWidgets import QVBoxLayout, QLabel, QComboBox, QWidget


class GeneralParameters(QWidget):
    node_color_label = QLabel('Choose Node Color:')
    colors = ['red', 'green', 'blue', 'purple', 'black', 'white']
    background_color_label = QLabel('Choose Background Color:')
    edge_color_label = QLabel('Choose Edge Color:')

    def __init__(self):
        super().__init__()
        self.myLayout = QVBoxLayout()
        # add node color choice.
        self.addWidget(self.node_color_label)
        self.node_color_choice = QComboBox(self)
        self.node_color_choice.addItems(self.colors)
        self.addWidget(self.node_color_choice)
        # add background color choice.
        self.addWidget(self.background_color_label)
        self.background_color_choice = QComboBox(self)
        self.background_color_choice.addItems(self.colors)
        self.addWidget(self.background_color_choice)
        # add edge color choice.
        self.addWidget(self.edge_color_label)
        self.edge_color_choice = QComboBox(self)
        self.edge_color_choice.addItems(self.colors)
        self.addWidget(self.edge_color_choice)
        self.setLayout(self.myLayout)
