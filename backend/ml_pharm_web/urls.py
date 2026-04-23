from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from rest_framework.exceptions import NotFound

from . import settings
from drugs.utils.handler404 import API404


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('accounts.urls')),
    path('api/v1/', include('drugs.urls')),
    path('api/v1/', include('menu.urls')),
    path('api/v1/', include('ranker.urls')),
    path('api/v1/', include('medscape_api.urls')),
    path('api/v1/', include('synonyms.urls')),
    path('api/v1/', include('graphs.urls')),
    path('api/v1/', include('contraindications.urls')),
    path('api/v1/', include('med_bayes.urls')),
    path('api/v1/', include('pHistory2se.urls')),
    path('api/v1/', include('logging_system.urls')),

    re_path(r'^mini-front-manager.*$',
            TemplateView.as_view(template_name='index.html')),
    re_path('', API404.as_view(), name='api-404'),
]


def custom_page_not_found(request, exception):
    """Обработка отсутствия ресурса."""
    raise NotFound("Ресурс не найден.")


handler404 = custom_page_not_found


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
