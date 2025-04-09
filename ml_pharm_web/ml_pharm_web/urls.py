from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from ml_pharm_web import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pharm_web.urls')),
    path('accounts/', include('accounts.urls')),

    path('api/v1/', include('drugs.urls')),
    
    path('test-api/v1/', include('test_drf.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
