import os
from django.conf import settings
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.auth import bearer_token_required

from logging_system.models import SystemState
from logging_system.serializers import (SystemStateSerializer,
                                        LoggingToggleSerializer
                                        )
from logging_system.services import CalculationLoggingService


from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiTypes

# Определяем путь к лог-файлу
LOG_FILE_PATH = os.path.join(settings.BASE_DIR, 'logs', 'requested_drugs.log')


class SystemStateView(APIView):
    """
    Получение текущего состояния системы (GET).
    Доступно только администраторам.
    """

    @extend_schema(
        operation_id='system_state',
        responses={
            200: OpenApiResponse(
                response=SystemStateSerializer,
                description='Текущее состояние системы.',
            ),
        },
        tags=['logging'],
    )
    @bearer_token_required
    def get(self, request):
        state = SystemState.get_current_state()
        serializer = SystemStateSerializer(state)
        return Response(serializer.data)

@extend_schema(tags=['logging'])
class LoggingToggleView(APIView):
    """
    Включение/выключение логирования.
    GET – получить текущий статус.
    POST – изменить статус (передать {"enabled": true/false}).
    """

    @extend_schema(
        operation_id='logging_toggle_status',
        responses={
            200: OpenApiResponse(
                response=SystemStateSerializer,
                description='Текущее состояние логирования.',
            ),
        },
        tags=['logging'],
    )
    @bearer_token_required
    def get(self, request):
        return Response({'enabled': CalculationLoggingService.is_enabled()})


    @extend_schema(
        operation_id='logging_toggle',
        request=LoggingToggleSerializer,
        responses={
            200: OpenApiResponse(
                response=SystemStateSerializer,
                description='Состояние логирования успешно изменено.',
            ),
        },
        tags=['logging'],
    )
    @bearer_token_required
    def post(self, request):
        enabled = request.data.get('enabled')
        if enabled is None:
            return Response(
                {'error': 'Поле "enabled" обязательно'},
                status=status.HTTP_400_BAD_REQUEST
            )
        CalculationLoggingService.set_enabled(bool(enabled))
        return Response({'enabled': CalculationLoggingService.is_enabled()})


class LogsExportView(APIView):
    """
    Экспорт файла логов для скачивания.
    """

    @extend_schema(
        operation_id='logs_export',
        responses={
            200: OpenApiTypes.BINARY,
        },
        tags=['logging'],
    )
    @bearer_token_required
    def get(self, request):
        if not os.path.exists(LOG_FILE_PATH):
            return Response(
                {'error': 'Файл логов не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        # Отдаём файл как вложение
        response = FileResponse(
            open(LOG_FILE_PATH, 'rb'),
            content_type='text/plain',
            as_attachment=True,
            filename='requested_drugs.log'
        )
        return response


class LogsDeleteView(APIView):
    """
    Очистка файла логов (DELETE).
    """


    @extend_schema(
        operation_id='logs_delete',
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Логи успешно очищены.',
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Файл логов не найден.',
            ),
            500: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Ошибка очистки логов.',
            ),
        },
        tags=['logging'],
    )
    @bearer_token_required
    def delete(self, request):
        if not os.path.exists(LOG_FILE_PATH):
            return Response(
                {'error': 'Файл логов не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            with open(LOG_FILE_PATH, 'w') as f:
                f.truncate(0)
            return Response({'message': 'Логи очищены'})
        except Exception as e:
            return Response(
                {'error': f'Ошибка очистки логов: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )