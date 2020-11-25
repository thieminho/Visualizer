from pyvis.network import Network
import networkx as nx
from PyQt5.QtWebEngineWidgets import *


class Visualizer(QWebEngineView):

    def __init__(self, graph):
        super().__init__()
        self.graph = graph
        self.net = Network(height="100%", width="100%", notebook=False, directed=True)
        self.net.set_edge_smooth(smooth_type='dynamic')

    def set_graph_to_network(self):
        for _,_,edge_attr in self.graph.edges(data=True):
            edge_attr['value'] = edge_attr['Weight']
        self.net.from_nx(nx_graph=self.graph, default_node_size=10, default_edge_weight=1)

    def show(self) -> None:
        self.net.save_graph("visuzalized_graph.html")
        self.setHtml(self.net.html)
        super().show()
