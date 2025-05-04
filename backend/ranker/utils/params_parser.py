"""Модуль парсер для словарей в url-строках."""

import json
import ast

from rest_framework import serializers


class ParamsParser:
    """Парсер query-параметров URL."""

    HUMAN_DATA = 'humanData'

    def _parse_canonical(self, data, field_name):
        """Напосредственно каноничный парсинг."""
        try:
            parsed = json.loads(data)
        except Exception:
            pass
        try:
            parsed = ast.literal_eval(data)
        except Exception:
            raise serializers.ValidationError(('Отсутствует обязательное '
                                               f'поле {field_name}'))

        normalized = {}
        for key, value in  parsed.items():
            if isinstance(value, list):
                normalized[key] = value
            else:
                normalized[key] = [value]
        return normalized

    def parse(self, query_params, expected_type=dict, field_name='unknown'):
        """Парсинг словаря."""
        if expected_type is dict:
            if query_params:
                return self._parse_canonical(query_params, field_name)
            return None
        else:
            return query_params.get(field_name)
