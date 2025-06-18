"""Модуль исключений."""

from drugs.utils.custom_response import CustomResponse
from rest_framework.views import exception_handler
from rest_framework import exceptions


def custom_exception_handler(exc, context):
    if isinstance(exc, exceptions.NotAuthenticated):
        return CustomResponse(
            status=401,
            message="Учетные данные не были предоставлены.",
            http_status=401
        )

    if isinstance(exc, exceptions.AuthenticationFailed):
        return CustomResponse(
            status=401,
            message="Неверные учетные данные.",
            http_status=401
        )

    if isinstance(exc, exceptions.PermissionDenied):
        return CustomResponse(
            status=403,
            message="Доступ запрещен.",
            http_status=403
        )
    
    if isinstance(exc, exceptions.NotFound):
        return CustomResponse(
            status=404,
            message="Ресурс не найден.",
            http_status=404
        )

    if isinstance(exc, exceptions.NotFound):
        return CustomResponse(
            status=404,
            message="Ресурс не найден.",
            http_status=404
        )

    return exception_handler(exc, context)


class IncorrectFile(Exception):
    """Исключение из-за некорректного содержания файла."""

class PairFileError(Exception):
    """Исключение из-за файл запрещённых пар ЛС."""

class PairDBError(Exception):
    """Исключение из-за запрещённых пар ЛС в БД."""
