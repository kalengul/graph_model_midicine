from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from .models import Drug, DrugGroup
from .serializers import DrugGroupSerializer, DrugSerializer


class BaseCRUDAPI(APIView):
    model = None
    serializer_class = None

    def get(self, request, pk=None):
        try:
            if pk:
                instance = self.model.objects.get(pk=pk)
                serializer = self.serializer_class(instance)

                return Response(serializer.data)
            
            instances = self.model.objects.all()
            serializer = self.serializer_class(instances, many=True)

            return Response(serializer.data)
            
        except ObjectDoesNotExist:
            return Response({"error": "Объект не найден"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            except IntegrityError as e:
                return Response({"error": "Ошибка уникальности"}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DrugGroupAPI(BaseCRUDAPI):
    model = DrugGroup
    serializer_class = DrugGroupSerializer

class DrugAPI(BaseCRUDAPI):
    model = Drug
    serializer_class = DrugSerializer
    