import os
from datetime import datetime
import logging
import traceback

from rest_framework.views import APIView
from rest_framework import status
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from django.utils.text import get_valid_filename
from rest_framework.response import Response

from accounts.auth import bearer_token_required
from drugs.utils.custom_response import CustomResponse
from .serializers import (
    SynonymGroupCreateSerializer,
    SynonymGroupListSerializer,
    SynonymListSerializer,
    SynonymCreateSerializer,
    SynonymUpdateSerializer,
    FileUploadSerializer,
    SynonymStatusSerializer,
    ChangeSynonymStatusSerializer,
)
from .models import Synonym, SynonymGroup, SynonymStatus
from synonyms.utils.json_synonums_loader import (InnerJSONSynonymLoader,
                                                 )
from synonyms.utils.synonym_cleaner import CleanProcessor


logger = logging.getLogger('synonyms')


class SynonymGroupAPI(APIView):

    @bearer_token_required
    def get(self, request):
        serializer = SynonymGroupListSerializer(SynonymGroup.objects.all(),
                                                many=True)

        return CustomResponse(
            status=status.HTTP_200_OK,
            message="Группа синонимов получена",
            data=serializer.data,        
        )
    
    @bearer_token_required
    def post(self, request):
        logger.debug(f'request.data = {request.data}')
        serializer = SynonymGroupCreateSerializer(data=request.data)

        if not serializer.is_valid():
            logger.debug(f'request.errors = {serializer.errors}')
            logger.debug(f'request.error_messages = {serializer.error_messages}')
            traceback.print_exc()
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message="Неверные данные при создании группы синонимов",
            )

        try:
            serializer.save()

            return CustomResponse(
                    data=serializer.data,
                    status=status.HTTP_200_OK,
                    message=(f'Группа Синонимов {request.data.get("name")}'
                             ' добавлена'),
                    http_status=status.HTTP_200_OK,
                )
            
        except IntegrityError:
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message=(f'Группа {request.data.get("name")} уже существует'),
                http_status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception:
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Неизвестная ошибка сервера',
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SynonymListAPI(APIView):

    @bearer_token_required
    def get(self, request):
        sg_id = request.query_params.get('sg_id')

        if not sg_id:
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message="Не указан параметр sg_id",
            )
        
        queryset = Synonym.objects.filter(group_id=sg_id)
        serializer = SynonymListSerializer(queryset, many=True)

        print('serializer.data =', serializer.data)

        return CustomResponse(
            status=status.HTTP_200_OK,
            message="Список синонимов получен",
            data=serializer.data,
        )
    
    @bearer_token_required
    def post(self, request):
        serializer = SynonymCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message="Неверные данные при создании синонимов",
            )

        try:
            sg_id = serializer.validated_data['sg_id']
            names = serializer.validated_data['names']
            group = get_object_or_404(SynonymGroup, pk=sg_id)

            created = []
            for name in names:
                syn = Synonym.objects.create(group=group, name=name)
                created.append({
                    "s_id": syn.id,
                    "s_name": syn.name,
                    "st_id": syn.st_id.id if syn.st_id else None,
                })

            return CustomResponse(
                status=status.HTTP_200_OK,
                message=f"Синонимы добавлены в группу {group.name}",
                data=created,
            )

        except IntegrityError:
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message="Ошибка создания: данные нарушают ограничения уникальности или связей",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception:
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Неизвестная ошибка сервера при создании синонимов",
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @bearer_token_required
    def put(self, request):
        serializer = SynonymUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            errors = serializer.errors
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Неверные данные",
                "errors": errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
        sg_id = serializer.validated_data['sg_id']
        updated_ids = []
        ids = []

        for item in serializer.validated_data['list_id']:
            syn = get_object_or_404(Synonym, pk=item['s_id'], group_id=sg_id)
            # syn.st_id = get_object_or_404(SynonymStatus, pk=item['st_id'])
            st_id = item.get('st_id', None)
            if st_id in (None, 'undefined'):
                syn.st_id = None
            else:
                syn.st_id = get_object_or_404(SynonymStatus, pk=st_id)
            syn.save(update_fields=['st_id'])
            ids.append(syn.id)
            updated_ids.append({'s_id': syn.id,
                                'st_id': item.get('st_id')})

        return CustomResponse(
            status=status.HTTP_200_OK,
            message=f"Изменены слова: {ids}",
            data={"updated_ids": updated_ids},
        )


class LoadSynonymView(APIView):
    """Вью импорта синонимов."""

    @bearer_token_required
    def post(self, request):
        """Импорт синонимов в БД."""
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']

            path = os.path.join(settings.TXT_DB_PATH,
                                get_valid_filename(uploaded_file.name))
            with open(path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            CleanProcessor().get_cleaner().clear_table()
            logger.debug(f'Число групп = {SynonymGroup.objects.count()}')
            logger.debug(f'Число синонимов = {Synonym.objects.count()}')

            try:
                uploaded_file.seek(0)
                InnerJSONSynonymLoader().import_synonyms(uploaded_file)
            except Exception as second_error:
                traceback.print_exc()
                logger.info(('Обычный импорт синонимов не сработал'
                             f' {second_error}'))
                return CustomResponse(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message='Ошибка импорта синонимов',
                    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return CustomResponse(
                message=f'Данные из файл {uploaded_file.name} импортированы успешно!',
                status=status.HTTP_200_OK
            )
        return CustomResponse(
            message='Файл передан некорректно',
            status=status.HTTP_400_BAD_REQUEST,
        )

    @bearer_token_required
    def get(self, request):
        """Экспорт синонимов из БД в json-файл."""
        try:
            response = HttpResponse(InnerJSONSynonymLoader().export_synonyms(),
                                    content_type='application/json; charset=utf-8')
            response['Content-Disposition'] = (
                f'attachment; filename=clusters_{datetime.now().strftime("%Y_%m_%d")}.json')
            return response
        except Exception as error:
            message = 'Ошибка при экспорте синонимов'
            logger.error(f'{message}: {error}')
            return CustomResponse(
                message=message,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SynonymStatusView(APIView):
    """Вью для статуса синонима."""

    @bearer_token_required
    def get(self, request):
        """Получение списка статусов."""
        try:
            statuses = SynonymStatus.objects.all()
            serializer = SynonymStatusSerializer(statuses, many=True)
            return CustomResponse(
                status=status.HTTP_200_OK,
                message='Статусы синонимов успешно получены',
                http_status=status.HTTP_200_OK,
                data=serializer.data
            )
        except Exception as error:
            message = 'Ошибка получения статусов синонимов'
            logger.error(f'{message}: {error}')
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=message,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @bearer_token_required
    def post(self, request):
        """Добавление статуса синонима."""
        serializer = SynonymStatusSerializer(data=request.data)
        if not serializer.is_valid():
            message = (f'Статус {serializer.initial_data["st_name"]}'
                       ' уже создан')
            logger.info(message)
            if 'st_name' in serializer.errors:
                for err in serializer.errors['st_name']:
                    if getattr(err, 'code', '') == 'unique':
                        return CustomResponse(
                            status=status.HTTP_400_BAD_REQUEST,
                            message=message,
                            http_status=status.HTTP_400_BAD_REQUEST
                        )

            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message='Некорректные поля в теле запроса',
                http_status=status.HTTP_400_BAD_REQUEST
            )

        try:
            serializer.save()
            return CustomResponse(
                status=status.HTTP_200_OK,
                message='Новая группа добавлена',
                http_status=status.HTTP_200_OK,
                data=serializer.data
            )
        except IntegrityError:
            message = f'Статус {serializer.validated_data["st_name"]} уже создан'
            logger.info(message)
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message=message,
                http_status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as error:
            message = 'Ошибка добавления статуса синонима'
            logger.error(f'{message}: {error}')
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=message,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @bearer_token_required
    def put(self, request):
        """Измение цвета статуса синонима."""
        st_id = request.data.get('st_id')
        try:
            instance = SynonymStatus.objects.get(id=st_id)
        except SynonymStatus.DoesNotExist:
            return CustomResponse(
            status=status.HTTP_404_NOT_FOUND,
            message='Статус синонима не найден',
            http_status=status.HTTP_404_NOT_FOUND
            )

        serializer = ChangeSynonymStatusSerializer(instance, data=request.data)
        if not serializer.is_valid():
            errors = serializer.errors
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Неверные данные",
                "errors": errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.save()
            return CustomResponse(
                status=status.HTTP_200_OK,
                message='Успешное обновление данных',
                http_status=status.HTTP_200_OK,
                data=serializer.data
            )
        except Exception as error:
            message = 'Ошибка изменения статуса синонима'
            logger.error(f'{message}: {error}')
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=message,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
