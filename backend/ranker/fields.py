from rest_framework import serializers

from medscape_api.utils.params_parser import ParamsParser


class ParsedDictField(serializers.Field):
    """Поле сериализатора для словаря."""

    def __init__(self, expected_type=dict, field_name='unknown', **kwargs):
        self.expected_type = expected_type
        self.field_name = field_name
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        return ParamsParser().parse(data, self.expected_type, self.field_name)

    def to_representation(self, value):
        return value
