"""Модуль маршрутов."""

from django.urls import path
from rest_framework.permissions import AllowAny

from .views import (
    index_views,
    show_model_views,
    aboutpage_views,
    LoginUser,
    RegisterUser,
    addpage_views,
    addDrug_views,
    addDrugGroup_views,
    updateSideEffects_views,
    search_drugs,
    search_polipharma_drugs,
    load_to_db,
    clean_db,
    finding_matches,
    MedicationSideEffectListView,
    show_list_med_side_effect,
    MedicationCreateView,
    SideEffectCreateView,
    MedicationSideEffectDetailView,
    SomeApiView
)

urlpatterns = [
    path('', index_views, name='home'),
    path('ml_model/<slug:ml_model_slug>/',
         show_model_views,
         name='show_model'),
    path('about/', aboutpage_views, name='about'),
    path('login/', LoginUser.as_view(), name='login'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('addpage/', addpage_views, name='add_page'),
    path('addDrug/', addDrug_views, name='add_Drug'),
    path('addDrugGroup/', addDrugGroup_views, name='add_DrugGroup'),
    path('updateSideEffects/',
         updateSideEffects_views,
         name='update_SideEffects'),
    path('search/', search_drugs, name='search'),
    path('search_polipharma/',
         search_polipharma_drugs,
         name='search_polipharma'),

    # Манипуляции с БД.
    path('load_to_db/', load_to_db, name='load_to_db'),
    path('clean_db/', clean_db, name='clean_db'),
    # Вспомогательный маршрут. Кандидат на удаление.
    path('finding_matches/', finding_matches, name='finding_matches'),
    # Для просмотра таблиц рангов соотвтествующих ЛС с ПД.
    path('show_list_med_side_effect/',
         show_list_med_side_effect,
         name='show_list_med_side_effect'),
    path('api/medication-side-effects/',
         MedicationSideEffectListView.as_view(),
         name='med-side-effects'),
    path('api/medications/',
         MedicationCreateView.as_view(),
         name='medication-create'),
    path('api/side-effects/',
         SideEffectCreateView.as_view(),
         name='side-effect-create'),
    path('api/medication-side-effects/<int:pk>/',
         MedicationSideEffectDetailView.as_view()),
    path('some-api/', SomeApiView.as_view(permission_classes=[AllowAny])),
]
