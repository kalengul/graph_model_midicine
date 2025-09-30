import json
import io
import zipfile
import traceback
import logging
from pathlib import Path

import networkx as nx
from rest_framework.views import APIView
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings

from drugs.utils.custom_response import CustomResponse
from graphs.serializers import (GraphSerializer, UpdateGraphSerializer,
                                BayesSerializer)
from graphs.models import Graph
from graphs.utils.cleaner_graph_db import CleanProcessor
from graphs.utils.graph_loader import JSONGraphLoader
from graphs.utils.graph_manipulator import GraphManipulator
from graphs.utils.binarizer import Binarizer
from graphs.utils.merger import Merger
from graphs.utils.parse_ids import parse_ids
from graphs.bayes_calculation import (load_combined_data, get_result,
                                      build_network, calculate_probabilities,
                                      GRAPHS_4_PATH, PROBABILITIES_PATH)
from drugs.models import Drug
from graphs.utils.load_gender_side_effect import GENDER_SIDE_EFFECT
from graphs.utils.graph_storage import GraphStorage
from graphs.utils.text_builder import TextBuilder
from graphs.utils.removing_direct_side_effect_nodes import (
    remove_direct_side_effect_nodes)
from graphs.utils.graph_optimization.lineman import Lineman
from graphs.utils.graph_optimization.deleter_non_relative_nodes import (
    SmartNonRelativeNodesDeleter,
    SimpleNonRelativeNodesDeleter)
from graphs.utils.parser import GraphParser


logger = logging.getLogger('graphs')
INCORRECT_DATA = 'Некорректные данные'
NAME = 'name'
MULTI_GRAPH_PATH = Path(settings.GRAPH_PATH) / 'multigraph.json'
GRAPH_FOR_BAYES_PATH = Path(settings.GRAPH_PATH) / 'node_with_roots.json'
UNNECESSARY = ['directed', 'multigraph', 'graph']


class GraphView(APIView):
    """Вью для графов."""

    GRAPH_JSON = 'graph_json'
    GRAPH_XML = 'graph_xml'

    REMOVING = ("directed", "multigraph", "graph")
    ERROR_COMPATIBILITY = 'Ошибка определения совместимости'

    def _get_multigraph(self):
        """Получение мультиграфа."""
        with open(MULTI_GRAPH_PATH, 'r', encoding='utf-8') as f:
            json_graph = json.load(f)
        return nx.node_link_graph(json_graph)

    def _get_subgraph(self, drug_name):
        """Получение подграфа для отдельного ЛС."""
        graph = self._get_multigraph()
        drug_node = None
        for node_id, node_data in graph.nodes(data=True):
            if node_data.get('name') == drug_name:
                drug_node = node_id
                break
        if drug_node is None:
            raise ValueError(f"Вершина с именем '{drug_name}' не найдена")

        all_descendants = nx.descendants(graph, drug_node)

        subgraph_nodes = {drug_node} | all_descendants
        subgraph = graph.subgraph(subgraph_nodes)

        return subgraph

    # def _calculate_max_level(self, graph):
    #     """Вычисляет максимальный уровень из всех вершин графа."""
    #     roots = [node for node in graph.nodes() if graph.in_degree(node) == 0]

    #     if not roots:
    #         min_level = float('inf')
    #         for node, data in graph.nodes(data=True):
    #             level = data.get('level', float('inf'))
    #             if level < min_level:
    #                 min_level = level
    #         roots = [node for node, data in graph.nodes(data=True)
    #                  if data.get('level', -1) == min_level]

    #     max_height = 0
    #     for root in roots:
    #         if root in graph:
    #             try

    def _combine_subgraphs(self, subgraphs):
        """Объединение подграфов отдлеьных ЛС в единый подграф нескольких ЛС."""
        if not subgraphs:
            return nx.DiGraph()

        combined_graph = subgraphs[0].copy()
        combined_graph.graph[NAME] = [subgraphs[0].graph[NAME]]
        combined_graph.graph['maxLevel'] = 0

        for i in range(1, len(subgraphs)):
            current_subgraph = subgraphs[i]

            for node, node_data in current_subgraph.nodes(data=True):
                if not combined_graph.has_node(node):
                    combined_graph.add_node(node, **node_data)
            for u, v, edge_data in current_subgraph.edges(data=True):
                if not combined_graph.has_edge(u, v):
                    combined_graph.add_edge(u, v, **edge_data)

            combined_graph.graph[NAME].append(current_subgraph.graph[NAME])

        return combined_graph

    def _remove_key_value(self, data):
        """Удаление ненужных пар по ключу."""
        return {k: v for k, v in data.items() if k not in self.REMOVING}

    def _get_graph_from_file(self, request):
        """
        Получение файл из запроса.

        Достаёт файл из запроса и возвращает dict-граф
        или CustomResponse.
        """
        file = request.FILES.get('file')
        file2 = request.FILES.get('file2')

        if not file:
            return None, CustomResponse(
                http_status=status.HTTP_400_BAD_REQUEST,
                message='JSON-файл не передан',
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not file2:
            return None, CustomResponse(
                http_status=status.HTTP_400_BAD_REQUEST,
                message='XML-файл не передан',
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            graph_json = json.load(file)
            graph_xml = file2.read().decode('utf-8')
        except json.JSONDecodeError:
            return None, CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                http_status=status.HTTP_400_BAD_REQUEST,
                message="Ошибка чтения JSON-файла."
            )

        return graph_json, graph_xml, None

    def _parse_ids(self, ids):
        """Парсинг списка id."""
        parsed_ids = []
        for id in ids:
            parsed_id = id.replace('[', '').replace(']', '').split(', ')
            for item in parsed_id:
                parsed_id = int(item)
                parsed_ids.append(item)
        return parsed_ids

    def remove_unnecessary_keys_and_values(self, graph):
        """Удаление ненужный клчей и значкний из словаря графа."""
        for key in UNNECESSARY:
            graph.pop(key)
        return graph

    def post(self, request):
        """Добавление графа."""
        graph_json, graph_xml, error = self._get_graph_from_file(request)

        if error:
            return error

        graph_serializer = GraphSerializer(data={
            NAME: '+'.join(graph_json[NAME]),
            self.GRAPH_JSON: graph_json,
            self.GRAPH_XML: graph_xml
        })
        if graph_serializer.is_valid():
            graph_serializer.save()
            return CustomResponse(
                status=status.HTTP_201_CREATED,
                http_status=status.HTTP_201_CREATED,
                message='Граф добавлен в БД успешно.'
            )
        else:
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                http_status=status.HTTP_400_BAD_REQUEST,
                message=(f'{INCORRECT_DATA}. Убедитесь что у него есть поля '
                         f'name, nodes, links. {graph_serializer.errors}')
            )

    def get(self, request, id=None):
        """Получнение графа по id или список."""
        try:
            ids = id or request.query_params.getlist('id')
            ids = self._parse_ids(ids)
        except Exception as error:
            message = 'Не передан id'
            logger.error(f'{message}. Ошибка {error}')
            return CustomResponse(
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=self.ERROR_COMPATIBILITY
            )
        if ids:
            drugs = []
            graph_storage = GraphStorage()
            try:
                for id in ids:
                    drug = Drug.objects.get(id=id)
                    drugs.append(drug.drug_name.lower())
                    if not drug:
                        return CustomResponse(
                            http_status=status.HTTP_404_NOT_FOUND,
                            status=status.HTTP_404_NOT_FOUND,
                            message='ЛС не найдено'
                        )
                with open(graph_storage.graph_path, 'r', encoding='utf-8') as f:
                    graph = json.load(f)

                with open(GRAPH_FOR_BAYES_PATH, 'r', encoding='utf-8') as f:
                    most_relative_nodes = json.load(f)

                print('drugs =', drugs)

                graph = SmartNonRelativeNodesDeleter().delete_nodes(
                    nx.node_link_graph(graph, edges='links'),
                    most_relative_nodes=most_relative_nodes,
                    roots=[node['id'] for node in graph['nodes']
                           if node['name'] in drugs])

                json_graph = nx.node_link_data(graph, edges='links')
                json_graph = GraphParser().jsonPolina(json_graph)
                json_graph['name'] = drugs
                json_graph = self.remove_unnecessary_keys_and_values(
                    json_graph)
                return CustomResponse(
                    http_status=status.HTTP_200_OK,
                    status=status.HTTP_200_OK,
                    message='Граф для лекарственных средств получения',
                    data=json_graph
                )
            except Exception as error:
                logger.error(f"Ошибка получения графа ЛС {error}")
                return CustomResponse(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Общий граф отстутсвует"
                )
        else:
            return CustomResponse(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=self.ERROR_COMPATIBILITY
            )

    def put(self, request, id):
        """Изменение графа."""
        instance = get_object_or_404(Graph, pk=id)

        graph_json, graph_xml, error = self._get_graph_from_file(request)

        if error:
            return error

        graph_serializer = UpdateGraphSerializer(
            instance,
            data={self.GRAPH_JSON: graph_json,
                  self.GRAPH_XML: graph_xml})
        if graph_serializer.is_valid():
            graph_serializer.save()
            return CustomResponse(
                http_status=status.HTTP_200_OK,
                message='Граф успешно обновлён',
                status=status.HTTP_200_OK
            )
        return CustomResponse(
            http_status=status.HTTP_400_BAD_REQUEST,
            message=INCORRECT_DATA,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, id):
        """Удаление графа."""
        if id:
            try:
                graph = Graph.objects.get(id=id)
                name = graph.name
                graph.delete()
                return CustomResponse(
                    status=status.HTTP_200_OK,
                    message=f"Графа {name} успешно удалён",
                    http_status=status.HTTP_200_OK
                )
            except ObjectDoesNotExist:
                return CustomResponse(
                    status=status.HTTP_404_NOT_FOUND,
                    message="Графа отсутствует",
                    http_status=status.HTTP_404_NOT_FOUND
                )
            except Exception as error:
                return CustomResponse(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=f"Внутренная ошибка сервера. {error}",
                    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


class LoadGraphView(APIView):
    """Вью для загрузки данных в БД."""

    def post(self, request):
        """Загрузка графов в БД."""
        try:
            GraphManipulator(CleanProcessor().get_cleaner(),
                             JSONGraphLoader()).perform()

            return CustomResponse(
                message="Графы успешно загружены в БД",
                status=status.HTTP_200_OK,
                http_status=status.HTTP_200_OK)
        except Exception as error:
            return CustomResponse(
                message=(
                    "Ошибка загрузки графов в БД"
                    f"Ошибка: {error}"
                ),
                status=status.HTTP_200_OK,
                http_status=status.HTTP_200_OK)


class MergeView(APIView):
    """Вьюшка слияния."""

    @parse_ids
    def get(self, request, ids, *args, **kwargs):
        """Слияние графов."""
        try:
            merged_graph = Merger().merge(ids)
            return CustomResponse(
                status=status.HTTP_200_OK,
                http_status=status.HTTP_200_OK,
                message='графы слиты успешно',
                data=merged_graph
            )
        except Exception as error:
            print(f'При слиянии графа произошла ошибка. Ошибка {error}')
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='При слиянии графа произошла ошибка'
            )


class BayeseView(APIView):
    """Вьюшка для бинарного словаря идентификаторов."""

    MAN = 'man'
    WOMAN = 'woman'
    GENDER = 'gender'
    SIDE_EFFECT = 'side_effects'
    EFFECT_NAME = "se_name"

    def _exist_contraindications(self, drug_ids, contra_ids):
        """
        Проверка наличия противопаказаний.

        Проверка пересечения противопоказаний у ЛС из комбинации
        и противопоказаний, указаных в запросе.
        """
        exist = False
        submessages = []

        drugs = Drug.objects.filter(id__in=drug_ids).prefetch_related(
            "contraindications")
        for drug in drugs:
            intersect = drug.contraindications.filter(id__in=contra_ids)
            logger.debug(f'drug = {drug.drug_name}')
            for contra in drug.contraindications.all():
                logger.debug(f'contra - {contra.id}, {contra.name}')
            if intersect.exists():
                logger.debug('Противопоказание у ЛС есть')
                names = ", ".join(list(intersect.values_list("name",
                                                             flat=True)))
                submessages.append(f'{drug.drug_name}: {names}')
                exist = True

        if submessages:
            *rest, last = submessages
            message = ';\n'.join(rest + [last + '.'])
        else:
            message = None

        return exist, message

    def _exclude_by_gender(self, source_effect, gender, gender_effects):
        """
        Исключение по полу.

        Если gender - man, недопускаются женские ПД,
        и наоборот, если woman, мужские ПД.
        """
        if gender == self.MAN:
            excluded = gender_effects[self.WOMAN]
        else:
            excluded = gender_effects[self.MAN]

        result = []
        for effect in source_effect:
            effect_name = TextBuilder(effect[self.EFFECT_NAME]).lower().text
            logger.debug(f'effect_name = {effect_name}')
            match_found = False
            for exc in excluded:
                exc = TextBuilder(exc).lower().text
                if exc in effect_name or effect_name in exc:
                    logger.debug(f'{effect_name} - половое ПД')
                    match_found = True
                    break

            if not match_found:
                logger.debug(f'{effect_name} - не половое ПД. Добавление')
                result.append(effect)

        return result

    def _get_bin_ids(self, drugs):
        """Получение бинаризированного словаря."""
        graph = GraphStorage().download_graph()
        bin_id = {}
        drug2id = {}

        for node in graph['nodes']:
            if node['label'] != 'prepare':
                continue
            drug2id[node[NAME]] = node['id']
            bin_id[node['id']] = 0

        for drug in drugs:
            bin_id[drug2id[drug.lower()]] = 1
        return bin_id

    @parse_ids
    def get(self, request, ids, *args, **kwargs):
        """Получение бинарного словаря идентификаторов."""
        bin_ids = Binarizer().binarize(ids)

        return CustomResponse(
            status=status.HTTP_200_OK,
            http_status=status.HTTP_200_OK,
            message='Бинарный словарь id-ов сформировался успешно',
            data=bin_ids)

    def post(self, request):
        """Вычисление сети Байеса."""
        graph_storage = GraphStorage()
        serializer = BayesSerializer(data=request.data)
        message = 'Некорректные данные'
        logger.info(f'message = {message}')
        if not serializer.is_valid():
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                http_status=status.HTTP_400_BAD_REQUEST,
                message=message
            )

        drug_ids = serializer.validated_data['drugs']

        human_data = serializer.validated_data.get('humanData')

        exist = False
        description = None
        gender = None
        сompatibility_bayes = 'unknown'
        contraindication_ids = []
        if human_data:
            age = human_data.get("age")
            gender = human_data.get('gender')
            contraindication_ids = human_data.get('cont_list', [])
        if contraindication_ids:
            exist, description = (
                self._exist_contraindications(drug_ids, contraindication_ids))
        if exist:
            logger.debug('Есть найдено противопоказание')
            сompatibility_bayes = 'banned-contraindications'

        drugs = []
        for id in drug_ids:
            drug = Drug.objects.get(id=id)
            if not drug:
                logger.debug(f'ЛС с id {id} нет в БД')
                continue
            drugs.append(drug.drug_name.lower())

        with open(graph_storage.graph_path, 'r', encoding='utf-8') as f:
            graph = json.load(f)

        with open(GRAPH_FOR_BAYES_PATH, 'r', encoding='utf-8') as f:
            most_relative_nodes = json.load(f)

        graph = SimpleNonRelativeNodesDeleter().delete_nodes(
            nx.node_link_graph(graph, edges='links'),
            most_relative_nodes=most_relative_nodes,
            roots=[node['id'] for node in graph['nodes']
                   if node['name'] in drugs]
        )
        graph = nx.node_link_data(graph, edges='links')

        prob_data, drug_states_input_data, drugs_for_output, \
            combination_description = load_combined_data(
                graph_data=graph,
                prob_file=graph_storage.probability_path,
                drug_states_input=self._get_bin_ids(drugs)
            )

        # Построение сети с новыми параметрами
        network = build_network(graph, prob_data)

        # Перерасчет вероятностей (логирование не меняется)
        final_probs = calculate_probabilities(network)

        data = get_result(
            final_probs,
            graph,
            drug_states_input_data,
            drugs_for_output,
            combination_description
        )

        result = {
                    "сompatibility_bayes": сompatibility_bayes,
                    "rank_iteractions": "unknown",
                    "side_effects": [
                        {
                            "сompatibility": "unknown",
                            "effects": []

                        }],
                    "combinations": "unknown",
                    "drugs": drugs
            }

        # result = {
        #             "сompatibility_bayes": сompatibility_bayes,
        #             "rank_iteractions": "unknown",
        #             "side_effects": [
        #                 {
        #                     "сompatibility": "unknown",
        #                     "effects": []

        #                 },
        #                 {
        #                     "сompatibility": "compatible",
        #                     "effects": []

        #                 },
        #                 {
        #                     "сompatibility": "caution",
        #                     "effects": []

        #                 },
        #                 {
        #                     "сompatibility": "incompatible",
        #                     "effects": []

        #                 }
        #                 ],
        #             "combinations": "unknown",
        #             "drugs": drugs
        #     }

        # max_rank = 0
        # for se in data["side_effects"]:
        #     rank = data["side_effects"][se]["probability"]
        #     if rank > max_rank:
        #         max_rank = rank
        #     if not rank:
        #         result["side_effects"][0]["effects"].append({
        #             self.EFFECT_NAME: se,
        #             "rank": rank,
        #         })
        #     elif rank < 0.5:
        #         result["side_effects"][1]["effects"].append({
        #             self.EFFECT_NAME: se,
        #             "rank": rank,
        #         })
        #     elif rank < 0.75:
        #         result["side_effects"][2]["effects"].append({
        #             self.EFFECT_NAME: se,
        #             "rank": rank,
        #         })
        #     elif rank >= 0.75:
        #         result["side_effects"][3]["effects"].append({
        #             self.EFFECT_NAME: se,
        #             "rank": rank,
        #         })

        # if max_rank < 0.5:
        #     сompatibility_bayes = 'compatible'
        # elif max_rank < 0.75:
        #     сompatibility_bayes = 'caution'
        # else:
        #     сompatibility_bayes = 'incompatible'

        # if not exist:
        #     result['сompatibility_bayes'] = сompatibility_bayes

        for se in data["side_effects"]:
            result["side_effects"][0]["effects"].append({
                self.EFFECT_NAME: se,
                "rank": data["side_effects"][se]["probability"],
            })

        result["side_effects"][0]["effects"].sort(key=lambda x: x["rank"],
                                                  reverse=True)

        if gender:
            logger.debug(f'Пол указан. gender = {gender}')
            result["side_effects"][0]["effects"] = (
                self._exclude_by_gender(result["side_effects"][0]["effects"],
                                        gender, GENDER_SIDE_EFFECT))

        message = 'Совместимость ЛС по сети Байеса успешно расcчитана'
        logger.info(f'message = {message}')
        return CustomResponse(
            http_status=status.HTTP_200_OK,
            status=status.HTTP_200_OK,
            message=message,
            data=result
        )


class GraphStorageView(APIView):
    """Вью экспорта/импрота графов для СБ."""

    def post(self, request):
        """Импорт графа и вероятностей."""
        graph_file = request.FILES.get('graph_file')
        probability_file = request.FILES.get('probability_file')

        storage = GraphStorage()

        if graph_file:
            graph = json.load(graph_file)
            result = Lineman().traverse(nx.node_link_graph(graph,
                                                           edges='links'))
            with open(GRAPH_FOR_BAYES_PATH, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            storage.save_graph(graph)
        else:
            message = 'Не был отправлен файл с графом.'
            logger.info(f'message = {message}')
            return CustomResponse(
                http_status=status.HTTP_400_BAD_REQUEST,
                status=status.HTTP_400_BAD_REQUEST,
                message=message
            )
        if probability_file:
            probability = json.load(probability_file)
            storage.save_probability(probability)
        else:
            message = 'Не был отправлен файл с вероятностями.'
            logger.info(f'message = {message}')
            return CustomResponse(
                http_status=status.HTTP_400_BAD_REQUEST,
                status=status.HTTP_400_BAD_REQUEST,
                message=message
            )
        message = 'Граф и вероятности успешно загружены.'
        logger.info(f'message = {message}')
        return CustomResponse(
            http_status=status.HTTP_200_OK,
            status=status.HTTP_200_OK,
            message=message
        )

    def get(self, request):
        """Экспорта графа и вероятностей."""
        storage = GraphStorage()

        if storage.size_of_graph_file == 0:
            message = ('Файл с графов - пустой. '
                       'Пожалуйста, загрузите файл с графом')
            logger.info(f'message = {message}')
            return CustomResponse(
                http_status=status.HTTP_404_NOT_FOUND,
                status=status.HTTP_404_NOT_FOUND,
                message=message
            )
        if storage.size_of_probability_file == 0:
            message = ('Файл с вероятностями - пустой. '
                       'Пожалуйста, загрузите файл с вероятностями')
            logger.info(f'message = {message}')
            return CustomResponse(
                http_status=status.HTTP_404_NOT_FOUND,
                status=status.HTTP_404_NOT_FOUND,
                message=message
            )

        graph = storage.download_graph()
        probability = storage.download_probability()

        drug_number = len(graph[NAME])
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zipedfile:
            zipedfile.writestr(
                f'multigraph_{drug_number}.json',
                json.dumps(graph, ensure_ascii=False, indent=4))
            zipedfile.writestr(
                f'probability_{drug_number}.json',
                json.dumps(probability, ensure_ascii=False, indent=4))
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = (
            f'attachment; filename="graph_export_{drug_number}.zip"')
        return response


class GraphVisualizationView(APIView):
    """Отдаёт граф для визуализации на фронтенде."""

    def get(self, request):
        """Отправка json-файл графа для визуализации."""
        graph = GraphStorage().download_graph()
        if not graph:
            return CustomResponse(
                http_status=status.HTTP_404_NOT_FOUND,
                status=status.HTTP_404_NOT_FOUND,
                message='Граф для не найден'
            )
        return CustomResponse(
            status=status.HTTP_200_OK,
            http_status=status.HTTP_200_OK,
            data=graph
        )
