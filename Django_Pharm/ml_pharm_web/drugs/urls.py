from django.urls import path

from .views import *


urlpatterns = [
    path('addpage/', addpage_views, name='add_page'),
    path('addDrug/', add_drug_views, name='add_Drug'),
    path('addDrugGroup/', add_drugGroup_views, name='add_DrugGroup'),
    path('updateSideEffects/', updateSideEffects_views, name='update_SideEffects'),
    path('sideEffects/', list_side_effects_view, name='side_effects_list'),
    path('sideEffects/add/', add_side_effect_view, name='side_effects_add'),
    path('sideEffects/update/<int:drug_id>/', update_side_effect_view, name='side_effects_update'),
    # Манипуляции с БД.
    path('load_to_db/', load_to_db, name='load_to_db'),
    path('clean_db/', clean_db, name='clean_db'),
]
