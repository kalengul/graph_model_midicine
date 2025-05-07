import logging

from rest_framework import serializers
from .models import (DrugGroup,
                     Drug,
                     SideEffect,
                     DrugSideEffect)


logger = logging.getLogger('drugs')


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

    side_effects = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    def create(self, validated_data):
        """Добавление ЛС."""
        side_effects_data = validated_data.pop('side_effects', [])
        drug = Drug.objects.create(**validated_data)

        logger.debug(f'side_effects_data = {side_effects_data}')
        if side_effects_data:
            passed_ids = set()

            for se in side_effects_data:
                se_id = se.get('se_id')
                rank = se.get('rank')
                passed_ids.add(se_id)

                logger.debug(f'se_id = {se_id}')
                logger.debug(f'rank = {rank}')

                try:
                    DrugSideEffect.objects.create(
                        drug=drug,
                        side_effect=SideEffect.objects.get(id=se_id),
                        probability=rank
                    )
                except SideEffect.DoesNotExist:
                    raise serializers.ValidationError(
                        f"ПД с id={se_id} не существует")
            for effect in SideEffect.objects.order_by('id').exclude(
                id__in=passed_ids):
                DrugSideEffect.objects.create(
                    drug=drug,
                    side_effect=effect)
        else:
            for effect in SideEffect.objects.order_by('id').iterator():
                DrugSideEffect.objects.create(
                    drug=drug,
                    side_effect=effect)

        return drug

    class Meta:
        """Настройка сериализатора."""

        model = Drug
        fields = ['id', 'drug_name', 'dg_id', 'side_effects']


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

    side_effects = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    def create(self, validated_data):
        """Добавление ПД."""
        side_effects_data = validated_data.pop('side_effects', [])
        side_effect = SideEffect.objects.create(**validated_data)

        logger.debug(f'side_effects_data = {side_effects_data}')
        if side_effects_data:
            logger.debug('есть side_effects_data')
            passed_ids = set()

            for se in side_effects_data:
                drug_id = se.get('drug_id')
                rank = se.get('rank')
                passed_ids.add(drug_id)

                logger.debug(f'drug_id = {drug_id}')
                logger.debug('rank = {rank}')
                try:
                    DrugSideEffect.objects.create(
                        drug=Drug.objects.get(id=drug_id),
                        side_effect=side_effect,
                        probability=rank
                    )
                except Drug.DoesNotExist:
                    raise serializers.ValidationError(
                        f"ЛС с id={drug_id} не существует")
            for drug in Drug.objects.order_by('id').exclude(
                id__in=passed_ids):
                DrugSideEffect.objects.create(drug=drug,
                                              side_effect=side_effect)
        else:
            for drug in Drug.objects.order_by('id').iterator():
                DrugSideEffect.objects.create(drug=drug,
                                              side_effect=side_effect)

        return side_effect

    class Meta:
        """Настройка сериализатора."""

        model = SideEffect
        fields = ['id', 'se_name', 'side_effects']


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
        source='drug',
        read_only=True)

    se_id = serializers.PrimaryKeyRelatedField(
        source='side_effect',
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
