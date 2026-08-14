from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from rest_framework.exceptions import NotFound

from ml_pharm_web import settings
from ml_pharm_web.utils.health_check import health_check
from drugs.utils.handler404 import API404
from django.conf import settings

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


urlpatterns = [
    path('health/', health_check, name='health'),
    path('admin/', admin.site.urls),
    
    path('api/v1/', include('accounts.urls')),
    path('api/v1/', include('drugs.urls')),
    path('api/v1/', include('menu.urls')),
    path('api/v1/', include('ranker.urls')),
    path("api/v1/risk-assessments/", include("risk_assessments.urls")),
    path('api/v1/', include('medscape_api.urls')),
    path('api/v1/', include('synonyms.urls')),
    path('api/v1/', include('graphs.urls')),
    path('api/v1/', include('contraindications.urls')),
    path('api/v1/', include('med_bayes.urls')),
    #path('api/v1/', include('pHistory2se.urls')),
    path('api/v1/', include('logging_system.urls')),
    path('api/v1/', include('combination_checker.urls')),

    # OpenAPI
    path('api/dev/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/dev/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema') , name='swagger-ui'),
    path('api/dev/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    re_path(r'^mini-front-manager.*$', TemplateView.as_view(template_name='index.html')),
    re_path('', API404.as_view(), name='api-404'),
]


def custom_page_not_found(request, exception):
    """Обработка отсутствия ресурса."""
    raise NotFound("Ресурс не найден.")


handler404 = custom_page_not_found


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
