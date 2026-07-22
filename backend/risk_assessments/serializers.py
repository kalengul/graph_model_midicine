"""
Сериализаторы модуля risk_assessments.
"""
from rest_framework import serializers


class PatientProfileSerializer(serializers.Serializer):
    age = serializers.IntegerField(required=False, allow_null=True, min_value=0, max_value=120)
    gender = serializers.ChoiceField(choices=["man", "woman"], required=False, allow_null=True)
    contList = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        allow_empty=True,
        default=list,
    )


class DrugRiskAssessmentRequestSerializer(serializers.Serializer):
    drugs = serializers.ListField(
        child=serializers.CharField(),
        min_length=2,
        max_length=50,
    )
    patientProfile = PatientProfileSerializer(required=False, allow_null=True)

    def validate_drugs(self, value: list[str]) -> list[str]:
        normalized = [v.lower().replace("/", "+").replace(" ", "") for v in value]
        if len(normalized) != len(set(normalized)):
            raise serializers.ValidationError(
                "Массив drugs содержит дублирующиеся значения после нормализации."
            )
        return normalized