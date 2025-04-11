from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from .models import Drug, DrugGroup, SideEffect
from .serializers import (
    DrugSerializer,
    DrugGroupSerializer,
    DrugListRetrieveSerializer,
    SideEffectListRetrieveSerializer
)
from drugs.utils.db_manipulator import DBManipulator


class AddDrugGroupAPI(APIView):
    """Вью-класс для создания групп ЛС."""

    def post(self, request):
        """Метод для запросов POST."""
        serializer = DrugGroupSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {"error": "Группа с таким именем или slug уже существует"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetDrugGroupAPI(APIView):
    """Вью-класс для получения групп ЛС."""

    def get(self, request):
        """Пример вью, которая возвращает одну группу по id."""
        pk = request.query_params.get('id') 
        if not pk:
            return Response(
                {"error": "Необходимо указать ID группы"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            group = DrugGroup.objects.get(pk=pk)
            serializer = DrugGroupSerializer(group)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Группа ЛС не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )


class AddDrugAPI(APIView):
    """Вью-класс для создания ЛС."""

    def post(self, request):
        """Метод для запросов POST."""
        serializer = DrugSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                if 'slug' in str(e):
                    return Response(
                        {"error": "Лекарство с таким slug уже существует"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                return Response(
                    {"error": "Ошибка при создании лекарства"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetDrugAPI(APIView):
    """
    GET api/v1/getDrug/?drug_id={id}.

    Если drug_id не указан — вернуть список всех ЛС.
    Если указан — вернуть одно ЛС.
    """

    def get(self, request):
        """Метод для запросов GET."""
        drug_id = request.query_params.get('drug_id')

        # Если drug_id не указан, возвращаем список всех ЛС
        if not drug_id:
            drugs = Drug.objects.all()
            serializer = DrugListRetrieveSerializer(drugs, many=True)
            return Response({
                "result": {
                    "status": 200,
                    "message": "Список ЛС получен"
                },
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        # Если drug_id указан, пытаемся получить одно ЛС
        try:
            drug = Drug.objects.get(pk=drug_id)
            serializer = DrugListRetrieveSerializer(drug)
            return Response({
                "result": {
                    "status": 200,
                    "message": "ЛС получено"
                },
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Drug.DoesNotExist:
            return Response({
                "result": {
                    "status": 404,
                    "message": "Лекарственное средство не найдено"
                },
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({
                "result": {
                    "status": 500,
                    "message": "Неизвестная ошибка сервера"
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetSideEffectAPI(APIView):
    """
    GET api/v1/getSideEffect/?se_id={id}.

    Если se_id не указан — вернуть список всех побочных эффектов.
    Если указан — вернуть один.
    """

    def get(self, request):
        """Метод для запросов GET."""
        se_id = request.query_params.get('se_id')

        # Если se_id не указан, возвращаем список всех
        if not se_id:
            side_effects = SideEffect.objects.all()
            serializer = SideEffectListRetrieveSerializer(side_effects,
                                                          many=True)
            return Response({
                "result": {
                    "status": 200,
                    "message": "Список побочных эффектов получен"
                },
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        # Если se_id указан, пытаемся получить один
        try:
            se = SideEffect.objects.get(pk=se_id)
            serializer = SideEffectListRetrieveSerializer(se)
            return Response({
                "result": {
                    "status": 200,
                    "message": "Побочный эффект получен"
                },
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except SideEffect.DoesNotExist:
            return Response({
                "result": {
                    "status": 404,
                    "message": "Побочный эффект не найден"
                },
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({
                "result": {
                    "status": 500,
                    "message": "Неизвестная ошибка сервера"
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DataImportView(APIView):
    """Вью-класс для импорта данных в БД из файлов."""

    def post(self, request):
        """Импорт данных из файлов в БД."""
        try:
            rangs_count = DBManipulator().load_to_db()
            return Response({
                'message': ('Данные из файлов импортированы успешно!'
                            f'Рангов {rangs_count}')},
                            status=status.HTTP_200_OK)
        except Exception as error:
            return Response({
                'message': ('При импортировании данных возника ошибка:'
                            f'{error}')},
                            status=status.HTTP_400_BAD_REQUEST)


class DatabaseCleanView(APIView):
    """Вью-класс для отчистки таблиц БД.

    Очищаются таблицы:
        - Drug;
        - SifeEffect;
        - DrugSifeEffect.
    """

    def post(self, request):
        """Очистка таблиц БД."""
        try:
            DBManipulator().clean_db()
            return Response({'message': 'Очистка таблиц прошла успешно!'},
                            status=status.HTTP_200_OK)
        except Exception as error:
            return Response({'message': ('При очистке БД возника ошибка:'
                                         f'{error}')},
                            status=status.HTTP_400_BAD_REQUEST)
