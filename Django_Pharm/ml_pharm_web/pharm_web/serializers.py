from rest_framework import serializers
from .models import (Medication,
                     SideEffect,
                     MedicationSideEffect)


class MedicationSerializer(serializers.ModelSerializer):
    """Сериализатор для ЛС."""

    class Meta:
        """Класс настрокий сериализатора."""

        model = Medication
        fields = ['id', 'name']


class SideEffectSerializer(serializers.ModelSerializer):
    """Сериализатор для ПД."""

    class Meta:
        """Класс настрокий сериализатора."""

        model = SideEffect
        fields = ['id', 'name', 'weight']


class MedicationSideEffectSerializer(serializers.ModelSerializer):
    """Сериализатор класса для данных о рангах."""

    medication = MedicationSerializer()
    side_effect = SideEffectSerializer()

    class Meta:
        """Класс настрокий сериализатора."""

        model = MedicationSideEffect
        fields = '__all__'
