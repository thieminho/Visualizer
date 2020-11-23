import networkx as nx
import matplotlib.pyplot as plt


g = nx.petersen_graph()

plt.subplot(121)
nx.draw(g, with_labels=True, font_weight='bold')
plt.subplot(122)
nx.draw_shell(g, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
plt.show()
