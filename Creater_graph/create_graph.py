import json
import time


import networkx as nx
import matplotlib.pyplot as plt

from collections import defaultdict

from split_sent_razdel import split_format_text             # Форматирование и разделение на предложения
from mark_sent_1 import mark_lines                          # Маркировка текста BIO
from highlight_words_1 import find_connections, print_list  # Определение связей

# На вход подаётся список предложений из json файла инструкции
def create_gragh_json(drug_name, text_list):

	# Форматирование и разделение на предложения
	text = '\n'.join(text_list)

	start_time = time.time()

	sents = split_format_text(text).split('\n')

	end_time = time.time()
	print_list(sents)

	# Присваивание меток BIO (можно заменить на нейронку)
	dict_words_tags = mark_lines(sents)
	
	target_drug = 'drug'

	semantic_graph = nx.DiGraph()
	semantic_graph.add_node(drug_name, 
							name=drug_name,
							positions=list(),
							tag = target_drug,
							ratio = None,
							roots = drug_name,
							instructions = list(),
							humanInformation = None
							)
	
	all_subj_connections_dict = []
	all_related_connections_dict = []
	all_predict_connections_dict = []
	all_not_connections_dict = []

	start_time_ner = 0
	end_time_ner = 0

	# Проход по каждому предложению
	for i_line, sent_words_tags in enumerate(dict_words_tags):

		start_time_ner += time.time()

		subj_connections_dict,\
		related_connections_dict,\
		predict_connections_dict,\
		not_connections_dict = find_connections(
												sent_words_tags["tokens"],
												sent_words_tags["tags"],
												line = i_line
											)
		
		end_time_ner += time.time()

		# Добавление токена как узел
		def add_token(semantic_graph, token):
			position = (drug_name, *token['pos'])
			name = token['name']

			# Поиск существующих узлов
			node = semantic_graph.nodes.get(name)
			if node:
				if position not in node['positions']:
					node['positions'].append(position)
					# print(name + ' встретилось больше 1 раза')
			else:
				semantic_graph.add_node(
					name,
					name=name,
					positions=[position],
					tag=token['tag'],
					ratio=None,
					roots=drug_name,
					instructions=None,
					humanInformation=None
				)

		# Добавление связей для каждого предложения
		semantic_graph.nodes[drug_name]['instructions'].append(sent_words_tags["tokens"])

		for subj, predict in subj_connections_dict:
			add_token(semantic_graph, subj)

		for predict, related in related_connections_dict:
			add_token(semantic_graph, related)

		for token in not_connections_dict:
			if token['tag'] == 'side_e':
				add_token(semantic_graph, token) 
				semantic_graph.add_edge(drug_name, token['name'], label = 'побочка')


		# Сбор всех соединений
		all_subj_connections_dict += subj_connections_dict
		all_related_connections_dict += related_connections_dict
		all_predict_connections_dict += predict_connections_dict
		all_not_connections_dict += not_connections_dict
	# Конец цикла

	print("Время нахождения связей и NER:", end_time_ner-start_time_ner)
	print("Среднее время нахождения связей и NER:", (end_time_ner-start_time_ner)/len(dict_words_tags))
	

	# print("Начало построения графа")
	start_time_graph = time.time()

	# Поиск независимых глаголов
	def search_main_mech():
		list_mech = [mech for mech, related in all_related_connections_dict]
		list_depend_mech = [mech_2 for mech_1, mech_2 in all_predict_connections_dict]
		list_not_depend = [mech for mech in list_mech if mech not in list_depend_mech]

		for mech, related in all_related_connections_dict:
			if mech in list_not_depend:
				semantic_graph.add_edge(drug_name,
										related['name'],
										label = mech['name'])

		return semantic_graph

	semantic_graph = search_main_mech()

	
	# Добавление связей между сущ., если один глагол зависит от другого
	# Пример: 
	# Обладая: свойством вазодилататора
	# Может снижать: сопротивление коронарных сосудов
	# Обладая: Может снижать
	# Результат: (Обладая) свойством вазодилататора -> (Может снижать) сопротивление коронарных сосудов
	def linking_noun_to_noun():
		# Словарь существительных по ключам глаголам
		verb_to_nouns = defaultdict(list)

		# Заполнение словаря
		for verb, noun in all_related_connections_dict:
			key_verb = f'{verb['name']}_{*verb['pos'],}'
			verb_to_nouns[key_verb].append(noun)
			
		# Создаем связи между зависимыми существительными
		for verb1, verb2 in all_predict_connections_dict:
			key_verb1 = f'{verb1['name']}_{*verb1['pos'],}'
			key_verb2 = f'{verb2['name']}_{*verb2['pos'],}'
			if key_verb1 in verb_to_nouns and key_verb2 in verb_to_nouns:
				nouns1 = verb_to_nouns[key_verb1]
				nouns2 = verb_to_nouns[key_verb2]

				for noun1 in nouns1:
					for noun2 in nouns2:
						semantic_graph.add_edge(noun1['name'], noun2['name'], label=verb2['name'])

		return semantic_graph

	semantic_graph = linking_noun_to_noun()


	# Связь подлежащих
	def linking_between():
		# Используем множества для хранения уникальных элементов
		edges_to_remove = set()
		edges_to_add = set()

		for subj, predict in all_subj_connections_dict:

			if subj['name'] == drug_name:
				continue

			for mech, related in all_related_connections_dict:
				if predict == mech:
					parent_nodes = list(semantic_graph.predecessors(related['name']))
					# print_list(parent_nodes, label=f"Родители {related['name']}")

					# Добавляем уникальные ребра в множества
					for node in parent_nodes:
						edges_to_remove.add((node, related['name']))
						edges_to_add.add((node, subj['name']))
						edges_to_add.add((subj['name'], related['name'], predict['name']))

		# Применяем все удаленные ребра
		for edge in edges_to_remove:
			semantic_graph.remove_edge(*edge)

		# Применяем все добавленные ребра
		for edge in edges_to_add:
			if len(edge) == 2:
				semantic_graph.add_edge(edge[0], edge[1])
			else:
				semantic_graph.add_edge(edge[0], edge[1], label = edge[2])

		return semantic_graph
	
	semantic_graph = linking_between()

	end_time_graph = time.time()
	print("Время построения графа:", end_time_graph-start_time_graph, end='\n\n')

	return semantic_graph

def creat_praph(path):
	# Открыть JSON-файл
	with open(path, 'r', encoding='utf-8') as file:
		data = json.load(file)

	drug_name = data['Название']

	text_list = []
	# Проход по ключам и значениям в JSON
	for key, value in data.items():
		# Проверяем, является ли значение списком строк
		if isinstance(value, list)\
			and all(isinstance(item, str) for item in value)\
			and key != 'Название':
			text_list.extend(value)

	start_time = time.time()
	semantic_graph = create_gragh_json(drug_name, text_list)
	end_time = time.time()
	print("Полное время алгоритма:", end_time-start_time, end='\n\n')
	
	return semantic_graph


if __name__ == "__main__":
	semantic_graph = creat_praph('full_pipeline\\amiodaron.json')

	# Позиционирование узлов
	pos = nx.spring_layout(semantic_graph)

	nx.draw(semantic_graph, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10)

	# Получение меток рёбер из атрибута 'label'
	edge_labels = nx.get_edge_attributes(semantic_graph, 'label')

	# Отображение меток рёбер
	nx.draw_networkx_edge_labels(semantic_graph, pos, edge_labels=edge_labels, font_color='red')

	# Показ графика
	plt.show()