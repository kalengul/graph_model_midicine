"""Модуль кастомного респонса."""

from rest_framework.response import Response
from rest_framework import status as DRF_status
from rest_framework import status as DRF_status


class CustomResponse:
    """Кастомный респонс."""

    @staticmethod
    def response(data=None,
                 status=DRF_status.HTTP_200_OK,
                 message='успешно',
                 http_status=DRF_status.HTTP_200_OK):
        """Отправка ответа."""
        if status != DRF_status.HTTP_200_OK:
            http_status = status

        if data:
            return Response({
                "result": {
                    "status": status,
                    "message": message
                },
                "data": data
            }, status=http_status)
        else:
            return Response({
                "result": {
                    "status": status,
                    "message": message
                },
                "data": {}
            }, status=http_status)
