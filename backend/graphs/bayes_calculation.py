"""Модуль сети Байеса."""

import json
import random
from collections import defaultdict
from itertools import product
from pathlib import Path

from django.conf import settings


PROBABILITIES_PATH = Path(settings.GRAPH_PATH) / 'probabilities_opt.json'
GRAPHS_4_PATH = Path(settings.GRAPH_PATH) / 'graphs_4.json'


class BayesianNode:
    def __init__(self, node_id, name, parents, prob_data):
        self.id = node_id
        self.name = name
        self.parents = parents
        self.prob_table = self._parse_probabilities(prob_data)

    def _parse_probabilities(self, prob_data):
        parsed = {}
        for k, v in prob_data.items():
            key = tuple(map(int, k.split(','))) if k else ()
            parsed[key] = float(v)
        return parsed

    def get_probability(self, parent_states):
        return self.prob_table.get(parent_states, 0.0)

def load_graph(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def load_probabilities(filename='probabilities.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def create_base_probabilities(graph_data, output_file='probabilities.json'):
    # Инициализация структур данных
    parent_map = defaultdict(list)
    id_to_node = {n['id']: n for n in graph_data['nodes']}
    
    # Построение карты родителей
    for link in graph_data['links']:
        parent_map[link['target']].append(link['source'])
    
    # Находим все prepare-узлы и их предков
    prepare_nodes = [n['id'] for n in graph_data['nodes'] if n.get('label') == 'prepare']
    zero_nodes = set()
    
    # Рекурсивный поиск предков
    def find_ancestors(node_id):
        ancestors = set()
        for parent in parent_map.get(node_id, []):
            ancestors.add(parent)
            ancestors.update(find_ancestors(parent))
        return ancestors
    
    # Собираем все узлы для обнуления
    for node_id in prepare_nodes:
        zero_nodes.add(node_id)
        zero_nodes.update(find_ancestors(node_id))
    
    # Генерация вероятностей
    probabilities = {}
    for node in graph_data['nodes']:
        node_id = node['id']
        parents = parent_map.get(node_id, [])
        
        # Для нулевых узлов
        if node_id in zero_nodes:
            if not parents:
                probabilities[node['name']] = {"": 0.0}
            else:
                combs = product([0], repeat=len(parents))  # Все комбинации нулей
                probabilities[node['name']] = {','.join(map(str, c)): 0.0 for c in combs}
        else:
            # Случайные вероятности для остальных
            if not parents:
                probabilities[node['name']] = {"": random.uniform(0.00001, 0.999)}
            else:
                combs = product([0, 1], repeat=len(parents))
                probabilities[node['name']] = {','.join(map(str, c)): random.uniform(0.0000001, 0.999) for c in combs}
    
    # Сохранение в файл
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(probabilities, f, indent=4, ensure_ascii=False)


# Функция создания файла доз (оригинальная, оставлена без изменений согласно заданию)
def create_doses_file(graph_data, output_file='prepare_doses.json'):
    prepare_nodes = [n['name'] for n in graph_data['nodes'] if n.get('label') == 'prepare']
    doses = {name: 0.0 for name in prepare_nodes}
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(doses, f, indent=4, ensure_ascii=False)


# Модифицированная функция загрузки и объединения данных
def load_combined_data(graph_data, prob_file='probabilities_opt.json',
                       drug_states_input=None):
    with open(prob_file, 'r', encoding='utf-8') as f:
        probabilities = json.load(f)
    
    # Создаем маппинг drug_id <-> drug_name для удобства
    drug_id_to_name = {n['id']: n['name'] for n in graph_data['nodes'] if n.get('label') == 'prepare'}
    
    # Обновляем вероятности из файла drug_states
    for drug_id, state in drug_states_input.items():
        drug_name = drug_id_to_name.get(drug_id)
        if drug_name and drug_name in probabilities:
            # Для узлов без родителей или для всех комбинаций родителей
            if "" in probabilities[drug_name]:
                probabilities[drug_name][""] = float(state)
            else:
                # Применяем состояние к каждой комбинации родителей
                # Это предполагает, что состояние (0 или 1) переписывает
                # любую условную логику для этого узла препарата.
                probabilities[drug_name] = {k: float(state) for k in probabilities[drug_name]}
    
    # Подготовка данных для вывода в файл optimized_results.json
    drugs_for_output = []
    combination_parts = []

    # Отсортируем ID препаратов, чтобы порядок в выводе был предсказуемым
    sorted_drug_ids = sorted(drug_states_input.keys(), key=lambda drug_id: drug_id_to_name.get(drug_id, ''))
    
    for drug_id in sorted_drug_ids:
        drug_name = drug_id_to_name.get(drug_id)
        state = drug_states_input.get(drug_id)
        if drug_name:
            drugs_for_output.append(drug_name)
            combination_parts.append(f"{drug_name}={state}")

    combination_description = " + ".join(combination_parts)

    return probabilities, drug_states_input, drugs_for_output, combination_description


def topological_sort(nodes, parent_map):
    visited = set()
    result = []
    stack = []
    
    for node in nodes:
        if node not in visited:
            stack.append((node, False))
            while stack:
                current, processed = stack.pop()
                if processed:
                    result.append(current)
                    continue
                if current in visited:
                    continue
                visited.add(current)
                stack.append((current, True))
                for parent in reversed(parent_map.get(current, [])):
                    if parent not in visited:
                        stack.append((parent, False))
    return result

def build_network(graph_data, prob_data):
    parent_map = defaultdict(list)
    for link in graph_data['links']:
        parent_map[link['target']].append(link['source'])

    nodes = {}
    for node in graph_data['nodes']:
        node_id = node['id']
        nodes[node_id] = BayesianNode(
            node_id=node_id,
            name=node['name'],
            parents=parent_map.get(node_id, []),
            prob_data=prob_data.get(node['name'], {})
        )
    return nodes

def calculate_probabilities(network):
    """Вычисляет априорные вероятности для всех узлов сети"""

    # 1. Создаем словарь связей "узел -> его родители"
    parent_map = {nid: node.parents for nid, node in network.items()}

    # 2. Топологическая сортировка узлов
    sorted_nodes = topological_sort(network.keys(), parent_map)

    # 3. Словарь для накопления результатов
    probabilities = {}

    # Открываем файл для записи логов
    with open('calculation_trace.txt', 'w', encoding='utf-8') as f:
        # 4. Заголовок лога
        f.write("\n" + "="*50 + "\n")
        f.write("НАЧАЛО РАСЧЕТА ВЕРОЯТНОСТЕЙ\n")
        f.write(f"Порядок обработки узлов: {sorted_nodes}\n")
        f.write("="*50 + "\n\n")

        # 5. Обработка узлов
        for node_id in sorted_nodes:
            node = network[node_id]
            f.write(f"[Узел {node_id} '{node.name}']\n")
            f.write(f"Тип: {'Корневой' if not node.parents else 'Дочерний'}\n")
            f.write(f"Родители: {node.parents or 'нет'}\n")

            if not node.parents:
                # Узел без родителей
                prob = node.get_probability(())
                probabilities[node_id] = prob
                f.write(f"Вероятность из таблицы: {prob:.4f}\n")
                f.write("-"*50 + "\n\n")
                continue

            total_conditional = sum(node.prob_table.values())
            normalized_probs = {}

            if abs(total_conditional - 1.0) > 1e-9:
                f.write(f"! Нормализация условных вероятностей (исходная сумма: {total_conditional:.4f})\n")
                for comb, p in node.prob_table.items():
                    normalized_probs[comb] = p / total_conditional if total_conditional != 0 else 0.0
            else:
                normalized_probs = node.prob_table


            # Расчет для узлов с родителями
            total = 0.0
            f.write(f"Комбинации состояний родителей ({len(normalized_probs)}):\n")

            for i, (comb, p_node) in enumerate(normalized_probs.items(), 1):
                prob_comb = 1.0
                comb_str = ",".join(map(str, comb))
                f.write(f"\nКомбинация {i}: {comb_str}\n")
                f.write(f"P({node.name}|{comb_str}) = {p_node:.4f}\n")

                for j, (parent_id, state) in enumerate(zip(node.parents, comb), 1):
                    parent_prob = probabilities.get(parent_id, 0.0)
                    parent = network[parent_id]
                    operation = "P" if state == 1 else "1-P"
                    value = parent_prob if state == 1 else (1 - parent_prob)

                    f.write(f"  Родитель {j}: {parent.name} (ID {parent_id})\n")
                    f.write(f"  Состояние: {state} → {operation}({parent_prob:.4f}) = {value:.4f}\n")

                    prob_comb *= value
                    f.write(f"  Текущая prob_comb: {prob_comb:.4f}\n")

                contribution = p_node * prob_comb   
                tr_temp = total
                total = total + contribution
                f.write(f"Вклад комбинации: {p_node:.4f} * {prob_comb:.4f} = {contribution:.4f}\n")
                f.write(f"!!!Накопление суммы влияний: {tr_temp:.4f} + {contribution:.4f} = {total:.4f}\n")
                f.write(f"Накопленный сумма (свертка): {total:.4f}\n")

            probabilities[node_id] = total
            f.write(f"\nИтоговая вероятность: {total:.4f}\n")
            f.write("="*50 + "\n\n")

    return probabilities

def get_conditional_probability(network, node_id, parent_states):
    node = network.get(node_id)
    if not node:
        raise ValueError(f"Узел {node_id} не найден")
    return node.get_probability(parent_states)


def get_result(final_probs, graph_data, drug_states_input, drugs_for_output, combination_description):
    # Создаем вспомогательный словарь для быстрого поиска узлов по ID
    id_to_node = {n['id']: n for n in graph_data['nodes']}
    
    all_side_effects_output = {}

    # Перебираем все узлы в графе, чтобы найти побочные эффекты
    # и получить их финальные вероятности из final_probs
    for node_id, prob in final_probs.items():
        node = id_to_node.get(node_id)
        # Проверяем, является ли узел побочным эффектом
        if node and node.get('label') in ['side_effect', 'side_e', 'effect']:
            side_effect_name = node['name']
            all_side_effects_output[side_effect_name] = {
                "id": node_id,
                "probability": round(float(prob), 6) # Округляем до 6 знаков после запятой
            }
    
    # Формируем финальную структуру данных по образцу optimized_results.json
    final_output_data = {
        "combination_description": combination_description,
        "drugs": drugs_for_output,
        "drug_states_input": drug_states_input,
        "side_effects": all_side_effects_output
    }
    return final_output_data

        
def save_results(final_probs, graph_data, drug_states_input, drugs_for_output, combination_description, filename="results.json"):
    # Создаем вспомогательный словарь для быстрого поиска узлов по ID
    id_to_node = {n['id']: n for n in graph_data['nodes']}
    
    all_side_effects_output = {}

    # Перебираем все узлы в графе, чтобы найти побочные эффекты
    # и получить их финальные вероятности из final_probs
    for node_id, prob in final_probs.items():
        node = id_to_node.get(node_id)
        # Проверяем, является ли узел побочным эффектом
        if node and node.get('label') in ['side_effect', 'side_e', 'effect']:
            side_effect_name = node['name']
            all_side_effects_output[side_effect_name] = {
                "id": node_id,
                "probability": round(float(prob), 6) # Округляем до 6 знаков после запятой
            }
    
    # Формируем финальную структуру данных по образцу optimized_results.json
    final_output_data = {
        "combination_description": combination_description,
        "drugs": drugs_for_output,
        "drug_states_input": drug_states_input,
        "side_effects": all_side_effects_output
    }

    # Сохраняем результат в файл
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_output_data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    # Загрузка графа
    with open('graphs_4.json') as f: # Предполагается, что это ваш файл графа
        graph = json.load(f)
    
    # Шаг 1 и 2 по созданию файлов base_probabilities и prepare_doses
    # закомментированы, так как drug_states.json и probabilities_opt.json
    # предполагаются как уже существующие входные данные.
    # create_base_probabilities(graph, output_file='probabilities_opt.json') # Если нужно сгенерировать
    # create_doses_file(graph) # Это для старого формата prepare_doses.json

    # Шаг 3: Загрузить объединенные данные с учетом drug_states.json
    prob_data, drug_states_input_data, drugs_for_output, combination_description = load_combined_data(
        graph_data=graph,
        prob_file='probabilities_opt.json',  # Теперь этот файл - источник общих вероятностей
        drug_states_file='drug_states.json' # А этот - входные состояния препаратов
    )
    
    # Построение сети с новыми параметрами
    network = build_network(graph, prob_data)
    
    # Перерасчет вероятностей (логирование не меняется)
    final_probs = calculate_probabilities(network)
    
    # Сохранение обновленных результатов в новом формате
    save_results(
        final_probs,
        graph,
        drug_states_input_data,
        drugs_for_output,
        combination_description,
        "results.json"
    )
    
    print("Расчеты успешно завершены. Результаты сохранены в results.json")
