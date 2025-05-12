from rest_framework.views import APIView
from rest_framework import status
from accounts.auth import bearer_token_required
from drugs.utils.custom_response import CustomResponse
from .serializers import SynonymUpdateSerializer


class SynonymGroupAPI(APIView):
    @bearer_token_required
    def get(self, request):
        return CustomResponse.response(
            status=status.HTTP_200_OK,
            message="Группа синонимов получена",
            data=[dict(sg_id=i, sg_name=f'Кластер {i}', completed=i % 10 == 0) for i in range(1, 30)],
        )


class SynonymListAPI(APIView):
    @bearer_token_required
    def get(self, request):
        sg_id = request.query_params.get('sg_id')
        if not sg_id:
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Не указан параметр sg_id",
            )
        
        return CustomResponse.response(
            status=status.HTTP_200_OK,
            message="Список синонимов получен",
            data=[dict(s_id=i, s_name=f'слово {i}', is_changed=i % 5 == 0) for i in range(1, 25)],
        )
    
    @bearer_token_required
    def put(self, request):
        serializer = SynonymUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Неверные данные",
            )
        
        if not serializer.data:
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Не были переданы данные",
            )
    
        updated_ids = []

        s_lists = serializer.validated_data.get('list_id')

        for s_list in s_lists:
            if s_list.get('is_changed'):
                updated_ids.append(s_list.get('s_id'))

        return CustomResponse.response(
            status=status.HTTP_200_OK,
            message=f'Изменены слова: {updated_ids}',
        )
