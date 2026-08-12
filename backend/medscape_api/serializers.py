"""
backend\medscape_api\serializers.py
"""

from rest_framework import serializers

from medscape_api.fields import ParsedListField


class QueryParamsSerializer(serializers.Serializer):
    """Сериализватор параметров URL-строк."""

    drugs = ParsedListField(required=False, field_name='drugs')

class MedScapeDrugGroupSerializer(serializers.Serializer):
    name = serializers.CharField()
    drugs = serializers.ListField(
        child=serializers.CharField()
    )


class AlternativeMedScapeOutSerializer(serializers.Serializer):
    drug_groups = MedScapeDrugGroupSerializer(
        many=True,
        allow_empty=True,
    )

class AllDrugTableResponseSerializer(serializers.Serializer):
    DrugGroup = serializers.ListField()
    sd = serializers.CharField()
    sd2 = serializers.CharField(allow_blank=True)
    Drug = serializers.ListField()
    DrugInteractionTable = serializers.ListField()
    DrugInteraction = serializers.ListField()
    StringTable = serializers.CharField()


class LoadJSONResponseSerializer(serializers.Serializer):
    main_element = serializers.JSONField()
