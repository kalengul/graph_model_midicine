"""Модуль кастомного респонса."""

from rest_framework.response import Response
from rest_framework import status as DRF_status
from rest_framework import status as DRF_status


class CustomResponse(Response):
    """Кастомный респонс."""

    def __init__(self, data=None, status=DRF_status.HTTP_200_OK, message='успешно',
                 http_status=DRF_status.HTTP_200_OK):
        """Формирование ответа."""
        if status != DRF_status.HTTP_200_OK:
            http_status = status

        formatted_data = {
            "result": {
                "status": status,
                "message": message
            },
            "data": data if data is not None else {}
        }

        super().__init__(data=formatted_data,
                         status=http_status)        
