from copy import deepcopy

from drf_spectacular.openapi import AutoSchema


class ContractAutoSchema(AutoSchema):
    """
    Кастомная OpenAPI-схема проекта.

    1. Генерирует детерминированные operation_id.
    2. Добавляет CustomResponse envelope ко всем JSON response.
    """

    WRAPPED_MARKER = 'x-custom-response'

    RESULT_SCHEMA = {
        'type': 'object',
        'properties': {
            'status': {
                'type': 'integer',
                'example': 200,
            },
            'message': {
                'type': 'string',
                'example': 'успешно',
            },
        },
        'required': ['status', 'message'],
    }

    def get_operation_id(self):
        """
        Generate deterministic operation IDs.

        /graph/       GET  -> graph_retrieve
        /graph/{id}/  GET  -> graph_retrieve_by_id
        """
        operation_id = super().get_operation_id()

        path = self.path.rstrip('/')

        if '{' in path:
            operation_id = f'{operation_id}_by_id'

        return operation_id

    @staticmethod
    def _is_binary_schema(schema):
        """Проверяет schema для FileResponse / binary response."""
        return (
            schema.get('type') == 'string'
            and schema.get('format') == 'binary'
        )

    @classmethod
    def _wrap_response_schema(cls, schema):
        """Оборачивает data schema в CustomResponse envelope."""
        return {
            'type': 'object',
            cls.WRAPPED_MARKER: True,
            'properties': {
                'result': deepcopy(cls.RESULT_SCHEMA),
                'data': schema,
            },
            'required': ['result', 'data'],
        }

    @classmethod
    def _should_wrap(cls, status_code, schema):
        """Определяет, нужно ли добавлять CustomResponse envelope."""
        if not schema:
            return False

        if str(status_code) == '204':
            return False

        if cls._is_binary_schema(schema):
            return False

        if schema.get(cls.WRAPPED_MARKER):
            return False

        return True

    def _get_response_bodies(self, direction='response'):
        response_bodies = super()._get_response_bodies(direction)

        for status_code, response in response_bodies.items():
            if str(status_code) == '204':
                continue

            content = response.get('content', {})

            for media_type, media in content.items():
                schema = media.get('schema')

                if not self._should_wrap(status_code, schema):
                    continue

                media['schema'] = self._wrap_response_schema(schema)

        return response_bodies