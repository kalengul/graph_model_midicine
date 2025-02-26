import networkx as nx
from pyvis.network import Network
from IPython.core.display import display, HTML

nx_graph = nx.cycle_graph(10)
nx_graph.nodes[1]['title'] = 'Number 1'
nx_graph.nodes[1]['group'] = 1
nx_graph.nodes[3]['title'] = 'I belong to a different group!'
nx_graph.nodes[3]['group'] = 10
nx_graph.add_node(20, size=20, title='couple', group=2)
nx_graph.add_node(21, size=15, title='couple', group=2)
nx_graph.add_edge(20, 21, weight=5)
nx_graph.add_node(25, size=25, label='lonely', title='lonely node', group=3)
nt = Network('500px', '500px', notebook = True, cdn_resources = 'in_line')
# populates the nodes and edges data structures
nt.from_nx(nx_graph)
nt.show('nx.html')
display(HTML('nx.html'))