"""Модель парсинга IDs."""

from functools import wraps

from rest_framework import status

from drugs.utils.custom_response import CustomResponse


IDS = 'ids'


def parse_ids(func):
    """Обёртка для парсинг."""
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        """Парсинг ids."""
        ids_param = request.query_params.get(IDS)
        if not ids_param:
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                http_status=status.HTTP_400_BAD_REQUEST,
                message='не указан IDs'
            )

        try:
            ids_param = ids_param.strip().lstrip('[').rstrip(']')
            ids = [int(i) for i in ids_param.split(',')]
        except ValueError:
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                http_status=status.HTTP_400_BAD_REQUEST,
                message='Некорректные данные! IDs должны быть целыми числами'
            )

        kwargs[IDS] = ids

        return func(self, request, *args, **kwargs)

    return wrapper
