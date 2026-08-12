import json
import logging
from functools import wraps

from rest_framework.views import APIView
from rest_framework import status
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from contraindications.models import Contraindication
from contraindications.serializers import (ContraindicationListSerializer,
                                           ContraindicationDetailSerializer,
                                           ContraindicationFileUploadSerializer)
from drugs.utils.custom_response import CustomResponse
# from drugs.models import Drug
# from contraindications.utils.adapters import ContraAdapter, DrugAdapter
from contraindications.utils.cleaner import ContraindicationCleanProcessor
from contraindications.utils.loader import LoadAndBuildDrugContraindications

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes


logger = logging.getLogger('contraindications')


def require_contraindication(func):
    """Проверка id противопоказаний."""
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



@extend_schema_view(
    get=extend_schema(
        operation_id='contraindications_list',
        responses={
            200: OpenApiResponse(
                response=ContraindicationListSerializer(many=True),
                description='Список противопоказаний.',
            ),
            404: OpenApiResponse(
                description='Противопоказание не найдено.',
            ),
        },
        tags=['contraindications'],
    ),
    post=extend_schema(
        operation_id='contraindication_create',
        request=ContraindicationListSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Противопоказание успешно создано.',
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Некорректные данные.',
            ),
            500: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Ошибка добавления противопоказания.',
            ),
        },
        tags=['contraindications'],
    ),
    put=extend_schema(
        operation_id='contraindication_update',
        request=ContraindicationDetailSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Противопоказание успешно изменено.',
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Некорректные данные.',
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Противопоказание не найдено.',
            ),
            500: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Ошибка изменения противопоказания.',
            ),
        },
        tags=['contraindications'],
    ),
    delete=extend_schema(
        operation_id='contraindication_delete',
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Противопоказание успешно удалено.',
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='ID не указан.',
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Противопоказание не найдено.',
            ),
        },
        tags=['contraindications'],
    ),
)
class ContraindicationView(APIView):
    """Вью для противопоказаний."""

    def get(self, request, id=None):
        """
        Получение противопоказаний.

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


@extend_schema_view(
    post=extend_schema(
        operation_id='contraindications_load',
        request=ContraindicationFileUploadSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Противопоказания успешно загружены.',
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Файл не передан.',
            ),
            500: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Ошибка загрузки противопоказаний.',
            ),
        },
        tags=['contraindications'],
    ),
    get=extend_schema(
        operation_id='contraindications_export',
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description='JSON-файл с противопоказаниями.',
            ),
            500: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Ошибка выгрузки.',
            ),
        },
        tags=['contraindications'],
    ),
)
class LoadContraindicationView(APIView):
    """Загрузка противопоказаний из загружаемого файла."""

    def post(self, request):
        """Загрузка противопоказаний и связывание с ЛС."""
        loaded_file = request.FILES.get('file')
        if not loaded_file:
            message = 'Файл с ЛС и противопоказания не загружен'
            logger.info(f'message = {message}')
            return CustomResponse(
                http_status=status.HTTP_400_BAD_REQUEST,
                status=status.HTTP_400_BAD_REQUEST,
                message=message
            )
        data = json.load(loaded_file)
        try:
            # Очистка таблица противопоказаний
            ContraindicationCleanProcessor().get_cleaner().clean()
            # Непосредственно загрузка противопоказаний
            LoadAndBuildDrugContraindications().load(data)
            message = 'Противопоказания загружены успешно'
            logger.info(message)
            return CustomResponse(
                http_status=status.HTTP_200_OK,
                status=status.HTTP_200_OK,
                message=message
            )
        except Exception as error:
            logger.error(f'Ошибка загрузки противопоказаний {error}')
            return CustomResponse(
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='При загрузке противопоказаний в БД произошла ошибка'
            )

    def get(self, request):
        """Выгрузка противопоказаний из БД."""
        try:
            data = LoadAndBuildDrugContraindications().download()
            response = HttpResponse(
                json.dumps(data, ensure_ascii=False, indent=4),
                content_type='application/json'
            )
            response['Content-Disposition'] = (
                'attachment; filename="exported_contraindications.json"')
            return response
        except Exception as error:
            logger.error(f'Ошибка выгрузки противопоказаний {error}')
            return CustomResponse(
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='При выгрузке противопоказаний в БД произошла ошибка'
            )


# class LoadAndBuildDrugContraindications(APIView):
#     """Служебная вьюшка для загрузки противопоказаний ЛС."""

#     def post(self, request):
#         """Загрузка противопоказаний и связывание с ЛС."""
#         loaded_file = request.FILES.get('file')
#         contras_key = request.POST.get('contras_key')
#         drug_key = request.POST.get('drug_key')
#         if not loaded_file:
#             message = 'Файл с ЛС и противопоказания не загружен'
#             logger.info(f'message = {message}')
#             return CustomResponse(
#                 http_status=status.HTTP_400_BAD_REQUEST,
#                 status=status.HTTP_400_BAD_REQUEST,
#                 message=message
#             )

#         data = json.load(loaded_file)

#         contras_key = None if not contras_key else [contras_key]
#         drug_key = None if not drug_key else [drug_key]

#         for item in data:
#             drug_name = DrugAdapter(item, drug_key).name
#             try:
#                 drug = Drug.objects.get(drug_name__iexact=drug_name)
#             except Drug.DoesNotExist:
#                 message = f'В БД нет такого ЛС: {drug_name}'
#                 logger.info(f'message {message}')
#                 return CustomResponse(
#                     http_status=status.HTTP_404_NOT_FOUND,
#                     status=status.HTTP_404_NOT_FOUND,
#                     message=message
#                 )
#             for name in ContraAdapter(item, contras_key).contras:
#                 try:
#                     contraindication = Contraindication.objects.get(
#                         name__iexact=name)
#                 except Contraindication.DoesNotExist:
#                     contraindication = Contraindication.objects.create(
#                         name=name)
#                 drug.contraindications.add(contraindication)
#         message = 'ЛС и противопоказания успешно связаны'
#         logger.info(f'message = {message}')
#         return CustomResponse(
#             http_status=status.HTTP_200_OK,
#             status=status.HTTP_200_OK,
#             message=message
#         )

@extend_schema_view(
    delete=extend_schema(
        operation_id='contraindications_clear',
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Таблица противопоказаний успешно очищена.',
            ),
            500: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Ошибка очистки.',
            ),
        },
        tags=['contraindications'],
    ),
)
class ClearContraindication(APIView):
    """Вью полной очистки противопоказания."""

    def delete(self, request):
        """Очистка от всех противопоказаний."""
        try:
            ContraindicationCleanProcessor().get_cleaner().clean()
            message = "Таблица противопоказаний очищена успешно"
            logger.info(f'message = {message}')
            return CustomResponse(
                status=status.HTTP_200_OK,
                http_status=status.HTTP_200_OK,
                message=message
            )
        except Exception as error:
            message = ('При очистке противопоказаний возникла ошибка.'
                       f'Ошибка: {error}')
            logger.error(f'message = {message}')
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=message
            )
