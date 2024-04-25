from gensim.models import Word2Vec
import networkx as nx
import pgmpy

import json

'''
Модуль для строительства семантического графа.
Входными данными являются список ЛС (названий), список медицинских терминов
и порог семантической близости.
Названия ЛС являются первыми (отправными) вершиинами семанитческого графа,
далее иду вершины терминов, которые опрысываю свойства и хараткеристики ЛС: взаимодействия, 
побочные действия, состовные элементы и тд.
Порог позволяет оценить какие потенциальные вершины связанны между собой непосредствее, 
а какие через промежуточные вершины.  Семантическая близость вычисляется языковой моделью (в н.в Word2Vec).
В итоге результирующий графа содержит три типа вершин:
    вершины ЛС;
    вершины терминов непосредственно связанных с ЛС;
    вершины терминов связанные с ЛС через другие вершины терминов.
'''
def creating_semantic_network(essential_medicines_list, termList, threshold):
    model = None
    try:
        # загрузка языковой модели
        print('загрузка языковой модели')
        MODEL_PATH = r'D:\The job\loaderDB\loaderDB\medicalNLP\NLP_models\LM_models\model_W2V_10_10_1'
        model = Word2Vec.load(MODEL_PATH)
    except:
        print('Проблемы загрузки языковой модели!')
        print(str(Exception))
        return -1

    try:
        # строительство семантического графа
        print('строительство семантического графа')
        graph = nx.DiGraph()
        essential_medicines_set = set(essential_medicines_list).intersection(set(model.wv.key_to_index.keys()))
        print(f'len(essential_medicines_set) = {len(essential_medicines_set)}')
        terms_without_em = set(termList) - set(essential_medicines_list)
        count_em = 0
        for em in essential_medicines_set:
            if em not in model.wv.key_to_index:
                continue
            count_em += 1
            print(f'Добавлено {count_em} лекарств в семантический граф')
            graph.add_node(em)
            
            for term in terms_without_em:
                if term not in model.wv.key_to_index:
                    continue
                semanticProximity = model.wv.similarity(em, term)
                if semanticProximity >= threshold:
                    graph.add_edge(em, term)
        
        print('ЛС добавлены')
        terms_without_em = list(terms_without_em)
        terms_count = 0
        term = terms_without_em.pop()
        while term:
            if term not in model.wv.key_to_index:
                    if terms_without_em:
                        term = terms_without_em.pop()
                        continue
                    else:
                        break
            terms_count += 1
            if terms_count % 1000 == 0:
                print(f'Добавлено {terms_count} медицинских терминов в семантических граф')
            for node in list(graph.nodes):
                semanticProximity = model.wv.similarity(node, term)
                if semanticProximity >= threshold:
                    graph.add_edge(em, term)
            if not terms_without_em:
                term = None
                continue
            term = terms_without_em.pop()

        if terms_without_em:
            print(f'Осталось неиспользованных {len(terms_without_em)} медицинских терминов')
        else:
            print('Использованы все медицинские термины')

        print('семантический граф построен')

        # сохранение семантического графа
        SG_PATH = r'D:\The job\loaderDB\loaderDB\medicalNLP\NLP_models\semantic_network\semantic_graph.json'
        outfile = open(SG_PATH, 'w')
        data = nx.node_link_data(graph)
        sdata = json.dump(data, outfile)
        outfile.close()
        print('семантический граф сохранён')
    except:
        print(str(Exception))
        return -1
