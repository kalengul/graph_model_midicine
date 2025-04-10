from django.urls import path

from .views import *

urlpatterns = [
    path('', index_views, name='home'),
    path('ml_model/<slug:ml_model_slug>/', show_model_views, name='show_model'),
    path('about/', aboutpage_views, name='about'),
    path('search/', search_drugs, name='search'),
    path('search_polipharma/', search_polipharma_drugs, name='search_polipharma'),
    # Вспомогательный маршрут. Кандидат на удаление.
    path('finding_matches/', finding_matches, name='finding_matches'),
    
]
