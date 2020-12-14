from pyvis.network import Network
import networkx as nx
from PyQt5.QtWebEngineWidgets import *
import pandas as pd
import fnmatch


class Visualizer(QWebEngineView):

    def __init__(self):
        super().__init__()
        #self.file_name = file_name
        self.net = Network(height="100%", width="100%", notebook=False, directed=True)
        self.net.set_edge_smooth(smooth_type='dynamic')
        self.used = False

    def __del__(self):
        print("visualizer object deleted")

    def load_tranzition_data(self, data):
        print(f'Constructing Tranzition Graph from {self.file_name}')
        acctualData = pd.DataFrame(data, columns=['type', 'id', 'from', 'to'])
        nodes = acctualData[acctualData['type'] == 'n']
        transitions = acctualData[acctualData['type'] == 't']

        for node in nodes.itertuples(name='Nodes'):
            dictNode = node._asdict()
            node_type, node_id = dictNode['type'], dictNode['id']
            self.net.add_node(node_id, shape='circular')

        for transition in transitions.itertuples(name='Transitions'):
            dictTran = transition._asdict()
            node_type, node_id, source, target = dictTran['type'], dictTran['id'], dictTran['_3'], dictTran['to']
            self.net.add_node(node_id,shape='box',label=' ')

            if pd.notnull(source):
                [self.net.add_edge(s, node_id) for s in source.split(';')]
            if pd.notnull(target):
                [self.net.add_edge(node_id, s) for s in target.split(';')]


    def load_data(self):
        print(f'Loading data from {self.file_name}')
        data = pd.read_csv(self.file_name)
        if fnmatch.fnmatch(self.file_name, '*transition*.csv'):
            self.load_tranzition_data(data=data)
        else:
            print(f'file {self.file_name} not matched regex')


    def set_graph_to_network(self, filename):
        print("setting Graph for Network")
        self.used = True
        self.file_name = filename
        self.load_data()

    def clear(self):
        self.net = None
        self.used = False

    def show(self) -> None:
        self.net.options.manipulation = True
        self.net.save_graph("visuzalized_graph.html")
        self.setHtml(self.net.html)
        super().show()