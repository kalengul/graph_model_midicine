"""
URL configuration for ml_pharm_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# Импорт функции для обслуживания медиафайлов
from django.conf.urls.static import static
# Импорт модуля для работы с административной панелью
from django.contrib import admin
# Импорт функций для работы с URL-адресами
from django.urls import path, include
# Импорт настроек проекта
from ml_pharm_web import settings

# Определение шаблонов URL для проекта
urlpatterns = [
    # Шаблон URL для административной панели
    path('admin/', admin.site.urls),
    # Включение шаблонов URL из приложения pharm_web
    path('', include('pharm_web.urls')),
    path('test-api/v1/', include('test_drf.urls')),
]

# Добавление шаблона URL для обслуживания медиафайлов во время разработки, если DEBUG установлен в True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
