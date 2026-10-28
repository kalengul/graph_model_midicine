import os
import re
import csv

from django.conf import settings
from django.http import FileResponse, StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.auth import bearer_token_required
from logging_system.models import SystemState
from logging_system.serializers import (SystemStateSerializer,
                                        LoggingToggleSerializer
                                        )
from logging_system.services import LoggingToggleService
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiTypes

# Определяем путь к лог-файлу
LOG_DIR = settings.LOG_DIR
LOG_FILES = {
    'fortran_calc': os.path.join(LOG_DIR, 'fortran_calc.log'),
    'risk_assessments': os.path.join(LOG_DIR, 'risk_assesments.log'),
    'logging_system':   os.path.join(LOG_DIR, 'logging_system.log'),
}


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
        return Response({'enabled': LoggingToggleService.is_enabled()})


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
        LoggingToggleService.set_enabled(bool(enabled))
        return Response({'enabled': LoggingToggleService.is_enabled()})


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
    def get(self, request, log_type: str):
        path = LOG_FILES.get(log_type)
        if not path or not os.path.exists(path):
            return Response(
                {'error': 'Файл логов не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        if request.query_params.get('export', '').lower() == 'csv':
            response = StreamingHttpResponse(
                self._export_csv(path),
                content_type='text/csv; charset=utf-8',
            )
            response['Content-Disposition'] = (
                f'attachment; filename="{os.path.basename(path)}.csv"'
            )
            return response

        return FileResponse(
            open(path, 'rb'),
            content_type='text/plain',
            as_attachment=True,
            filename=os.path.basename(path)
        )

    def _export_csv(self, path: str):
        """Генератор CSV-строк. Без заголовков, 4 колонки, разделитель — запятая."""

        def escape(value: str) -> str:
            if any(ch in value for ch in (';', '"', '\n', '\r')):
                return '"' + value.replace('"', '""') + '"'
            return value

        def generate():
            yield '\ufeff0,1,2,3\n' # BOM для Excel UTF-8

            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    line = line.rstrip('\n')
                    if not line:
                        continue

                    parts = [p.strip() for p in line.split('|')]

                    yield ';'.join(escape(p) for p in parts) + '\n'

        return generate()

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
    def delete(self, request, log_type: str):
            path = LOG_FILES.get(log_type)
            if not path or not os.path.exists(path):
                return Response(
                    {'error': 'Файл логов не найден'},
                    status=status.HTTP_404_NOT_FOUND
                )
            try:
                with open(path, 'w') as f:
                    f.truncate(0)
                return Response({'message': 'Логи очищены'})
            except Exception as e:
                return Response(
                    {'error': f'Ошибка очистки логов: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
