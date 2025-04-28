from rest_framework import serializers

from ranker.fields import ParsedDictField
from medscape_api.fields import ParsedListField


class QueryParamsSerializer(serializers.Serializer):
    """Сериализватор параметров URL-строк."""

    drugs = ParsedListField(required=False, field_name='drugs')
    humanData = ParsedDictField(required=False, field_name='humanData')
