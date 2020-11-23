from pyvis.network import Network
import pandas as pd
# import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import sys
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QApplication

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
G = nx.from_pandas_edgelist(data,source='Source',target='Target', edge_attr='Weight', create_using=graph)

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

got_net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
got_net.from_nx(G)
got_net.save_graph("gameofthrones.html")

web = QWebEngineView()
web.setHtml(got_net.html)
web.show()
sys.exit(app.exec_())