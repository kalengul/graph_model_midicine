from rest_framework import serializers

from medscape_api.fields import ParsedListField


class QueryParamsSerializer(serializers.Serializer):
    """Сериализватор параметров URL-строк."""

    drugs = ParsedListField(required=False, field_name='drugs')
    humanData = serializers.IntegerField()