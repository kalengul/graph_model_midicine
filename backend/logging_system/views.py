import os
from django.conf import settings
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

from .models import SystemState
from .serializers import SystemStateSerializer
from .services import CalculationLoggingService

# Определяем путь к лог-файлу
LOG_FILE_PATH = os.path.join(settings.BASE_DIR, 'logs', 'requested_drugs.log')


class SystemStateView(APIView):
    """
    Получение текущего состояния системы (GET).
    Доступно только администраторам.
    """
    # permission_classes = [IsAdminUser]

    def get(self, request):
        state = SystemState.get_current_state()
        serializer = SystemStateSerializer(state)
        return Response(serializer.data)


class LoggingToggleView(APIView):
    """
    Включение/выключение логирования.
    GET – получить текущий статус.
    POST – изменить статус (передать {"enabled": true/false}).
    """
    # permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({'enabled': CalculationLoggingService.is_enabled()})

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
    # permission_classes = [IsAdminUser]

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
    # permission_classes = [IsAdminUser]

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