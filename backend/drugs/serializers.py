from rest_framework import serializers
from .models import (DrugGroup,
                     Drug,
                     SideEffect,
                     DrugSideEffect)


class DrugGroupSerializer(serializers.ModelSerializer):
    """Сериализатор грппы ЛС."""

    class Meta:
        """Настройка сериализатора."""

        model = DrugGroup
        fields = ['id', 'dg_name']


class DrugSerializer(serializers.ModelSerializer):
    """
    Сериализатор ЛС.

    Выполняет добавление и получение ЛС
    (в том числе связь c группой и побочными эффектами).
    """

    dg_id = serializers.PrimaryKeyRelatedField(
        source='drug_group',
        queryset=DrugGroup.objects.all(),
        required=False,
        allow_null=True,
        error_messages={'does_not_exist': 'Группа ЛС с таким ID не найдена'}
    )

    def create(self, validated_data):
        """Добавление ЛС."""
        side_effects_data = validated_data.pop('side_effects', [])
        drug = Drug.objects.create(**validated_data)

        for se in side_effects_data:
            se_id = se.get('se_id')
            rank = se.get('rank')

            try:
                DrugSideEffect.objects.create(
                    drug=drug,
                    side_effect=SideEffect.objects.get(id=se_id),
                    probability=rank
                )
            except SideEffect.DoesNotExist:
                raise serializers.ValidationError(
                    f"ПД с id={se_id} не существует")

        return drug

    class Meta:
        """Настройка сериализатора."""

        model = Drug
        fields = ['drug_name', 'dg_id', 'side_effects']


class DrugListRetrieveSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода ЛС.

    Вывода ЛС в формате:
    {
       "id": "...",
       "drug_name": "..."
    }
    """

    class Meta:
        """Настройка сериализатора."""

        model = Drug
        fields = ['id', 'drug_name']


class SideEffectSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с побочным действием.

    Выполнения операции добавления/редактирования побочного эффекта.
    (если понадобится).
    """

    class Meta:
        """Настройка сериализатора."""

        model = SideEffect
        fields = ['id', 'se_name']


# class SideEffectListRetrieveSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для вывода побочных эффектов в формате:
#     {
#        "id": "...",
#        "side_effect_name": "..."
#     }
#     """

#     class Meta:
#         """Настройка сериализатора."""

#         model = SideEffect
#         fields = ['id', 'se_name']


class DrugSideEffectSerializer(serializers.ModelSerializer):
    """Сериализатор для рагнов.

    Форман данных:
    "update_rags": [
        {
            "drug_id": 1,
            "se_id": 1,
            "rank": 0.8,
        }
    ]
    """

    class FloatWithCommanField(serializers.FloatField):
        """Расширенный класс для исправления точек в числах."""

        def to_internal_value(self, data):
            """Исправление точек в числах."""
            if isinstance(data, str):
                data = data.replace(',', '.')
            return super().to_internal_value(data)

    drug_id = serializers.PrimaryKeyRelatedField(
        # queryset=Drug.objects.all(),
        source='drug',
        # required=True,
        read_only=True)

    se_id = serializers.PrimaryKeyRelatedField(
        # queryset=SideEffect.objects.all(),
        source='side_effect',
        # required=True,
        read_only=True)

    rank = FloatWithCommanField(source='probability')

    class Meta:
        """Настройка сериализатора."""

        model = DrugSideEffect
        fields = [
            'drug_id',
            'se_id',
            'rank',
        ]
