"""Модуль парсер для словарей в url-строках."""

import json
import ast

from rest_framework import serializers


class ParamsParser:
    """Парсер query-параметров URL."""

    def _parse_canonical(self, data, field_name):
        """Напосредственно каноничный парсинг."""
        print('data =', data)
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


    def _parse_string_to_list(self, value: str) -> list:
        """Парсинг строки в список."""
        if value.startswith('[') and value.endswith(']'):
            inner = value.strip('[]')
            return [v.strip() for v in inner.split(',') if v.strip()]
        return [value]


    def parse(self, query_params, expected_type=dict, field_name='unknown'):
        """Парсинг словаря."""
        if expected_type is dict:
            if 'humanData' in query_params:
                return self._parse_canonical(query_params['humanData'], field_name)
            return None
        else:
            return query_params.get(field_name)

    def parse_non_canonical(self, query_params):
        """Парсинг неканоничных словарей."""
        human_data_raw = query_params.get('humanData[age]')
        print('human_data_raw =', human_data_raw)
        print('type(human_data_raw) =', type(human_data_raw))
        if human_data_raw:
            human_data_raw = {'age': self._parse_string_to_list(human_data_raw)}
        return human_data_raw
