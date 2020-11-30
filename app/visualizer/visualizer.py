from pyvis.network import Network
import networkx as nx
from PyQt5.QtWebEngineWidgets import *
import pandas as pd

class Visualizer(QWebEngineView):

    def __init__(self, dataFrame):
        super().__init__()
        self.dataToVisualize = dataFrame
        self.net = Network(height="100%", width="100%", notebook=False, directed=True)
        self.net.set_edge_smooth(smooth_type='dynamic')

    def set_graph_to_network(self):
        print("setting Graph for Network")
        acctualData = pd.DataFrame(self.dataToVisualize,columns=['type', 'id', 'from', 'to'])
        nodes = acctualData[acctualData['type'] == 'a']
        transitions = acctualData[acctualData['type'] == 't']
        print(nodes)
        print(transitions)
        for node in nodes.itertuples(name='Nodes'):
            dictNode = node._asdict()
            node_type, node_id = dictNode['type'], dictNode['id']
            self.net.add_node(node_id, shape='circular')

        for transition in transitions.itertuples(name='Transitions'):
            dictTran = transition._asdict()
            node_type, node_id, source, target = dictTran['type'], dictTran['id'], dictTran['_3'], dictTran['to']
            self.net.add_node(node_id, shape='box', label=node_id)

            if pd.notnull(source):
                [self.net.add_edge(s, node_id) for s in source]
            if pd.notnull(target):
                [self.net.add_edge(node_id, s) for s in target]

    def show(self) -> None:
        self.net.save_graph("visuzalized_graph.html")
        self.setHtml(self.net.html)
        super().show()
