from rest_framework.views import APIView
from rest_framework import status
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from accounts.auth import bearer_token_required
from drugs.utils.custom_response import CustomResponse
from .serializers import (
    SynonymGroupCreateSerializer,
    SynonymGroupListSerializer,
    SynonymListSerializer,
    SynonymCreateSerializer,
    SynonymUpdateSerializer,
)
from .models import Synonym, SynonymGroup


class SynonymGroupAPI(APIView):
    @bearer_token_required
    def get(self, request):
        serializer = SynonymGroupListSerializer(SynonymGroup.objects.all(), many=True)

        return CustomResponse.response(
            status=status.HTTP_200_OK,
            message="Группа синонимов получена",
            data=serializer.data,        
        )
    
    @bearer_token_required
    def post(self, request):
        serializer = SynonymGroupCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Неверные данные при создании группы синонимов",
            )

        try:
            serializer.save()

            return CustomResponse.response(
                    data=serializer.data,
                    status=status.HTTP_200_OK,
                    message=(f'Группа Синонимов {request.data.get("name")} добавлена'),
                    http_status=status.HTTP_200_OK,
                )
            
        except IntegrityError:
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message=(f'Группа {request.data.get("name")} уже существует'),
                http_status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception:
            return CustomResponse.response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Неизвестная ошибка сервера',
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
        
        queryset = Synonym.objects.filter(group_id=sg_id)
        serializer = SynonymListSerializer(queryset,many=True)
        
        return CustomResponse.response(
            status=status.HTTP_200_OK,
            message="Список синонимов получен",
            data=serializer.data,
        )
    
    @bearer_token_required
    def post(self, request):
        serializer = SynonymCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Неверные данные при создании синонимов",
            )

        try:
            sg_id = serializer.validated_data['sg_id']
            names = serializer.validated_data['names']
            group = get_object_or_404(SynonymGroup, pk=sg_id)

            created = []
            for name in names:
                syn = Synonym.objects.create(group=group, name=name)
                created.append({
                    "s_id": syn.id,
                    "s_name": syn.name,
                    "is_changed": syn.is_changed,
                })

            return CustomResponse.response(
                status=status.HTTP_200_OK,
                message=f"Синонимы добавлены в группу {group.name}",
                data=created,
            )

        except IntegrityError:
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Ошибка создания: данные нарушают ограничения уникальности или связей",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception:
            return CustomResponse.response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Неизвестная ошибка сервера при создании синонимов",
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @bearer_token_required
    def put(self, request):
        serializer = SynonymUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Неверные данные",
            )
    
        sg_id = serializer.validated_data['sg_id']
        updated_ids = []

        for item in serializer.validated_data['list_id']:
            syn = get_object_or_404(Synonym, pk=item['s_id'], group_id=sg_id)
            syn.is_changed = item['status']
            syn.save(update_fields=['is_changed'])
            updated_ids.append(syn.id)

        return CustomResponse.response(
            status=status.HTTP_200_OK,
            message=f"Изменены слова: {updated_ids}",
            data={"updated_ids": updated_ids},
        )
    