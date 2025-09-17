import json
import logging
from functools import wraps

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


logger = logging.getLogger('contraindications')


def require_contraindication(func):
    @wraps(func)
    def wrapper(view, request, *args, **kwargs):
        contraindication_id = (kwargs.get('id')
                               or request.query_params.get('id'))

        if not contraindication_id:
            message = 'Не указан ID изменяемого противопоказания'
            logger.info(f'message = {message}')
            return CustomResponse(
                http_status=status.HTTP_400_BAD_REQUEST,
                status=status.HTTP_400_BAD_REQUEST,
                message=message
            )
        try:
            contraindication = Contraindication.objects.get(
                id=contraindication_id)
        except ObjectDoesNotExist:
            message = "Противопоказание не найдено"
            logger.info(f'message = {message}')
            return CustomResponse(
                status=status.HTTP_404_NOT_FOUND,
                http_status=status.HTTP_404_NOT_FOUND,
                message=message
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
                message = 'Противопоказание успешно получено'
                logger.info(f'message = {message}')
                return CustomResponse(
                    status=status.HTTP_200_OK,
                    http_status=status.HTTP_200_OK,
                    message=message,
                    data=ContraindicationDetailSerializer(
                        contraindication).data
                )
            except ObjectDoesNotExist:
                message = "Противопоказание не найдено"
                logger.info(f'message = {message}')
                return CustomResponse(
                    status=status.HTTP_404_NOT_FOUND,
                    http_status=status.HTTP_404_NOT_FOUND,
                    message=message
                    )
        serializer = ContraindicationListSerializer(
            Contraindication.objects.all(),
            many=True
        )
        message = 'Группа противопоказаний получена'
        logger.info(f'message = {message}')
        return CustomResponse(
            status=status.HTTP_200_OK,
            http_status=status.HTTP_200_OK,
            message=message,
            data=serializer.data)

    def post(self, request):
        """Добавление противопоказания."""
        serializer = ContraindicationListSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            message = 'Противопоказание успешно добавлено'
            logger.info(f'message = {message}')
            return CustomResponse(
                http_status=status.HTTP_200_OK,
                status=status.HTTP_200_OK,
                message=message,
                data=serializer.data)
        except ValueError:
            message = 'Такое противопоказание уже есть'
            logger.info(f'message = {message}')
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                http_status=status.HTTP_400_BAD_REQUEST,
                message=message
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
            message = 'Противопоказание изменено успешно'
            logger.info(f'message = {message}')
            return CustomResponse(
                http_status=status.HTTP_200_OK,
                status=status.HTTP_200_OK,
                message=message,
                data=serializer.data
            )
        except ValueError:
            message = 'Некорректные данные'
            logger.info(f'message = {message}')
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                http_status=status.HTTP_400_BAD_REQUEST,
                message=message
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
        message = 'Противопоказание удалено успешно'
        logger.info(f'message = {message}')
        return CustomResponse(
            http_status=status.HTTP_200_OK,
            status=status.HTTP_200_OK,
            message=message
        )


class LoadAndBuildDrugContraindications(APIView):
    """Служебная вьюшка для загрузки противопоказаний ЛС."""

    def post(self, request):
        """Загрузка противопоказаний и связывание с ЛС."""
        loaded_file = request.FILES.get('file')
        contras_key = request.POST.get('contras_key')
        drug_key = request.POST.get('drug_key')
        if not loaded_file:
            message = 'Файл с ЛС и противопоказания не загружен'
            logger.info(f'message = {message}')
            return CustomResponse(
                http_status=status.HTTP_400_BAD_REQUEST,
                status=status.HTTP_400_BAD_REQUEST,
                message=message
            )

        data = json.load(loaded_file)

        contras_key = None if not contras_key else [contras_key]
        drug_key = None if not drug_key else [drug_key]

        for item in data:
            drug_name = DrugAdapter(item, drug_key).name
            try:
                drug = Drug.objects.get(drug_name__iexact=drug_name)
            except Drug.DoesNotExist:
                message = f'В БД нет такого ЛС: {drug_name}'
                logger.info(f'message {message}')
                return CustomResponse(
                    http_status=status.HTTP_404_NOT_FOUND,
                    status=status.HTTP_404_NOT_FOUND,
                    message=message
                )
            for name in ContraAdapter(item, contras_key).contras:
                try:
                    contraindication = Contraindication.objects.get(
                        name__iexact=name)
                except Contraindication.DoesNotExist:
                    contraindication = Contraindication.objects.create(
                        name=name)
                drug.contraindications.add(contraindication)
        message = 'ЛС и противопоказания успешно связаны'
        logger.info(f'message = {message}')
        return CustomResponse(
            http_status=status.HTTP_200_OK,
            status=status.HTTP_200_OK,
            message=message
        )


class ClearContraindication(APIView):
    """Вью полной очистки противопоказания."""

    def delete(self, request):
        """Очистка от всех противопоказаний."""
        try:
            CleanProcessor().get_cleaner().clean()
            message = "Таблица противопоказаний очищина успешно"
            logger.info(f'message = {message}')
            return CustomResponse(
                status=status.HTTP_200_OK,
                http_status=status.HTTP_200_OK,
                message=message
            )
        except Exception as error:
            message = ('При очистке противопоказаний возника ошибка.'
                       f'Ошибка: {error}')
            logger.error(f'message = {message}')
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=message
            )
