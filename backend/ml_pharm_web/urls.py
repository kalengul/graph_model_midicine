from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.exceptions import NotFound
from . import settings
from drugs.utils.handler404 import API404


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('accounts.urls')),
    path('api/v1/', include('drugs.urls')),
    path('api/v1/', include('menu.urls')),
    path('api/v1/polifarmakoterapiya-fortran/', include('ranker.urls')),
    path('api/v1/', include('medscape_api.urls')),
    path('api/v1/', include('synonyms.urls')),

    re_path('', API404.as_view(), name='api-404'),
]


def custom_page_not_found(request, exception):
    raise NotFound("Ресурс не найден.")


handler404 = custom_page_not_found


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
