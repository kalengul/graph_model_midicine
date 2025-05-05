from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drugs.utils.custom_response import CustomResponse

class API404(APIView):
    authentication_classes = [] 
    permission_classes = []     

    def _not_found(self):
        return CustomResponse.response(
            status=404,
            message="Ресурс не найден.",
            http_status=status.HTTP_404_NOT_FOUND
        )

    def get(self, request, *args, **kwargs):
        return self._not_found()

    def post(self, request, *args, **kwargs):
        return self._not_found()

    def put(self, request, *args, **kwargs):
        return self._not_found()

    def delete(self, request, *args, **kwargs):
        return self._not_found()

    def patch(self, request, *args, **kwargs):
        return self._not_found()
