from rest_framework import serializers
from .models import (Medication,
                     SideEffect,
                     MedicationSideEffect)


class MedicationSerializer(serializers.ModelSerializer):
    """Сериализатор для ЛС."""

    drug_name = serializers.CharField(source='name')
    drug_id = serializers.IntegerField(source='id')

    class Meta:
        """Класс настрокий сериализатора."""

        model = Medication
        fields = ['drug_id', 'drug_name']


class SideEffectSerializer(serializers.ModelSerializer):
    """Сериализатор для ПД."""

    side_name = serializers.CharField(source='name')
    side_id = serializers.IntegerField(source='id')

    class Meta:
        """Класс настрокий сериализатора."""

        model = SideEffect
        fields = ['side_id', 'side_name', 'weight']


class MedicationSideEffectSerializer(serializers.ModelSerializer):
    """Сериализатор класса для данных о рангах."""

    #medication = MedicationSerializer()
    drug_name = serializers.CharField(source='medication.name')
    drug_id = serializers.IntegerField(source='medication.id')
    # side_name = SideEffectSerializer()
    side_name = serializers.CharField(source='side_effect.name')
    side_id = serializers.IntegerField(source='side_effect.id')

    rang_id = serializers.CharField(source='id')

    class Meta:
        """Класс настрокий сериализатора."""

        model = MedicationSideEffect
        fields = ['drug_name',
                  'drug_id',
                  'side_name',
                  'side_id',
                  'rang_id',
                  'rang_base',
                  'rang_f1',
                  'rang_f2',
                  'rang_freq',
                  'rang_m1',
                  'rang_m2',
                  'rang_s']
