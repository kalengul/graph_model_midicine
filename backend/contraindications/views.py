from functools import wraps

from rest_framework.views import APIView
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

from contraindications.models import Contraindication
from contraindications.serializers import (ContraindicationListSerializer,
                                           ContraindicationDetailSerializer)
from drugs.utils.custom_response import CustomResponse


def require_contraindication(func):
    @wraps(func)
    def wrapper(self, request, id=None, *args, **kwargs):
        if not id:
            return CustomResponse(
                http_status=status.HTTP_400_BAD_REQUEST,
                status=status.HTTP_400_BAD_REQUEST,
                message='Не указан ID изменяемого противопоказания',
            )
        try:
            contraindication = Contraindication.objects.get(id=id)
        except ObjectDoesNotExist:
            return CustomResponse(
                status=status.HTTP_404_NOT_FOUND,
                http_status=status.HTTP_404_NOT_FOUND,
                message="Противопоказание не найдено"
            )
        return func(self, request, id=id, contraindication=contraindication,
                    *args, **kwargs)
    return wrapper


class ContraindicationView(APIView):
    """Вью для противопоказаний."""

    def get(self, request, id=None):
        """
        Получение провопоказаний.

        Если id указан, отправляется в ответе указанный объект.
        В противном случае, отправляется полный список.
        """
        if id:
            try:
                contraindication = Contraindication.objects.get(id=id)
                return CustomResponse(
                    status=status.HTTP_200_OK,
                    http_status=status.HTTP_200_OK,
                    message='Противопоказание успешно получено',
                    data=ContraindicationDetailSerializer(
                        contraindication).data
                )
            except ObjectDoesNotExist:
                return CustomResponse(
                    status=status.HTTP_404_NOT_FOUND,
                    http_status=status.HTTP_404_NOT_FOUND,
                    message="Противопоказание не найдено")
        serializer = ContraindicationListSerializer(
            Contraindication.objects.all(),
            many=True
        )
        return CustomResponse(
            status=status.HTTP_200_OK,
            http_status=status.HTTP_200_OK,
            message='Противопоказания успешно получены',
            data=serializer.data)

    def post(self, request):
        """Добавление противопоказания."""
        serializer = ContraindicationListSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            CustomResponse(
                http_status=status.HTTP_201_CREATED,
                status=status.HTTP_201_CREATED,
                message='Противокпоказание успешно добавлено',
                data=serializer.data)
        except ValueError:
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                http_status=status.HTTP_400_BAD_REQUEST,
                message='Такое противопоказание уже есть'
            )
        except Exception as error:
            message = 'Ошибка добавления противопоказания',
            print(f'{message}. Ошибка: {error}')
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=message
            )

    @require_contraindication
    def put(self, request, id=None, contraindication=None):
        """Изменение противопоказания."""
        try:
            serializer = ContraindicationDetailSerializer(contraindication,
                                                          data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return CustomResponse(
                http_status=status.HTTP_200_OK,
                status=status.HTTP_200_OK,
                message='Противопоказание изменено успешно',
                data=serializer.data
            )
        except Exception as error:
            message = 'Ошибка изменения противопоказания',
            print(f'{message}. Ошибка: {error}')
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=message
            )

    @require_contraindication
    def delete(self, request, id=None, contraindication=None):
        """Удаление противопоказания."""        
        contraindication.delete()
        return CustomResponse(
            http_status=status.HTTP_204_NO_CONTENT,
            status=status.HTTP_204_NO_CONTENT,
            message='Противопоказание удалено успешно'
        )
