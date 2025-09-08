import json

from rest_framework.views import APIView
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from drugs.utils.custom_response import CustomResponse
from .serializers import GraphSerializer, UpdateGraphSerializer
from .models import Graph
from graphs.utils.cleaner_graph_db import CleanProcessor
from graphs.utils.graph_loader import JSONGraphLoader
from graphs.utils.graph_manipulator import GraphManipulator
from graphs.utils.binarizer import Binarizer
from graphs.utils.merger import Merger
from graphs.utils.parse_ids import parse_ids


INCORRECT_DATA = 'Некорректные данные'
NAME = 'name'


class GraphView(APIView):
    """Вью для графов."""

    GRAPH_JSON = 'graph_json'
    GRAPH_XML = 'graph_xml'

    def _get_graph_from_file(self, request):
        """Достаёт файл из запроса и возвращает dict-граф или CustomResponse."""
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
        if id:
            try:
                graph = Graph.objects.get(id=id)
            except Graph.DoesNotExist:
                return CustomResponse(
                    status=status.HTTP_404_NOT_FOUND,
                    http_status=status.HTTP_404_NOT_FOUND,
                    message="Граф не найден"
                )

            return CustomResponse(
                data=GraphSerializer(graph).data,
                status=status.HTTP_200_OK,
                http_status=status.HTTP_200_OK,
                message="Граф найден успешно")

        return CustomResponse(
            data=GraphSerializer(Graph.objects.all(), many=True).data,
            status=status.HTTP_200_OK,
            http_status=status.HTTP_200_OK,
            message="Графы получены успешно")

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

    @parse_ids
    def get(self, request, ids, *args, **kwargs):
        """Получение бинарного словаря идентификаторов."""

        bin_ids = Binarizer().binarize(ids)

        return CustomResponse(
            status=status.HTTP_200_OK,
            http_status=status.HTTP_200_OK,
            message='Бинарный словарь id-ов сформировался успешно',
            data=bin_ids)
