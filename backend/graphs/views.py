import json
import io
import zipfile
import logging
from pathlib import Path
from datetime import datetime

import networkx as nx
from rest_framework.views import APIView
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings
import pandas as pd
import numpy as np

from drugs.utils.custom_response import CustomResponse
from graphs.serializers import (GraphSerializer, UpdateGraphSerializer,
                                BayesSerializer, GraphListSerializer)
from graphs.models import Graph
from graphs.utils.cleaner_graph_db import CleanProcessor
from graphs.utils.graph_loader import JSONGraphLoader
from graphs.utils.graph_manipulator import GraphManipulator
from graphs.utils.binarizer import Binarizer
from graphs.utils.merger import Merger
from graphs.utils.parse_ids import parse_ids
from graphs.bayes_calculation import (load_combined_data, get_result,
                                      build_network, calculate_probabilities)
from drugs.models import Drug, SideEffect, DrugSideEffect
from graphs.utils.load_gender_side_effect import GENDER_SIDE_EFFECT
from graphs.utils.graph_storage import GraphStorage
from graphs.utils.text_builder import TextBuilder
from graphs.utils.graph_optimization.lineman import Lineman
# from graphs.utils.graph_optimization.deleter_non_relative_nodes import (
#     SmartNonRelativeNodesDeleter,
#     SimpleNonRelativeNodesDeleter)
# from graphs.utils.parser import GraphParser
from accounts.auth import bearer_token_required


logger = logging.getLogger('graphs')
INCORRECT_DATA = 'Некорректные данные'
NAME = 'name'
NODES = 'nodes'
ID = 'id'
GRAPH_FOR_BAYES_PATH = Path(settings.GRAPH_PATH) / 'node_with_roots.json'


class GraphView(APIView):
    """Вью для графов."""

    GRAPH_JSON = 'graph_json'
    GRAPH_XML = 'graph_xml'

    REMOVING = ("directed", "multigraph", "graph")
    ERROR_COMPATIBILITY = 'Ошибка определения совместимости'

    def _remove_unnecessary_keys_and_values(self, graph):
        """Удаление ненужный клчей и значкний из словаря графа."""
        for key in self.REMOVING:
            graph.pop(key)
        return graph

    def _parse_ids(self, ids):
        """Парсинг списка id."""
        parsed_ids = []
        for id in ids:
            parsed_id = id.replace('[', '').replace(']', '').split(', ')
            for item in parsed_id:
                parsed_id = int(item)
                parsed_ids.append(item)
        return parsed_ids

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
                message=message
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
                    json_graph = json.load(f)
                    # graph = json.load(f)

                # with open(GRAPH_FOR_BAYES_PATH, 'r', encoding='utf-8') as f:
                #     most_relative_nodes = json.load(f)

                # print('drugs =', drugs)

                # graph = SmartNonRelativeNodesDeleter().delete_nodes(
                #     nx.node_link_graph(graph, edges='links'),
                #     most_relative_nodes=most_relative_nodes,
                #     roots=[node['id'] for node in graph['nodes']
                #            if node['name'] in drugs])

                # json_graph = nx.node_link_data(graph, edges='links')
                # json_graph = GraphParser().jsonPolina(json_graph)
                json_graph['name'] = drugs
                json_graph = self._remove_unnecessary_keys_and_values(
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


class CRUDGraphView(APIView):
    """Вью для CRUD."""

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

    def get(self, request):
        """Получение списка графов или отдельных графов."""
        graphs = Graph.objects.all()
        serializer = GraphListSerializer(instance=graphs, many=True)
        return CustomResponse(
            status=status.HTTP_200_OK,
            http_status=status.HTTP_200_OK,
            message='Список графов получен успешно',
            data=serializer.data
        )

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


class BayesTableView(APIView):
    """Вью для таблицы рангов Байеса для каждого ЛС и ПД."""

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

    # @bearer_token_required
    def get(self, request):
        """Получения таблицы рангов Байеса."""
        storage = GraphStorage()
        graph = storage.download_graph()

        drugs = sorted(graph['name'])
        effects = [effect.se_name
                   for effect in SideEffect.objects.all()]
        bayes_table = pd.DataFrame('-', index=drugs, columns=effects)

        # print('len(effects) =', len(effects))
        print('bayes_table =', bayes_table)

        for drug in drugs:
            prob_data, drug_states_input_data, drugs_for_output, \
                combination_description = load_combined_data(
                    graph_data=graph,
                    prob_file=storage.probability_path,
                    drug_states_input=self._get_bin_ids([drug])
                )

            # Построение сети с новыми параметрами
            network = build_network(graph, prob_data)

            # Перерасчет вероятностей (логирование не меняется)
            final_probs = calculate_probabilities(network,
                                                  'calculation_trace.txt')

            data = get_result(
                final_probs,
                graph,
                drug_states_input_data,
                drugs_for_output,
                combination_description)

            for effect in data['side_effects']:
                if effect in effects:
                    bayes_table.loc[drug, effect] = (
                        data['side_effects'][effect]['probability'])

        print('bayes_table =', bayes_table)

        fortran_table = pd.DataFrame('-', index=drugs, columns=effects)
        for drug in drugs:
            for effect in effects:
                fortran_table.loc[drug, effect] = DrugSideEffect.objects.get(
                    drug__drug_name__iexact=drug,
                    side_effect__se_name__iexact=effect).rang_base

        print('bayes_table =', bayes_table)
        # print('fortran_table =', fortran_table)

        # --- Преобразуем таблицы в числовой формат ---
        # Заменяем '-' на NaN и конвертируем в float
        bayes_numeric = bayes_table.replace('-', np.nan).astype(float)
        fortran_numeric = fortran_table.replace('-', np.nan).astype(float)

        # --- Вычисляем квадрат разницы ---
        diff_squared = (bayes_numeric - fortran_numeric) ** 2

        # Сумма по строкам (только числа)
        row_sums = diff_squared.sum(axis=1)

        # Заменяем NaN обратно на '-' для отображения (опционально)
        diff_squared_display = diff_squared.fillna('-')
        diff_squared_display['Сумма'] = row_sums.fillna('-')

        # Порог
        epsilon = 0.05

        # Абсолютная разница
        abs_diff = (bayes_numeric - fortran_numeric).abs()

        # Булево сравнение: True если разница <= epsilon
        accuracy_mask = abs_diff <= epsilon

        # Преобразуем True/False в "Верно"/"Неверно"
        accuracy_table = accuracy_mask.replace({True: 'Верно',
                                                False: 'Неверно'})

        # Восстанавливаем '-' вместо значений,
        # где хотя бы одна ячейка была пустой
        # (т.е. где была NaN в исходных числовых таблицах)
        mask_nan = bayes_numeric.isna() | fortran_numeric.isna()
        # # accuracy_table = accuracy_table.mask(mask_nan, '-')
        # accuracy_table = accuracy_table.where(~mask_nan, '-')
        # Создаём копию accuracy_table
        accuracy_table = accuracy_table.copy()

        # Применяем маску напрямую: где mask_nan == True → ставим '-'
        accuracy_table[mask_nan] = '-'
        # Определяем, какие столбцы относятся к эффектам (все, кроме, возможно, уже добавленного 'Сумма')
        # В accuracy_table изначально столько же столбцов, сколько в effects
        effect_columns = effects  # или: [col for col in accuracy_table.columns if col != 'Сумма']

        # Извлекаем под-DataFrame только с эффектами
        acc_effect_part = accuracy_table[effect_columns]

        # Считаем количество "Верно" по строкам
        count_true = (acc_effect_part == 'Верно').sum(axis=1)

        # Считаем общее количество не-"-" значений (т.е. "Верно" или "Неверно")
        count_valid = acc_effect_part.isin(['Верно', 'Неверно']).sum(axis=1)

        # Вычисляем долю
        accuracy_ratio = count_true / count_valid

        # Где нет валидных данных — ставим NaN, затем заменим на '-'
        accuracy_ratio = accuracy_ratio.where(count_valid > 0, np.nan)

        # Добавляем столбец в основную таблицу
        accuracy_table['Доля верно'] = accuracy_ratio.fillna('-')

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            bayes_table.to_excel(writer, sheet_name='Байес', index=True)
            fortran_table.to_excel(writer, sheet_name='Фортран', index=True)
            diff_squared_display.to_excel(writer,
                                          sheet_name='Кв. разности',
                                          index=True)
            accuracy_table.to_excel(writer, sheet_name='Точность', index=True)

        excel_buffer.seek(0)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer,
                             'w',
                             zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('comparison_bayes_and_fortran_tables.xlsx',
                              excel_buffer.getvalue())

        zip_buffer.seek(0)

        response = HttpResponse(
            zip_buffer.getvalue(),
            content_type=('application/zip')
        )
        response['Content-Disposition'] = ('attachment; '
                                           'filename="bayes_tables.zip"')
        return response
