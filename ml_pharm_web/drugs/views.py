from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Drug, DrugGroup, DrugSideEffect, SideEffect
from .serializers import DrugGroupSerializer, DrugSerializer


class DrugGroupAPI(APIView):
    def get(self, request):
        drug_groups = DrugGroup.objects.all()
        serializer = DrugGroupSerializer(drug_groups, many=True)

        return Response(serializer.data)
    
    def post(self, request):
        serializer = DrugGroupSerializer(request.data)


class DrugAPI(APIView):
    def get(self, request):
        drug_groups = Drug.objects.all()
        serializer = DrugSerializer(drug_groups, many=True)

        return Response(serializer.data)
    
    def post(self, request):
        serializer = DrugSerializer(request.data)
