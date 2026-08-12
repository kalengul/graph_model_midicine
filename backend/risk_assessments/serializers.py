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
    

class SideEffectSerializer(serializers.Serializer):
    seName = serializers.CharField()
    rank = serializers.FloatField()


class DrugEffectSerializer(serializers.Serializer):
    compatibility = serializers.CharField()
    effects = SideEffectSerializer(many=True)


class CombinationDrugSerializer(serializers.Serializer):
    name = serializers.CharField()
    sideEffects = SideEffectSerializer(many=True)


class CombinationSerializer(serializers.Serializer):
    compatibility = serializers.CharField()
    drugs = CombinationDrugSerializer(many=True)


class SeFromDrugItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    sideEffects = SideEffectSerializer(many=True)


class CompatibilitySerializer(serializers.Serializer):
    status = serializers.CharField()
    rank = serializers.FloatField()


class BannedPairSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField())
    names = serializers.ListField(child=serializers.CharField())
    reason = serializers.CharField(allow_null=True)


class BannedPairContSerializer(serializers.Serializer):
    drugId = serializers.IntegerField()
    drugName = serializers.CharField()
    contraindicationId = serializers.CharField()
    contraindicationName = serializers.CharField()
    reason = serializers.CharField(allow_null=True)


class RiskAssessmentResponseSerializer(serializers.Serializer):
    drugs = serializers.DictField(child=serializers.CharField())
    compatibility = CompatibilitySerializer()
    bannedPairs = BannedPairSerializer(many=True)
    bannedPairsCont = BannedPairContSerializer(many=True)
    sideEffects = DrugEffectSerializer(many=True)
    combinations = CombinationSerializer(many=True)
    seFromDrug = SeFromDrugItemSerializer(many=True)
