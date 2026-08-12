from rest_framework import serializers

class BayesColorSerializer(serializers.Serializer):
    """Сериализатор для изменения цветов Байеса."""

    green = serializers.FloatField()
    yellow = serializers.FloatField()
    red = serializers.FloatField()