from rest_framework import serializers

from ranker.utils.params_parser import ParamsParser


class ParsedDictField(serializers.Field):
    """Поле сериализатора для словаря."""

    def __init__(self, expected_type=dict, field_name='unknown', **kwargs):
        self.expected_type = expected_type
        self.field_name = field_name
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        parsed = ParamsParser().parse(data, self.expected_type, self.field_name)
        return parsed

    def to_representation(self, value):
        return value
