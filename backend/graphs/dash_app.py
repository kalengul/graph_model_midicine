from django_plotly_dash import DjangoDash
from dash import html

app = DjangoDash("GraphVisualizer")

app.layout = html.Div("Привет, это тестовый Dash")




# import base64
# import io
# import json
# import math
# import requests
# from collections import defaultdict

# from django_plotly_dash import DjangoDash
# import networkx as nx
# import plotly.graph_objects as go
# from dash import (dcc, html, Input, Output, State, ctx, no_update)


# print("Загрузка GraphVisualizer")

# app = DjangoDash("GraphVisualizer")  # Имя приложения

# COLORS = {
#     'prepare': 'green',
#     'action': 'purple',
#     'metabol': 'yellow',
#     'excretion': 'violet',
#     'absorbtion': 'black',
#     'mechanism': 'blue',
#     'group': 'green',
#     'noun': 'gray',
#     'side_e': 'red'
# }
# graph = nx.DiGraph()
# pos: dict = {}


# def load_graph_from_api(graph_id):
#     url = f"http://localhost:8000/api/v1/graphs/{graph_id}/"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # вызывает исключение при ошибке HTTP
#         return response.json()       # вернёт словарь JSON с графом
#     except requests.RequestException as e:
#         print(f"Ошибка при загрузке графа: {e}")
#         return None


# def empty_figure_with_message(message='Загрузите JSON-файл с графом'):
#     return go.Figure(
#         layout=go.Layout(
#             xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
#             yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
#             annotations=[
#                 dict(
#                     text=message,
#                     xref='paper', yref='paper',
#                     showarrow=False,
#                     font=dict(size=20),
#                     x=0.5, y=0.5,
#                     align='center'
#                 )
#             ]
#         )
#     )


# def build_figure(highlight_paths=None):
#     edge_x, edge_y = [], []
#     node_x, node_y = [], []
#     node_text, node_color, node_opacity = [], [], []

#     highlight_nodes = set()
#     highlight_edges = set()

#     # Определим рёбра на пути
#     if highlight_paths:
#         for path in highlight_paths:
#             highlight_nodes.update(path)
#             # highlight_edges.update((path[i], path[i+1])
#             #                        for i in range(len(path)-1))
#             for i in range(len(path) - 1):
#                 src, tgt = path[i], path[i + 1]
#                 if graph.has_edge(src, tgt):
#                     highlight_edges.add((src, tgt))
#                 elif graph.has_edge(tgt, src):
#                     highlight_edges.add((tgt, src))

#     # Рёбра
#     for src, tgt in graph.edges():
#         x0, y0 = pos[src]
#         x1, y1 = pos[tgt]
#         edge_x += [x0, x1, None]
#         edge_y += [y0, y1, None]

#     edge_trace = go.Scatter(
#         x=edge_x, y=edge_y,
#         line=dict(width=1, color='lightgray'),
#         hoverinfo='none',
#         mode='lines',
#         opacity=0.3 if highlight_nodes else 1
#     )

#     edge_highlight = []
#     annotations = []
#     if highlight_edges:
#         for src, tgt in highlight_edges:
#             x0, y0 = pos[src]
#             x1, y1 = pos[tgt]

#             # Вычисляем сокращение линии, чтобы стрелка не перекрывала узел
#             dx = x1 - x0
#             dy = y1 - y0
#             dist = math.hypot(dx, dy)
#             shrink = 15
#             if dist != 0:
#                 x1_adj = x1 - dx / dist * shrink
#                 y1_adj = y1 - dy / dist * shrink
#             else:
#                 x1_adj, y1_adj = x1, y1

#             # Линия рёбра
#             edge_highlight.append(go.Scatter(
#                 x=[x0, x1_adj],
#                 y=[y0, y1_adj],
#                 line=dict(width=2, color='black'),
#                 mode='lines',
#                 hoverinfo='none',
#                 opacity=1,
#                 showlegend=False
#             ))

#             annotations.append(dict(
#                 x=x1_adj,
#                 y=y1_adj,
#                 ax=x0,
#                 ay=y0,
#                 xref='x',
#                 yref='y',
#                 axref='x',
#                 ayref='y',
#                 showarrow=True,
#                 arrowhead=3,   # Стиль стрелки
#                 arrowsize=1.5,
#                 arrowwidth=1.5,
#                 arrowcolor='black',
#                 opacity=1
#             ))

#     for node in graph.nodes():
#         x, y = pos[node]
#         name = graph.nodes[node].get('name', '')
#         label = graph.nodes[node].get('label', '')
#         color = COLORS.get(label, 'lightgray')

#         is_highlighted = not highlight_nodes or node in highlight_nodes
#         opacity = 1.0 if is_highlighted else 0.1

#         node_x.append(x)
#         node_y.append(y)
#         node_color.append(color)
#         node_text.append(name)
#         node_opacity.append(opacity)

#     node_trace = go.Scatter(
#         x=node_x,
#         y=node_y,
#         mode='markers',
#         hoverinfo='text',
#         text=node_text,
#         marker=dict(
#             color=node_color,
#             size=20,
#             line_width=2,
#             opacity=node_opacity
#         )
#     )

#     data = [edge_trace] + edge_highlight + [node_trace]

#     fig = go.Figure(
#         data=data,
#         layout=go.Layout(
#             showlegend=False,
#             hovermode='closest',
#             margin=dict(b=20, l=5, r=5, t=40),
#             xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
#             yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
#             annotations=annotations
#         )
#     )
#     return fig


# def find_path_from_roots(start_node):
#     roots = [n for n in graph.nodes if graph.in_degree(n) == 0]
#     reverse_g = graph.reverse()

#     all_paths = []
#     for root in roots:
#         try:
#             paths = nx.shortest_simple_paths(reverse_g, start_node, root)
#             for path in paths:
#                 all_paths.append(path)
#         except nx.NetworkXNoPath:
#             continue
#     return all_paths


# def find_paths_to_descendants(start_node, max_depth=10):
#     paths = []

#     def dfs(node, path, depth):
#         if depth > max_depth:
#             return
#         neighbors = list(graph.successors(node))
#         for neighbor in neighbors:
#             if neighbor not in path:
#                 new_path = path + [neighbor]
#                 paths.append(new_path)
#                 dfs(neighbor, new_path, depth+1)

#     dfs(start_node, [start_node], 0)
#     return paths


# def layered_pos(graph, y_gap=200, x_gap=100):
#     level_nodes = defaultdict(list)
#     for node, attr in graph.nodes(data=True):
#         level = attr.get('level', 0)
#         level_nodes[level].append(node)

#     pos = {}
#     for level in sorted(level_nodes):
#         nodes = level_nodes[level]
#         count = len(nodes)
#         for i, node in enumerate(nodes):
#             x = i * x_gap - (count - 1) * x_gap / 2
#             y = -level * y_gap
#             pos[node] = (x, y)
#     return pos


# def process_and_draw(data):
#     global graph, pos

#     graph.clear()
#     for node in data['nodes']:
#         graph.add_node(node['id'],
#                        name=node.get('name'),
#                        label=node.get('label', ''),
#                        level=node.get('level', 1))
#     for link in data['links']:
#         if link['source'] in graph.nodes and link['target'] in graph.nodes:
#             graph.add_edge(link['source'], link['target'])
#         else:
#             print(f'Пропущено ребро: {link}')
#     pos = layered_pos(graph)
#     return build_figure()


# # app = Dash(__name__)

# app.layout = html.Div([
#     dcc.Input(
#         id='search-input',
#         type='text',
#         placeholder='Введите навазние вершины',
#         debounce=True,
#         style={'width': '100%', 'padding': '10px', 'fontSize': '16px'}
#     ),
#     html.Div(id='error-message', style={
#         'color': 'red',
#         'fontWeight': 'bold',
#         'textAlign': 'center',
#         'marginBottom': '10px'
#     }),
#     dcc.Dropdown(
#         id='graph-selector',
#         options=[],  # сюда потом подгрузишь список графов через API
#         placeholder="Выберите граф из базы",
#         style={'width': '100%', 'margin': '10px'}
#     ),
#     dcc.Loading(dcc.Graph(id='graph', figure=empty_figure_with_message()),
#                 type='circle'),
#     dcc.Store(id='selected-node'),
#     dcc.Store(id='esc-pressed', data=False),
#     dcc.Interval(id='interval-esc', interval=500, n_intervals=0),
# ])

# app.clientside_callback(
#     """
#     function(n_intervals) {
#         if (!window.escapeListenerAdded) {
#             window.escapeListenerAdded = true;
#             window.escPressed = false;
#             document.addEventListener('keydown', function(e) {
#                 if (e.key === 'Escape') {
#                     window.escPressed = true;
#                 }
#             });
#         }

#         if (window.escPressed) {
#             window.escPressed = false;
#             return true;
#         }

#         return window.dash_clientside.no_update;
#     }
#     """,
#     [Output('esc-pressed', 'data')],
#     [Input('interval-esc', 'n_intervals')]
# )


# @app.callback(
#     Output('graph-selector', 'options'),
#     Input('graph-selector', 'value')  # срабатывает один раз при загрузке
# )
# def load_graph_list(_):
#     try:
#         response = requests.get("http://localhost:8000/api/v1/graphs/")
#         response.raise_for_status()
#         graphs = response.json()
#         return [{'label': g['name'], 'value': g['id']} for g in graphs]
#     except requests.RequestException:
#         return []



# @app.callback(
#     Output('graph', 'figure'),
#     Output('selected-node', 'data'),
#     Output('error-message', 'children'),
#     Input('search-input', 'value'),
#     Input('graph-selector', 'value'),
#     Input('graph', 'clickData'),
#     Input('esc-pressed', 'data'),
#     State('selected-node', 'data'),
#     prevent_initial_call=True,
# )
# def render_graph(search_value, selected_graph_id, clickData, esc_pressed,
#                  selected_node):
#     """Функция отрисовки графа."""
#     trigger = ctx.triggered_id or 'initial'

#     if trigger == 'esc-pressed' and esc_pressed:
#         return build_figure(), None, ''
#     elif trigger == 'graph-selector' and selected_graph_id:
#         data = load_graph_from_api(selected_graph_id)
#         if data:
#             return process_and_draw(data), None, ''
#         return empty_figure_with_message("Ошибка загрузки графа"), None, ''
#     elif trigger == 'search-input' and search_value:
#         for node, attr in graph.nodes(data=True):
#             if attr.get('name', '').lower() == search_value.lower():
#                 paths = (find_path_from_roots(node) +
#                          find_paths_to_descendants(node))
#                 return build_figure(paths), node, ''

#         return build_figure(), None, (f'Вершина "{search_value}" '
#                                       'не найдена в графе.')
#     elif trigger == 'graph' and clickData:
#         point = clickData['points'][0]
#         x = point['x']
#         y = point['y']

#         for node, (x_node, y_node) in pos.items():
#             if math.hypot(x - x_node, y - y_node) < 15:
#                 if abs(x - x_node) < 10 and abs(y - y_node) < 10:
#                     if node == selected_node:
#                         return build_figure(), None, ''

#                     paths = (find_path_from_roots(node) +
#                              find_paths_to_descendants(node))
#                     return build_figure(paths), node, ''

#     return no_update
