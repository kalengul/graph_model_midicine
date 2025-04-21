"""Модуль кастомного респонса."""

from rest_framework.response import Response


class CustomResponse:
    """Кастомный респонс."""

    @staticmethod
    def response(data=None,
                 status=200,
                 message='успешно',
                 http_status=200):
        """Отправка ответа."""
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
