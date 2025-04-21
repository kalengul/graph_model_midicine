"""
ASGI config for ml_pharm_web project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
# Устанавливаем значение переменной окружения DJANGO_SETTINGS_MODULE на 'ml_pharm_web.settings', если она еще не была установлена
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ml_pharm_web.settings')
# Получаем объект приложения ASGI и сохраняем его в переменной application
application = get_asgi_application()
