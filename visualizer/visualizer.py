from pyvis.network import Network
from PyQt5.QtWebEngineWidgets import *
import pandas as pd
import fnmatch


class Visualizer(QWebEngineView):

    def __init__(self):
        super().__init__()
        # self.file_name = file_name
        self.font_color = 'white'
        self.background_color = 'white'
        self.net = Network(height="100%", width="100%", heading='Visualizer', notebook=False, directed=True, font_color=self.font_color,bgcolor=self.background_color)
        self.net.set_edge_smooth(smooth_type='dynamic')

        self.base_color = 'blue'
        self.base_edge_color = 'black'
        self.used = False

    def __del__(self):
        print("visualizer object deleted")

    def load_transition_data(self, data):
        print(f'Constructing Tranzition Graph from {self.file_name}')
        acctualData = pd.DataFrame(data, columns=['type', 'id', 'from', 'to'])
        nodes = acctualData[acctualData['type'] == 'n']
        transitions = acctualData[acctualData['type'] == 'p']

        for node in nodes.itertuples(name='Nodes'):
            dictNode = node._asdict()
            node_type, node_id = dictNode['type'], dictNode['id']
            self.net.add_node(node_id, shape='box',label=node_id, color=self.base_color)

        for transition in transitions.itertuples(name='Transitions'):
            dictTran = transition._asdict()
            node_type, node_id, source, target = dictTran['type'], dictTran['id'], dictTran['_3'], dictTran['to']
            self.net.add_node(node_id, shape='circular', label=' ', color='black')

            if pd.notnull(source):
                [self.net.add_edge(s, node_id, color=self.base_edge_color) for s in source.split(';')]
            if pd.notnull(target):
                [self.net.add_edge(node_id, s,color=self.base_edge_color) for s in target.split(';')]

    def load_fuzzy_data(self, data):
        self.net = Network(height="100%", width="100%", notebook=False, directed=True, layout=True)
        print(f'Constructing Fuzzy Graph from {self.file_name}')
        acctualData = pd.DataFrame(data, columns=['type', 'id', 'significance', 'from', 'to'])
        nodes = acctualData[acctualData['type'] == 'n']
        clusters = acctualData[acctualData['type'] == 'c']
        edges = acctualData[acctualData['type'] == 'e']

        for node in nodes.itertuples(name='Nodes'):
            dictNode = node._asdict()
            node_type, node_id, significance = dictNode['type'], dictNode['id'], dictNode['significance']
            self.net.add_node(node_id, shape='circular', title=f'{significance}',color=self.base_color)

        for cluster in clusters.itertuples(name='Clusters'):
            dictClus = cluster._asdict()
            node_type, node_id, significance = dictClus['type'], dictClus['id'], dictClus['significance']
            self.net.add_node(node_id, shape='box', title=f'{significance}', color='orange')

        for edge in edges.itertuples(name='Edges'):
            dictEdge = edge._asdict()
            node_type, node_id, significance, source, target = \
                dictEdge['type'], dictEdge['id'], dictEdge['significance'], dictEdge['_4'], dictEdge['to']
            self.net.add_edge(source, target, title=f'{significance}', width=significance * 4, color=self.base_edge_color)
        self.net.options.layout.hierarchical.sortMethod = 'directed'
        self.net.toggle_physics(False)

    def load_HM_data(self, data):
        print(f'Constructing Petri Net Graph from {self.file_name}')
        acctualData = pd.DataFrame(data, columns=['type', 'id', 'from', 'to'])
        places = acctualData[acctualData['type'] == 'p']
        transitions = acctualData[acctualData['type'] == 't']
        edges = acctualData[acctualData['type'] == 'e']
        print('here')
        for place in places.itertuples(name='Places'):
            dictPlace = place._asdict()
            node_type, node_id = dictPlace['type'], dictPlace['id']
            self.net.add_node(node_id, shape='circle',label=' ', color='black')
        for transition in transitions.itertuples(name='Transitions'):
            dictTran = transition._asdict()
            node_type, node_id, source, target = dictTran['type'], dictTran['id'], dictTran['_3'], dictTran['to']
            self.net.add_node(node_id, shape='box', label=f'{node_id}', color='self.base_color')
        for edge in edges.itertuples(name='Edges'):
            dictEdge = edge._asdict()
            node_type, node_id, source, target = \
                dictEdge['type'], dictEdge['id'], dictEdge['_3'], dictEdge['to']
            self.net.add_edge(source, target, color=self.base_edge_color)

    def load_data(self):
        print(f'Loading data from {self.file_name}')
        if fnmatch.fnmatch(self.file_name, '*transition*.csv'):
            data = pd.read_csv(self.file_name)
            self.load_transition_data(data=data)
        if fnmatch.fnmatch(self.file_name, '*fuzzy*.csv'):
            data = pd.read_csv(self.file_name)
            self.load_fuzzy_data(data=data)
        if fnmatch.fnmatch(self.file_name, '*HMresult*.csv'):
            print('regex found')
            data = pd.read_csv(self.file_name, sep=';')
            print(data)
            self.load_HM_data(data=data)
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
