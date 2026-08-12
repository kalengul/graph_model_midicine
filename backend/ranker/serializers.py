from rest_framework import serializers
from medscape_api.fields import ParsedListField


class CalculationRequestSerializer(serializers.Serializer):
    drugs = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text='Список ID лекарственных средств',
    )
    humanData = serializers.JSONField(
        required=False,
        allow_null=True,
        help_text='Данные о пациенте',
    )
    medCard = serializers.FileField(
        required=False,
        allow_null=True,
        help_text='Медицинская карта',
    )


class CalculationDataSerializer(serializers.Serializer):
    side_effects = serializers.ListField()
    SEFromDrug = serializers.ListField()
    drugs = serializers.ListField(
        child=serializers.CharField(),
    )
    compatibility_fortran = serializers.CharField(
        allow_null=True,
    )
    bannedPairs = serializers.ListField()
    bannedPairsCont = serializers.ListField()