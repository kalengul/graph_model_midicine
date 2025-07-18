
from spacy_load import spacy_pipeline
from print_list import print_list
import time

# Определяет диапазоны последовательностей BIO и соответствующие токены
def get_ner_tokens(tokens, tags):
	ranges = []
	start = None
	current_tag = None

	print("sent:")
	print(tokens)
	print(tags)

	for i, (token, tag) in enumerate(zip(tokens, tags)):
		if tag.startswith("B-"):
			if start is not None:
				ranges.append(((start, i - 1), tokens[start:i], current_tag))
			start = i
			current_tag = tag.split('-')[-1]
		elif tag.startswith("I-") and start is not None:
			continue
		elif tag.startswith("O") and start is not None:
			ranges.append(((start, i - 1), tokens[start:i], current_tag))
			start = None
			current_tag = None

	if start is not None:
		ranges.append(((start, len(tags) - 1), tokens[start:], current_tag))
	
	return ranges


# Поиск связей с механизмом
def find_mechanism_connections(doc, ner_tokens):

	# Списки
	subj_connections = []
	related_connections = []
	predict_connections = []

	# Создание словаря для быстрого доступа к токенам по диапазонам
	bio_sequences_dict = { (position[0], position[1]): (tokens, label) for position, tokens, label in ner_tokens}

	# По индексу определяет словосочетания 
	def find_tokens_in_range(index, sequences_dict):
		for start, end in sequences_dict.keys():
			if start <= index <= end:
				tokens, label = sequences_dict[(start, end)]
				return ((start, end), tokens, label)
		return None

	# Нахождение все токены с меткой 'mechanism'
	mechanism_tokens = [token for token in doc if token._.custom_tag in {"B-mechanism", "I-mechanism"}]

	for mechanism in mechanism_tokens:
		mechanism_data = find_tokens_in_range(mechanism.i, bio_sequences_dict)

		# Однородные к механизму
		conj_mechanisms = [find_tokens_in_range(token.i, bio_sequences_dict) for token in doc if token.dep_ == "conj" and token.head == mechanism]
		# print(mechanism, conj_mech)

		if not mechanism_data:
			continue
		
		# Определение допустимых тегов
		NOT_MECH_TAGS = {"B-side_e", "I-side_e", "B-noun", "I-noun", "B-prepar", "I-prepar", "B-abbr", "I-abbr", "B-sym", "I-sym"}
		MECH_TAGS = {"B-mechanism", "I-mechanism"}

		# Функция проверки наличия тега в списке допустимых
		def has_valid_tag(token, not_mech = True):
			if not_mech:
				return token._.custom_tag in NOT_MECH_TAGS
			else:
				return token._.custom_tag in MECH_TAGS

		# Функция для создания списка токенов и их индексов
		def get_conj_tokens(doc, filter_func):
			return [(token, token.i)
		   			for token in doc
					for base_token, _ in filter_func
					if 	token.dep_ == "conj"
					and token.head == base_token]
	
		# Функция нахождения зависимостей подлежащего и сказуемого
		def is_subj_token(token, mechanism):
			return (
					has_valid_tag(token)
				and token.head == mechanism
				and (   token.dep_ == "nsubj"
					 or token.dep_ == "nsubj:pass")  # Проверка на подлежащее
				and token.i < mechanism.i
			)
					
		# Функция нахождения зависимостей у глагола
		def is_related_token(token, mechanism):
			return (
					has_valid_tag(token)
				and token.head == mechanism
				and token.dep_ != "advcl"
				and not ((  token.dep_ == "nsubj"
						or  token.dep_ == "nsubj:pass")
					and token.i < mechanism.i
				)
			)
				
		# Функция нахождения глаголов, зависимых от глагола
		def is_predict_token(token, mechanism):
			return  (
					has_valid_tag(token, not_mech = False)
				and token.head == mechanism
				and (token.dep_ == "obl" or token.dep_ == "advcl")
			)

		# Основная обработка
		subj_tokens = [(token, token.i) for token in doc
										if is_subj_token(token,
														 mechanism)]
		related_tokens = [(token, token.i)  for token in doc
											if is_related_token(token,
																mechanism)]
		predict_tokens = [(token, token.i)  for token in doc
											if is_predict_token(token,
																mechanism)]
		
		
		
		# Конъюнктные токены
		conj_subj_tokens = get_conj_tokens(doc, subj_tokens)
		conj_related_tokens = get_conj_tokens(doc, related_tokens)
		conj_predict_tokens = get_conj_tokens(doc, predict_tokens)

		# Объединение с conj-связанными токенами
		all_subj_tokens = subj_tokens + conj_subj_tokens
		all_related_tokens = related_tokens + conj_related_tokens
		all_predict_tokens = predict_tokens + conj_predict_tokens

		print_list(all_subj_tokens, "subj_tokens")
		print_list(all_related_tokens, "related_tokens")
		print_list(all_predict_tokens, "predict_tokens")

		def make_connect(tokens, bio_sequences_dict, mechanism_data, swap = False):
			connections = []
			
			for _, token_index in tokens:
				token_data = find_tokens_in_range(token_index,
												  bio_sequences_dict)
				
				if token_data and mechanism_data:
					connection = (token_data, mechanism_data) if swap\
									else (mechanism_data, token_data)
					connections.append(connection)

			return connections
					
		
		# Поиск серий для всех токенов подлежащих
		if all_subj_tokens:
			subj_connections += make_connect(all_subj_tokens,
											 bio_sequences_dict,
											 mechanism_data,
											 swap = True)

			for conj_mech in conj_mechanisms:
				subj_connections += make_connect(all_subj_tokens,
												 bio_sequences_dict,
												 conj_mech,
												 swap = True)

		# Поиск серий для всех связанных токенов
		if all_related_tokens:
			related_connections += make_connect(all_related_tokens,
												bio_sequences_dict,
												mechanism_data)

			# Исключить связи, если они есть в подлежащем и сказуемом
			related_connections = [(mech, token)    for mech, token
													in related_connections
													if (token, mech)
													not in subj_connections]
			
		# Поиск серий для всех предсказательных токенов
		if all_predict_tokens:
			predict_connections += make_connect(all_predict_tokens,
												bio_sequences_dict,
												mechanism_data,
												swap = True)
			
	# print_list(subj_connections, label= 'Подлежащее и сказуемое')
	# print_list(related_connections, label= 'Зависимые от глагола')
	# print_list(predict_connections, label= 'Глаголы, которые зависят от глагола')
		
	return subj_connections, related_connections, predict_connections

# Определение не связанных слов
def find_not_connections(ner_tokens, connections):
	
	# Извлечение связанных слов с механизмом и механизмов
	connect_tokens =  [connection[0] for connection in connections]
	connect_tokens += [connection[1] for connection in connections]
			
	# Формируем результат: все элементы, которые не входят в exclude_indices
	not_connect_tokens = [item for item in ner_tokens if item not in connect_tokens]

	return not_connect_tokens

def find_connections(tokens, tags, line = None):

	# Создание текста для анализа
	text = " ".join(tokens)
	doc = spacy_pipeline(text)

	# Привязка кастомных тегов к токенам в doc
	for token, tag in zip(doc, tags):
		token.set_extension("custom_tag", default=False, force=True)
		token._.custom_tag = tag
		# print(token, tag)

	# Определение диапазонов для BIO последовательностей
	ner_tokens = get_ner_tokens(tokens, tags)

	# Поиск связей и вывод BIO последовательностей
	subj_connections, related_connections, predict_connections = find_mechanism_connections(doc, ner_tokens)

	# Исключение не связанных словосочетаний
	not_connections = find_not_connections(ner_tokens, subj_connections + related_connections + predict_connections)

	print_list(ner_tokens, label = "Исходный список NER")

	print_list(subj_connections, label= 'Подлежащее и сказуемое')
	print_list(related_connections, label= 'Слова зависимые от глагола')
	print_list(predict_connections, label= 'Глаголы зависимые от глагола')


	def transform_2_dict(item, line = line):
			return {
				'pos': (line, *item[0]),
				'name': ' '.join(item[1]),
				'tag': item[2]
			}
	
	subj_connections_dict = [   (transform_2_dict(connection_1),
								transform_2_dict(connection_2))
								for connection_1, connection_2 in subj_connections]
	
	related_connections_dict = [(transform_2_dict(connection_1),
								transform_2_dict(connection_2))
								for connection_1, connection_2 in related_connections]

	predict_connections_dict = [(transform_2_dict(connection_1),
								transform_2_dict(connection_2))
								for connection_1, connection_2 in predict_connections]
	
	not_connections_dict = [transform_2_dict(not_connection)
							for not_connection in not_connections]
	
	# print_list(subj_connections_dict, label= 'Подлежащее и сказуемое')
	# print_list(related_connections_dict, label= 'Слова зависимые от глагола')
	# print_list(predict_connections_dict, label= 'Глаголы зависимые от глагола')

	# print_list(not_connections, label = "Не связанные токены")

	return subj_connections_dict, related_connections_dict, predict_connections_dict, not_connections_dict
