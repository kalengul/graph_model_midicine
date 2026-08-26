import logging

from rest_framework import serializers

from side_effects.models import SideEffect, DrugSideEffect
from drugs.models import Drug


logger = logging.getLogger('side_effects')


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

    def validate_se_name(self, value):
        """
        Валидация названия ПД.

        Проверяет наличие ПД в БД перед его добавлением.
        """
        qs = SideEffect.objects.all()
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        for obj in qs:
            if obj.se_name.lower() == value.lower():
                raise serializers.ValidationError(
                    f"Побочный эффект {value} уже существует"
                )
        return value

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
                logger.debug(f'rank = {rank}')
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
    """Сериализатор для рангов.

    Формат данных:
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

    rank = FloatWithCommanField(source='rang_base')

    class Meta:
        """Настройка сериализатора."""

        model = DrugSideEffect
        fields = [
            'drug_id',
            'se_id',
            'rank',
        ]

