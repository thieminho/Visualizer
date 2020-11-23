from pyvis.network import Network
import networkx as nx
from PyQt5.QtWebEngineWidgets import *


class Visualizer(QWebEngineView):
    graph = None

    def __init__(self, graph):
        super().__init__()
        self.graph = graph
