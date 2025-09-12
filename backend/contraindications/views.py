from functools import wraps
import json

from rest_framework.views import APIView
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

from contraindications.models import Contraindication
from contraindications.serializers import (ContraindicationListSerializer,
                                           ContraindicationDetailSerializer)
from drugs.utils.custom_response import CustomResponse
from drugs.models import Drug
from contraindications.utils.adapters import ContraAdapter, DrugAdapter
from contraindications.utils.cleaner import CleanProcessor


def require_contraindication(func):
    @wraps(func)
    def wrapper(view, request, *args, **kwargs):
        contraindication_id = (kwargs.get('id')
                               or request.query_params.get('id'))

        if not contraindication_id:
            return CustomResponse(
                http_status=status.HTTP_400_BAD_REQUEST,
                status=status.HTTP_400_BAD_REQUEST,
                message='Не указан ID изменяемого противопоказания',
            )
        try:
            contraindication = Contraindication.objects.get(
                id=contraindication_id)
        except ObjectDoesNotExist:
            return CustomResponse(
                status=status.HTTP_404_NOT_FOUND,
                http_status=status.HTTP_404_NOT_FOUND,
                message="Противопоказание не найдено"
            )
        return func(view, request, contraindication=contraindication,
                    *args, **kwargs)
    return wrapper


class ContraindicationView(APIView):
    """Вью для противопоказаний."""

    def get(self, request, id=None):
        """
        Получение провопоказаний.

        Если id указан, отправляется в ответе указанный объект.
        В противном случае, отправляется полный список.
        """
        contraindication_id = id or request.query_params.get('id')
        if contraindication_id:
            try:
                contraindication = Contraindication.objects.get(
                    id=contraindication_id)
                return CustomResponse(
                    status=status.HTTP_200_OK,
                    http_status=status.HTTP_200_OK,
                    message='Противопоказание успешно получено',
                    data=ContraindicationDetailSerializer(
                        contraindication).data
                )
            except ObjectDoesNotExist:
                return CustomResponse(
                    status=status.HTTP_404_NOT_FOUND,
                    http_status=status.HTTP_404_NOT_FOUND,
                    message="Противопоказание не найдено")
        serializer = ContraindicationListSerializer(
            Contraindication.objects.all(),
            many=True
        )
        return CustomResponse(
            status=status.HTTP_200_OK,
            http_status=status.HTTP_200_OK,
            message='Группа противопоказаний получена',
            data=serializer.data)

    def post(self, request):
        """Добавление противопоказания."""
        serializer = ContraindicationListSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return CustomResponse(
                http_status=status.HTTP_200_OK,
                status=status.HTTP_200_OK,
                message='Противопоказание успешно добавлено',
                data=serializer.data)
        except ValueError:
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                http_status=status.HTTP_400_BAD_REQUEST,
                message='Такое противопоказание уже есть'
            )
        except Exception as error:
            message = 'Ошибка добавления противопоказания',
            print(f'{message}. Ошибка: {error}')
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=message
            )

    @require_contraindication
    def put(self, request, contraindication=None,  *args, **kwargs):
        """Изменение противопоказания."""
        try:
            serializer = ContraindicationDetailSerializer(contraindication,
                                                          data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return CustomResponse(
                http_status=status.HTTP_200_OK,
                status=status.HTTP_200_OK,
                message='Противопоказание изменено успешно',
                data=serializer.data
            )
        except ValueError:
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                http_status=status.HTTP_400_BAD_REQUEST,
                message='Некорректные данные'
            )
        except Exception as error:
            message = 'Ошибка изменения противопоказания',
            print(f'{message}. Ошибка: {error}')
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=message
            )

    @require_contraindication
    def delete(self, request, contraindication=None,  *args, **kwargs):
        """Удаление противопоказания."""
        contraindication.delete()
        return CustomResponse(
            http_status=status.HTTP_200_OK,
            status=status.HTTP_200_OK,
            message='Противопоказание удалено успешно'
        )


class LoadAndBuildDrugContraindications(APIView):
    """Служебная вьюшка для загрузки противопоказаний ЛС."""

    def post(self, request):
        """Загрузка противопоказаний и связывание с ЛС."""
        loaded_file = request.FILES.get('file')
        contras_key = request.POST.get('contras_key')
        drug_key = request.POST.get('drug_key')
        if not loaded_file:
            return CustomResponse(
                http_status=status.HTTP_400_BAD_REQUEST,
                status=status.HTTP_400_BAD_REQUEST,
                message='Файл с ЛС и противопоказания не загружен'
            )

        data = json.load(loaded_file)

        contras_key = None if not contras_key else [contras_key]
        drug_key = None if not drug_key else [drug_key]

        for item in data:
            drug_name = DrugAdapter(item, drug_key).name
            try:
                drug = Drug.objects.get(drug_name__iexact=drug_name)
            except Drug.DoesNotExist:
                return CustomResponse(
                    http_status=status.HTTP_404_NOT_FOUND,
                    status=status.HTTP_404_NOT_FOUND,
                    message=f'В БД нет такого ЛС: {drug_name}'
                )
            for name in ContraAdapter(item, contras_key).contras:
                try:
                    contraindication = Contraindication.objects.get(
                        name__iexact=name)
                except Contraindication.DoesNotExist:
                    contraindication = Contraindication.objects.create(
                        name=name)
                drug.contraindications.add(contraindication)
        return CustomResponse(
            http_status=status.HTTP_200_OK,
            status=status.HTTP_200_OK,
            message='ЛС и противопоказания успешно связаны'
        )


class ClearContraindication(APIView):
    """Вью полной очистки противопоказания."""

    def delete(self, request):
        """Очистка от всех противопоказаний."""
        try:
            CleanProcessor().get_cleaner().clean()
            return CustomResponse(
                status=status.HTTP_200_OK,
                http_status=status.HTTP_200_OK,
                message="Таблица противопоказаний очищина успешно"
            )
        except Exception as error:
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=('При очистке противопоказаний возника ошибка.'
                         f'Ошибка: {error}')
            )
