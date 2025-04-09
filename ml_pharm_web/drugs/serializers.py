from rest_framework import serializers
from .models import DrugGroup, Drug


class DrugGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrugGroup
        fields = ['id', 'name', 'slug']
        extra_kwargs = {
            'slug': {'read_only': True} 
        }


class DrugSerializer(serializers.ModelSerializer):
    drug_group = serializers.PrimaryKeyRelatedField(
        queryset=DrugGroup.objects.all(),
        required=True,
        error_messages={'does_not_exist': 'Группа ЛС с таким ID не найдена'}
    )

    class Meta:
        model = Drug
        fields = ['id', 'name', 'slug', 'drug_group', 'side_effects']
        extra_kwargs = {
            'slug': {'read_only': True},
            'side_effects': {'required': False} 
        }
