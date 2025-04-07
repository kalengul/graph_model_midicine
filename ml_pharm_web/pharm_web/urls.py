from django.urls import path

from .views import *

urlpatterns = [
    path('', index_views, name='home'),
    path('ml_model/<slug:ml_model_slug>/', show_model_views, name='show_model'),
    path('about/', aboutpage_views, name='about'),
    path('login/', LoginUser.as_view(), name='login'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('addpage/', addpage_views, name='add_page'),
    path('addDrug/', addDrug_views, name='add_Drug'),
    path('addDrugGroup/', addDrugGroup_views, name='add_DrugGroup'),
    path('updateSideEffects/', updateSideEffects_views, name='update_SideEffects'),
    path('search/', search_drugs, name='search'),
    path('search_polipharma/', search_polipharma_drugs, name='search_polipharma'),
    # Вспомогательный маршрут. Кандидат на удаление.
    path('finding_matches/', finding_matches, name='finding_matches'),
    
]
