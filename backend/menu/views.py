from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from menu.models import Menu
from menu.serializers import MenuSerializer, MenuResponseSerializer

from drf_spectacular.utils import extend_schema, OpenApiResponse


class GetMenuAPI(APIView):

    @extend_schema(
        operation_id='menu_list',
        responses={
            200: MenuResponseSerializer,
        },
        tags=['menu'],
    )
    def get(self, request):
        try:
            menu_items = Menu.objects.filter(is_active=True)
            serializer = MenuSerializer(menu_items, many=True)
            
            response_data = {
                "result": {
                    "status": status.HTTP_200_OK,
                    "message": "Меню получено"
                },
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            error_status = status.HTTP_400_BAD_REQUEST
            error_message = "Ошибка при получении меню"
            
            if isinstance(e, Exception):  
                error_status = status.HTTP_500_INTERNAL_SERVER_ERROR
                error_message = "Неизвестная ошибка сервера"
                
            return Response({
                "result": {
                    "status": error_status,
                    "message": error_message
                },
                "data": {}
            }, status=error_status)
