"""Модуль парсера параметров из URL-строк."""

import json
import ast
from rest_framework import serializers


class ParamsParser:
    """Парсер параметров из URL-строки."""

    def parse(self, value, expected_type, field_name):
        """Метод для парсинга."""
        if not isinstance(value, str):
            return value

        try:
            result = json.loads(value)
            if isinstance(result, expected_type):
                return result
        except Exception:
            pass

        try:
            result = ast.literal_eval(value)
            if isinstance(result, expected_type):
                return result

        except Exception:
            pass

        raise serializers.ValidationError({
            field_name: f'Невозможно распарсить поле {field_name}. Неверный формат.'
        })
