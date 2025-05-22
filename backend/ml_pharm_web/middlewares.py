import logging

from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from django.db import connection
from django.db.utils import OperationalError

from ml_pharm_web.utils.thread_locals import set_current_user


logger = logging.getLogger('apilog')


def get_transaction_id():
    """Получение идентификатора транзакции."""
    try:

        with connection.cursor() as cursor:
            cursor.execute('SELECT txid_current()')
            return cursor.fetchone()[0]
        
    except OperationalError:
        pass


class APILogMiddleware(MiddlewareMixin):
    """Перехватчик запросов и ответов."""

    def process_request(self, request):
        """Обработка запросов."""
        user = request.user if request.user.is_authenticated else None
        set_current_user(user)

    def process_response(self, request, response):
        """Обработка ответа до отправки клиенту."""
        if request.method not in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return response

        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        method = request.method
        path = request.get_full_path()
        status_code = response.status_code
        timestamp = now().isoformat()
        transaction_id = get_transaction_id()

        log_line = (f"{timestamp} | {user} | {method} {path} | "
                    f"{status_code} | txid={transaction_id}")
        logger.info(log_line)

        return response
