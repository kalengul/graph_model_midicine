from rest_framework import serializers
from .models import DrugGroup, Drug, SideEffect


class DrugGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrugGroup
        fields = ['id', 'name', 'slug']
        extra_kwargs = {
            'slug': {'read_only': True} 
        }


class DrugSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления/редактирования ЛС
    (в том числе связь c группой и побочными эффектами).
    """
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


class DrugListRetrieveSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода ЛС в формате:
    {
       "id": "...",
       "drug_name": "..."
    }
    """
    drug_name = serializers.CharField(source='name')

    class Meta:
        model = Drug
        fields = ['id', 'drug_name']


class SideEffectSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления/редактирования побочного эффекта
    (если понадобится).
    """
    class Meta:
        model = SideEffect
        fields = ['id', 'name']


class SideEffectListRetrieveSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода побочных эффектов в формате:
    {
       "id": "...",
       "side_effect_name": "..."
    }
    """
    side_effect_name = serializers.CharField(source='name')

    class Meta:
        model = SideEffect
        fields = ['id', 'side_effect_name']
