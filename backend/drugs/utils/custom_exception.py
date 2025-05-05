from drugs.utils.custom_response import CustomResponse
from rest_framework.views import exception_handler
from rest_framework import exceptions


def custom_exception_handler(exc, context):
    if isinstance(exc, exceptions.NotAuthenticated):
        return CustomResponse.response(
            status=401,
            message="Учетные данные не были предоставлены.",
            http_status=401
        )

    if isinstance(exc, exceptions.AuthenticationFailed):
        return CustomResponse.response(
            status=401,
            message="Неверные учетные данные.",
            http_status=401
        )

    if isinstance(exc, exceptions.PermissionDenied):
        return CustomResponse.response(
            status=403,
            message="Доступ запрещен.",
            http_status=403
        )
    
    if isinstance(exc, exceptions.NotFound):
        return CustomResponse.response(
            status=404,
            message="Ресурс не найден.",
            http_status=404
        )

    return exception_handler(exc, context)
