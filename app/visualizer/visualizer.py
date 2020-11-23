from pyvis.network import Network
import networkx as nx
from PyQt5.QtWebEngineWidgets import *


class Visualizer(QWebEngineView):

    def __init__(self, graph):
        super().__init__()
        self.graph = graph
        self.net = Network(height="100%", width="100%", notebook=False)

    def set_graph_to_network(self):
        self.net.from_nx(nx_graph=self.graph)

    def show(self) -> None:
        self.net.save_graph("visuzalized_graph.html")
        self.setHtml(self.net.html)
        super().show()
