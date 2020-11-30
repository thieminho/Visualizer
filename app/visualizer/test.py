from pyvis.network import Network
import pandas as pd
# import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import sys
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QApplication
from itertools import islice, repeat, chain

app = QApplication(sys.argv)

# import matplotlib.pyplot as plt
#
# K5 = nx.complete_graph(5)
# dot = nx.nx_pydot.to_pydot(K5)
# plt.plot()
# st.graphviz_chart(dot.to_string())
# plt.show()


# set the physics layout of the network
data = pd.read_csv("https://www.macalester.edu/~abeverid/data/stormofswords.csv")
graph = nx.DiGraph()
G = nx.from_pandas_edgelist(data, source='Source', target='Target', edge_attr='Weight', create_using=graph)

data1 = pd.read_csv("../../test.csv")
print(data1)
myNetwork = Network('500px', '100%', True, False, heading="Test")
data2 = pd.DataFrame(data1, columns=['type', 'id', 'from', 'to'])
print(data2)
unpacker = lambda x, y, z=None, k=None: (x, y, z, k)
nodes = data2[data2['type'] == 'a']
tranzitions = data2[data2['type'] == 't']
print(nodes)
print(tranzitions)

for node in nodes.itertuples(name='Nodes'):
    dictNode = node._asdict()
    node_type, node_id = dictNode['type'], dictNode['id']
    myNetwork.add_node(node_id,shape='circular')

for transition in tranzitions.itertuples(name='Transitions'):
    dictTran = transition._asdict()
    node_type, node_id, source, target = dictTran['type'], dictTran['id'], dictTran['_3'], dictTran['to']
    myNetwork.add_node(node_id, shape='box', label=node_id)
    if pd.notnull(source):
        [myNetwork.add_edge(s, node_id) for s in str(source)]
    if pd.notnull(target):
        [myNetwork.add_edge(node_id, s) for s in str(target)]
# for row in data2.itertuples(name='TestData'):
#     dictRow = row._asdict()
#     node_type, node_id, source, target = dictRow['type'], dictRow['id'], dictRow['_3'], dictRow['to']
#     print(f'Adding new node: {node_type} with id: {node_id}, sources {source}, destination: {target}')
#
#     if node_type == 'a':
#         # node is a node
#         myNetwork.add_node(node_id, shape='circular')
#     elif node_type == 't':
#         # node is a transition
#         myNetwork.add_node(node_id, shape='square', label=node_id)
#         if pd.notnull(source):
#             [myNetwork.add_edge(s, node_id) for s in str(source)]
#         if pd.notnull(target):
#             [myNetwork.add_edge(node_id, s) for s in str(target)]
#     else:
#         print("Bad node type")

# nx.to_directed(G)

# got_data = pd.read_csv("https://www.macalester.edu/~abeverid/data/stormofswords.csv")
#
# sources = got_data['Source']
# targets = got_data['Target']
# weights = got_data['Weight']
#
# edge_data = zip(sources, targets, weights)
#
# for e in edge_data:
#     src = e[0]
#     dst = e[1]
#     w = e[2]
#
#     got_net.add_node(src, src, title=src)
#     got_net.add_node(dst, dst, title=dst)
#     got_net.add_edge(src, dst, value=w)
#
# neighbor_map = got_net.get_adj_list()
#
# # add neighbor data to node hover data
# for node in got_net.nodes:
#     node["title"] += " Neighbors:<br>" + "<br>".join(neighbor_map[node["id"]])
#     node["value"] = len(neighbor_map[node["id"]])
# nx.draw(graph)
# plt.show()

# got_net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
# got_net.from_nx(G)
# got_net.save_graph("gameofthrones.html")
myNetwork.save_graph('test.html')
web = QWebEngineView()
web.setHtml(myNetwork.html)
web.show()
sys.exit(app.exec_())
