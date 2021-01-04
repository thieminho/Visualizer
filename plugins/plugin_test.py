import os

from PyQt5.QtCore import QMutex
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSlider


class Plugin:
    def __init__(self, *args, **kwargs):
        self.cognificane = 0
        self.param2 = 0
        print('Plugin init ("Alpha Miner"):', args, kwargs)

    def execute(self):
        print('Executing testing algorithm')
        return "success", "full_path"

    def fill_my_parameters(self, widget: QVBoxLayout):
        print('Adding custom params from plugin')
        self.slider = QSlider()
        widget.addWidget(self.slider)
