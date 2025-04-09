from rest_framework import serializers
from .models import DrugGroup, Drug


class DrugGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrugGroup
        fields = ['title']


class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = ['name', 'drug_group', 'side_effects']
        