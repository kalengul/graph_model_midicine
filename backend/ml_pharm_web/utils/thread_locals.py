"""
Модуль храниения текущего пользователя.

Хранит текущего пользователя в thread-local
для передачи между middleware и сигналами.
"""

import threading


_thread_locals = threading.local()


def set_current_user(user):
    """Установка текущего пользователя."""
    _thread_locals.user = user


def get_current_user():
    """Получение текущего пользователя."""
    return getattr(_thread_locals, 'user', None)
