from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from .models import (Drug,
                     DrugGroup,
                     SideEffect,
                     DrugSideEffect)
from .serializers import (
    DrugSerializer,
    DrugGroupSerializer,
    DrugListRetrieveSerializer,
    SideEffectSerializer,
    DrugSideEffectSerializer
)
from drugs.utils.db_manipulator import DBManipulator
from drugs.utils.custom_response import CustomResponse


INCORRECT_DATA = 'Указаны некорректные данные'
SERVER_ERROR = 'Неизвестная ошибка сервера'


class DrugGroupAPI(APIView):
    """Вью-класс для работы с группами ЛС."""

    def post(self, request):
        """Метод для запросов POST."""
        serializer = DrugGroupSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return CustomResponse.response(
                    status=status.HTTP_200_OK,
                    message=(f'Группа ЛС {request.data.get("dg_name")}'
                             ' добавлена'),
                    http_status=status.HTTP_200_OK)
            except IntegrityError:
                return CustomResponse.response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=(f'Группа {request.data.get("dg_name")}'
                             'уже существует'),
                    http_status=status.HTTP_400_BAD_REQUEST
                )
            except Exception:
                return CustomResponse.response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=SERVER_ERROR,
                    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        return CustomResponse.response(
            status=status.HTTP_400_BAD_REQUEST,
            message=INCORRECT_DATA,
            http_status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Пример вью, которая возвращает группу/список групп."""
        pk = request.query_params.get('dg_id')
        print('pk =', pk)
        if not pk:
            queryset = DrugGroup.objects.all()
            serializer = DrugGroupSerializer(queryset, many=True)
            print('Список групп ЛС!')
            print('serializer.data =', serializer.data)
            return CustomResponse.response(
                data=serializer.data,
                status=status.HTTP_200_OK,
                message="Список групп ЛС получен",
                http_status=status.HTTP_200_OK)
        try:
            group = DrugGroup.objects.get(pk=pk)
            serializer = DrugGroupSerializer(group)
            print('Группа ЛС по id!')
            print('serializer.data =', serializer.data)
            return CustomResponse.response(
                data=serializer.data,
                status=status.HTTP_200_OK,
                message='Группа ЛС получена',
                http_status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return CustomResponse.response(
                status=status.HTTP_404_NOT_FOUND,
                message='Группа ЛС не найдена',
                http_status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        """Метод для запроса DELETE."""
        try:
            instance = DrugGroup.objects.get(
                pk=request.query_params.get('dg_id'))
            instance.delete()
            return CustomResponse.response(
                status=status.HTTP_200_OK,
                message=f'Групп "{instance.dg_name}" удалена',
                http_status=status.HTTP_200_OK)
        except DrugGroup.DoesNotExist:
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Ошибка определения удаляемой группы ЛС',
                http_status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return CustomResponse.response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DrugAPI(APIView):
    """
    Вью-класс для создания ЛС.

    POST api/v1/addGrug/
    Добавление ЛС в БД.

    GET api/v1/getDrug/?drug_id={id}
    Если drug_id не указан — вернуть список всех ЛС.
    Если указан — вернуть одно ЛС.
    """

    def post(self, request):
        """Метод для запросов POST."""
        serializer = DrugSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return CustomResponse.response(
                    status=status.HTTP_200_OK,
                    message=f"ЛС {request.data.get('drug_name')} добавлен",
                    http_status=status.HTTP_200_OK)
            except IntegrityError as error:
                if 'slug' in str(error):
                    return CustomResponse.response(
                        status=status.HTTP_400_BAD_REQUEST,
                        message=(f"ЛС {request.data.get('drug_name')}"
                                 "уже существует"),
                        http_status=status.HTTP_400_BAD_REQUEST)
            except Exception:
                return CustomResponse.response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message='Ошибка при создании лекарства',
                    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return CustomResponse.response(
            status=status.HTTP_400_BAD_REQUEST,
            message=INCORRECT_DATA,
            http_status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Метод для запросов GET."""
        drug_id = request.query_params.get('drug_id')

        # Если drug_id не указан, возвращаем список всех ЛС
        if not drug_id:
            drugs = Drug.objects.all()
            serializer = DrugListRetrieveSerializer(drugs, many=True)
            return CustomResponse.response(
                data=serializer.data,
                status=status.HTTP_200_OK,
                message="Список ЛС получен",
                http_status=status.HTTP_200_OK)

        # Если drug_id указан, пытаемся получить одно ЛС
        try:
            drug = Drug.objects.get(pk=drug_id)
            serializer = DrugListRetrieveSerializer(drug)
            return CustomResponse.response(
                data=serializer.data,
                status=status.HTTP_200_OK,
                message="ЛС получено",
                http_status=status.HTTP_200_OK)
        except Drug.DoesNotExist:
            return CustomResponse.response(
                status=status.HTTP_404_NOT_FOUND,
                message="Лекарственное средство не найдено",
                http_status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return CustomResponse.response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def detele(self, request):
        """Метод для DELETE-запросов."""
        try:
            instance = Drug.objects.get(
                pk=request.query_params.get('drug_id'))
            instance.delete()
            return CustomResponse.response(
                status=status.HTTP_200_OK,
                message=f'ЛС "{instance.drug_name}" удалено',
                http_status=status.HTTP_200_OK)
        except Drug.DoesNotExist:
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Ошибка определения удаляемого ЛС',
                http_status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return CustomResponse.response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class AddDrugGroupAPI(APIView):
#     """Вью-класс для создания групп ЛС."""

#     def post(self, request):
#         """Метод для запросов POST."""
#         serializer = DrugGroupSerializer(data=request.data)
#         if serializer.is_valid():
#             try:
#                 serializer.save()
#                 return CustomResponse.response(
#                     status=status.HTTP_200_OK,
#                     message=f'Группа ЛС {request.data.get('dg_name')}',
#                     http_status=status.HTTP_200_OK)
#             except IntegrityError:
#                 return CustomResponse.response(
#                     status=status.HTTP_400_BAD_REQUEST,
#                     message=f'Группа {request.data.get('dg_name')} уже существует',
#                     http_status=status.HTTP_400_BAD_REQUEST
#                 )
#             except Exception:
#                 return CustomResponse.response(
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     message=SERVER_ERROR,
#                     http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                     )
#         return CustomResponse.response(
#             status=status.HTTP_400_BAD_REQUEST,
#             message=INCORRECT_DATA,
#             http_status=status.HTTP_400_BAD_REQUEST
#         )


# class GetDrugGroupAPI(APIView):
#     """Вью-класс для получения групп ЛС."""

#     def get(self, request):
#         """Пример вью, которая возвращает одну группу по id."""
#         pk = request.query_params.get('id')
#         if not pk:
#             return Response(
#                 {"error": "Необходимо указать ID группы"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         try:
#             group = DrugGroup.objects.get(pk=pk)
#             serializer = DrugGroupSerializer(group)
#             return Response(serializer.data)
#         except ObjectDoesNotExist:
#             return Response(
#                 {"error": "Группа ЛС не найдена"},
#                 status=status.HTTP_404_NOT_FOUND
#             )


# class AddDrugAPI(APIView):
#     """Вью-класс для создания ЛС."""

#     def post(self, request):
#         """Метод для запросов POST."""
#         serializer = DrugSerializer(data=request.data)
#         if serializer.is_valid():
#             try:
#                 serializer.save()
#                 return CustomResponse.response(
#                     status=status.HTTP_200_OK,
#                     message=f"ЛС {request.data.get('drug_name')} добавлен",
#                     http_status=status.HTTP_200_OK)
#             except IntegrityError as e:
#                 if 'slug' in str(e):
#                     return CustomResponse.response(
#                         status=status.HTTP_400_BAD_REQUEST,
#                         message=f"ЛС {request.data.get('drug_name')} уже существует",
#                         http_status=status.HTTP_400_BAD_REQUEST
#                     )
#                 return CustomResponse.response(
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     message='Ошибка при создании лекарства',
#                     http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                 )
#         return CustomResponse.response(
#             status=status.HTTP_400_BAD_REQUEST,
#             message=INCORRECT_DATA,
#             http_status=status.HTTP_400_BAD_REQUEST
#         )


# class GetDrugAPI(APIView):
#     """
#     GET api/v1/getDrug/?drug_id={id}.

#     Если drug_id не указан — вернуть список всех ЛС.
#     Если указан — вернуть одно ЛС.
#     """

#     def get(self, request):
#         """Метод для запросов GET."""
#         drug_id = request.query_params.get('drug_id')

#         # Если drug_id не указан, возвращаем список всех ЛС
#         if not drug_id:
#             drugs = Drug.objects.all()
#             serializer = DrugListRetrieveSerializer(drugs, many=True)
#             return Response({
#                 "result": {
#                     "status": 200,
#                     "message": "Список ЛС получен"
#                 },
#                 "data": serializer.data
#             }, status=status.HTTP_200_OK)

#         # Если drug_id указан, пытаемся получить одно ЛС
#         try:
#             drug = Drug.objects.get(pk=drug_id)
#             serializer = DrugListRetrieveSerializer(drug)
#             return Response({
#                 "result": {
#                     "status": 200,
#                     "message": "ЛС получено"
#                 },
#                 "data": serializer.data
#             }, status=status.HTTP_200_OK)
#         except Drug.DoesNotExist:
#             return Response({
#                 "result": {
#                     "status": 404,
#                     "message": "Лекарственное средство не найдено"
#                 },
#                 "data": {}
#             }, status=status.HTTP_404_NOT_FOUND)
#         except Exception:
#             return Response({
#                 "result": {
#                     "status": 500,
#                     "message": SERVER_ERROR
#                 }
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SideEffectAPI(APIView):
    """
    Вью для побочных дейсйствий.

    Добавление побочныз действий.
    POST api/v1/addSideEffect

    Получение побочного действия или списка побочных действий.
    GET api/v1/getSideEffect/?se_id={id}.

    Если se_id не указан — вернуть список всех побочных эффектов.
    Если указан — вернуть один.
    """

    def post(self, request):
        """Метод для запросов POST."""
        serializer = SideEffectSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return CustomResponse.response(
                    status=status.HTTP_200_OK,
                    message=(f'Побочный эффект {request.data.get("se_name")}'
                             'добавлен'),
                    http_status=status.HTTP_200_OK)
            except IntegrityError:
                return CustomResponse.response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=(f'Побочный эффект {request.data.get("se_name")}'
                             'уже существует'),
                    http_status=status.HTTP_400_BAD_REQUEST
                )
            except Exception:
                return CustomResponse.response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=SERVER_ERROR,
                    http_status=status.HTTP_400_BAD_REQUEST
                )
        return CustomResponse.response(
            status=status.HTTP_400_BAD_REQUEST,
            message=INCORRECT_DATA,
            http_status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Метод для запросов GET."""
        se_id = request.query_params.get('se_id')

        # Если se_id не указан, возвращаем список всех
        if not se_id:
            serializer = SideEffectSerializer(SideEffect.objects.all(),
                                              many=True)
            return CustomResponse.response(
                data=serializer.data,
                status=status.HTTP_200_OK,
                message="Список побочных эффектов получен",
                http_status=status.HTTP_200_OK)

        # Если se_id указан, пытаемся получить один
        try:
            serializer = SideEffectSerializer(SideEffect.objects.get(pk=se_id))
            return CustomResponse.response(
                data=serializer.data,
                status=status.HTTP_200_OK,
                message="Побочный эффект получен",
                http_status=status.HTTP_200_OK)
        except SideEffect.DoesNotExist:
            return CustomResponse.response(
                status=status.HTTP_404_NOT_FOUND,
                message="Побочный эффект не найден",
                http_status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return CustomResponse.response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        """Метод для DELETE-запросы."""
        try:
            instance = SideEffect.objects.get(
                pk=request.query_params.get('se_id'))
            instance.delete()
            return CustomResponse.response(
                status=status.HTTP_200_OK,
                message=f'Побочное действие "{instance.se_name}" удалено',
                http_status=status.HTTP_200_OK)
        except SideEffect.DoesNotExist:
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Ошибка определения удаляемого побочного действия',
                http_status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return CustomResponse.response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class GetSideEffectAPI(APIView):
#     """
#     GET api/v1/getSideEffect/?se_id={id}.

#     Если se_id не указан — вернуть список всех побочных эффектов.
#     Если указан — вернуть один.
#     """

#     def get(self, request):
#         """Метод для запросов GET."""
#         se_id = request.query_params.get('se_id')

#         # Если se_id не указан, возвращаем список всех
#         if not se_id:
#             side_effects = SideEffect.objects.all()
#             serializer = SideEffectListRetrieveSerializer(side_effects,
#                                                           many=True)
#             return Response({
#                 "result": {
#                     "status": 200,
#                     "message": "Список побочных эффектов получен"
#                 },
#                 "data": serializer.data
#             }, status=status.HTTP_200_OK)

#         # Если se_id указан, пытаемся получить один
#         try:
#             se = SideEffect.objects.get(pk=se_id)
#             serializer = SideEffectListRetrieveSerializer(se)
#             return Response({
#                 "result": {
#                     "status": 200,
#                     "message": "Побочный эффект получен"
#                 },
#                 "data": serializer.data
#             }, status=status.HTTP_200_OK)
#         except SideEffect.DoesNotExist:
#             return Response({
#                 "result": {
#                     "status": 404,
#                     "message": "Побочный эффект не найден"
#                 },
#                 "data": {}
#             }, status=status.HTTP_404_NOT_FOUND)
#         except Exception:
#             return Response({
#                 "result": {
#                     "status": 500,
#                     "message": SERVER_ERROR
#                 }
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DrugSideEffectView(APIView):
    """Вью для работы с рангами."""

    def put(self, request):
        """Метод для запроса PUT."""
        drug_id = request.data.get('drug_id')
        if not drug_id:
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message='id ЛС не передан',
                http_status=status.HTTP_400_BAD_REQUEST)
        se_id = request.data.get('se_id')

        if not se_id:
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message='id побочного действия не передан')

        if not Drug.objects.filter(id=drug_id).exists():
            return CustomResponse.response(
                status=status.HTTP_404_NOT_FOUND,
                message='Такого ЛС не существует',
                http_status=status.HTTP_404_NOT_FOUND)
        if not SideEffect.objects.filter(id=se_id).exists():
            return CustomResponse.response(
                status=status.HTTP_404_NOT_FOUND,
                message='Такого побочного эффекта не существует',
                http_status=status.HTTP_404_NOT_FOUND)

        try:
            drug_side_effect = DrugSideEffect.objects.get(
                drug_id=drug_id,
                side_effect_id=se_id)
        except DrugSideEffect.DoesNotExist:
            return CustomResponse.response(
                status=status.HTTP_404_NOT_FOUND,
                message='Нет такого ранга',
                http_status=status.HTTP_404_NOT_FOUND
            )
        serializer = DrugSideEffectSerializer(drug_side_effect,
                                              data=request.data)

        if serializer.is_valid():
            serializer.save()
            return CustomResponse.response(
                status=status.HTTP_200_OK,
                message='Ранги обновлены',
                http_status=status.HTTP_200_OK
            )
        return CustomResponse.response(
                status=status.HTTP_404_NOT_FOUND,
                message='Ранг задан некорректно',
                http_status=status.HTTP_404_NOT_FOUND
            )


class MultiDeleteView(APIView):
    """Вью-класс для множественного удаления."""

    def delete(self, request):
        """Метод одновременного удаления ЛС, ПД, ГЛС."""
        # drug_id = request.query_params.get("drug_id")
        # se_id = request.query_params.get("se_id")
        # dg_id = request.query_params.get("dg_id")

        # deleted = {}
        message = []

        try:
            drug_group = DrugGroup.objects.get(
                pk=request.query_params.get('dg_id'))
            # side_effect.delete()
            # return CustomResponse.response(
            #     status=status.HTTP_200_OK,
            message.append(f'Побочное действие "{drug_group.dg_name}" удалено')
            #     http_status=status.HTTP_200_OK)
        except DrugGroup.DoesNotExist:
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Ошибка определения удаляемого побочного действия',
                http_status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return CustomResponse.response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            drug = Drug.objects.get(
                pk=request.query_params.get('drug_id'))
            message.append(f'Побочное действие "{drug.drug_name}" удалено')
        except Drug.DoesNotExist:
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Ошибка определения удаляемого ЛС',
                http_status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return CustomResponse.response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            side_effect = SideEffect.objects.get(
                pk=request.query_params.get('se_id'))
            # side_effect.delete()
            # return CustomResponse.response(
            #     status=status.HTTP_200_OK,
            message.append((f'Побочное действие "{side_effect.se_name}"'
                            'удалено'))
            #     http_status=status.HTTP_200_OK)
        except SideEffect.DoesNotExist:
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Ошибка определения удаляемого побочного действия',
                http_status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return CustomResponse.response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # if drug_id:
        #     drug = get_object_or_404(Drug, id=drug_id)
        #     drug.delete()
        #     deleted["drug_id"] = drug_id

        # if se_id:
        #     se = get_object_or_404(SideEffect, id=se_id)
        #     se.delete()
        #     deleted["se_id"] = se_id

        # if dg_id:
        #     dg = get_object_or_404(Diagnosis, id=dg_id)
        #     dg.delete()
        #     deleted["dg_id"] = dg_id

        drug_group.delete()
        drug.delete()
        side_effect.delete()

        return CustomResponse.response(
            status=status.HTTP_200_OK,
            message=' '.join(message),
            http_status=status.HTTP_200_OK)


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
