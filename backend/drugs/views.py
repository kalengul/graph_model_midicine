import traceback
import logging

from rest_framework.views import APIView
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
from drugs.utils.custom_response import CustomResponse

from accounts.auth import bearer_token_required


logger = logging.getLogger('drugs')

INCORRECT_DATA = 'Указаны некорректные данные'
SERVER_ERROR = 'Неизвестная ошибка сервера'


class DrugGroupAPI(APIView):
    """Вью-класс для работы с группами ЛС."""

    @bearer_token_required
    def post(self, request):
        """Метод для запросов POST."""
        serializer = DrugGroupSerializer(data=request.data)

        if serializer.is_valid():
            try:
                serializer.save()

                return CustomResponse.response(
                    data=serializer.data,
                    status=status.HTTP_200_OK,
                    message=(f'Группа ЛС {request.data.get("dg_name")}'
                             ' добавлена'),
                    http_status=status.HTTP_200_OK)
            except IntegrityError:
                return CustomResponse.response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=(f'Группа {request.data.get("dg_name")}'
                             ' уже существует'),
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
            message=((f'Группа {request.data.get("dg_name")}'
                      ' уже существует')),
            http_status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Пример вью, которая возвращает группу/список групп."""
        pk = request.query_params.get('dg_id')
        if not pk:
            queryset = DrugGroup.objects.all()
            serializer = DrugGroupSerializer(queryset, many=True)
            return CustomResponse.response(
                data=serializer.data,
                status=status.HTTP_200_OK,
                message="Список групп ЛС получен",
                http_status=status.HTTP_200_OK)
        try:
            group = DrugGroup.objects.get(pk=pk)
            serializer = DrugGroupSerializer(group)
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

    @bearer_token_required
    def delete(self, request):
        """Метод для запроса DELETE."""
        try:
            instance = DrugGroup.objects.get(
                pk=request.query_params.get('dg_id'))
            instance.delete()
            return CustomResponse.response(
                status=status.HTTP_200_OK,
                message=f'Группа {instance.dg_name} удалена',
                http_status=status.HTTP_200_OK)
        except DrugGroup.DoesNotExist:
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Ошибка определения удаляемого объекта',
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

    ID = 'id'
    DRUG_NAME = 'drug_name'

    @bearer_token_required
    def post(self, request):
        """Метод для запросов POST."""
        serializer = DrugSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return CustomResponse.response(
                    data={
                            self.ID: serializer.data[self.ID],
                            self.DRUG_NAME: serializer.data[self.DRUG_NAME]
                        },
                    status=status.HTTP_200_OK,
                    message=f"ЛС {request.data.get('drug_name')} добавлен",
                    http_status=status.HTTP_200_OK)
            except IntegrityError as error:
                if 'slug' in str(error):
                    return CustomResponse.response(
                        status=status.HTTP_400_BAD_REQUEST,
                        message=(f"ЛС {request.data.get('drug_name')}"
                                 " уже существует"),
                        http_status=status.HTTP_400_BAD_REQUEST)
            except Exception:
                return CustomResponse.response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message='Ошибка при создании лекарства',
                    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "drug_name" in serializer.errors:
            for error in serializer.errors["drug_name"]:
                if "уже существует" in error.lower():
                    return CustomResponse.response(
                        status=status.HTTP_400_BAD_REQUEST,
                        message=((f'ЛС {request.data.get("drug_name")}'
                                  ' уже существует')),
                        http_status=status.HTTP_400_BAD_REQUEST)
        return CustomResponse.response(
            status=status.HTTP_400_BAD_REQUEST,
            message=(f"ЛС {request.data.get('drug_name')}"
                     " уже существует"),
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
            traceback.print_exc()
            return CustomResponse.response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @bearer_token_required
    def delete(self, request):
        """Метод для DELETE-запросов."""
        try:
            instance = Drug.objects.get(
                pk=request.query_params.get('drug_id'))
            instance.delete()
            return CustomResponse.response(
                status=status.HTTP_200_OK,
                message=f'Лекарственное средство {instance.drug_name} удалено',
                http_status=status.HTTP_200_OK)
        except Drug.DoesNotExist:
            traceback.print_exc()
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Ошибка определения удаляемого ЛС',
                http_status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return CustomResponse.response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

    ID = 'id'
    SE_NAME = 'se_name'

    @bearer_token_required
    def post(self, request):
        """Метод для запросов POST."""
        serializer = SideEffectSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return CustomResponse.response(
                    data={
                        self.ID: serializer.data[self.ID],
                        self.SE_NAME: serializer.data[self.SE_NAME]
                    },
                    status=status.HTTP_200_OK,
                    message=(f'Побочный эффект {request.data.get("se_name")}'
                             ' добавлен'),
                    http_status=status.HTTP_200_OK)
            except IntegrityError:
                return CustomResponse.response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=(f'Побочный эффект {request.data.get("se_name")}'
                             ' уже существует'),
                    http_status=status.HTTP_400_BAD_REQUEST)
            except Exception:
                traceback.print_exc()
                return CustomResponse.response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=SERVER_ERROR,
                    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if "se_name" in serializer.errors:
            for error in serializer.errors["se_name"]:
                if " уже существует" in error.lower():
                    return CustomResponse.response(
                        status=status.HTTP_400_BAD_REQUEST,
                        message=(('Побочное действие '
                                  f'{request.data.get("se_name")}'
                                  ' уже существует')),
                        http_status=status.HTTP_400_BAD_REQUEST)
        return CustomResponse.response(
            status=status.HTTP_400_BAD_REQUEST,
            message=(f'Побочный эффект {request.data.get("se_name")}'
                     'уже существует'),
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

    @bearer_token_required
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
                message='Ошибка определения удаляемого объекта',
                http_status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return CustomResponse.response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DrugSideEffectView(APIView):
    """Вью для работы с рангами."""

    @bearer_token_required
    def put(self, request):
        """Метод для запроса PUT."""
        update_data = request.data.get('update_rsgs')

        if not update_data or not isinstance(update_data, list):
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message='Передан некорректный формат данных',
                http_status=status.HTTP_400_BAD_REQUEST)

        for item in update_data:
            drug_id = item.get('drug_id')
            logger.info(f'drug_id = {drug_id}')
            se_id = item.get('se_id')
            logger.info(f'se_id = {se_id}')
            rank = item.get('rank')
            logger.info(f'rank = {rank}')

            if not drug_id:
                return CustomResponse.response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message='id ЛС не передан',
                    http_status=status.HTTP_400_BAD_REQUEST)

            if not se_id:
                return CustomResponse.response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message='id побочного действия не передан',
                    http_status=status.HTTP_400_BAD_REQUEST)

            if not Drug.objects.filter(id=drug_id).exists():
                return CustomResponse.response(
                    status=status.HTTP_404_NOT_FOUND,
                    message=f'ЛС с id={drug_id} не найдено',
                    http_status=status.HTTP_404_NOT_FOUND)

            if not SideEffect.objects.filter(id=se_id).exists():
                return CustomResponse.response(
                    status=status.HTTP_404_NOT_FOUND,
                    message=f'Побочный эффект с id={se_id} не найден',
                    http_status=status.HTTP_404_NOT_FOUND)

            try:
                drug_side_effect = DrugSideEffect.objects.get(
                    drug_id=drug_id,
                    side_effect_id=se_id
                )
            except DrugSideEffect.DoesNotExist:
                return CustomResponse.response(
                    status=status.HTTP_404_NOT_FOUND,
                    message=(f'Связь drug_id={drug_id} '
                             f'и se_id={se_id} не найдена'),
                    http_status=status.HTTP_404_NOT_FOUND
                )

            serializer = DrugSideEffectSerializer(drug_side_effect, data=item)
            if serializer.is_valid():
                serializer.save()
            else:
                return CustomResponse.response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=f'Некорректный ранг: {serializer.errors}',
                    http_status=status.HTTP_400_BAD_REQUEST
                )

        return CustomResponse.response(
            status=status.HTTP_200_OK,
            message='Ранги успешно обновлены',
            http_status=status.HTTP_200_OK
        )

    def get(self, request):
        """Метод для PUT-запросов."""
        try:
            serializer = DrugSideEffectSerializer(DrugSideEffect.objects.all(),
                                                  many=True)
            return CustomResponse.response(
                data=serializer.data,
                status=status.HTTP_200_OK,
                message="Ранги получены",
                http_status=status.HTTP_200_OK)
        except ValueError:
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Ошибка при получении ранга",
                http_status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return CustomResponse.response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Неизвестная ошибка сервера",
                    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
