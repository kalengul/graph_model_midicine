"""Модуль обработчика ошибки со статусом 404."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drugs.utils.custom_response import CustomResponse

class API404(APIView):
    """Обработчик ошибки со статусом 404."""

    authentication_classes = [] 
    permission_classes = []     

    def _not_found(self):
        """Метод отправки сообщения об ошибке."""
        return CustomResponse(
            status=404,
            message="Ресурс не найден.",
            http_status=status.HTTP_404_NOT_FOUND
        )

    def get(self, request, *args, **kwargs):
        """Метода для GET-запрос."""
        return self._not_found()

    def post(self, request, *args, **kwargs):
        """Метода для POST-запрос."""
        return self._not_found()

    def put(self, request, *args, **kwargs):
        """Метода для PUT-запрос."""
        return self._not_found()

    def delete(self, request, *args, **kwargs):
        """Метода для DELETE-запрос."""
        return self._not_found()

    def patch(self, request, *args, **kwargs):
        """Метода для PATC-запрос."""
        return self._not_found()
