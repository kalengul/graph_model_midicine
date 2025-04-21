from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from ml_pharm_web import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('pharm_web.urls')),
    path('accounts/', include('accounts.urls')),

    path('api/v1/', include('drugs.urls')),
    path('api/v1/', include('menu.urls')),
    path('api/v1/polifarmakoterapiya-fortran/', include('ranker.urls')),
    path('api/v1/', include('medscape_api.urls')),

    path('api/v1/test/', include('test_drf.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
