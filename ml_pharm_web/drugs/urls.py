from django.urls import path
from .views import (
    AddDrugGroupAPI,
    GetDrugGroupAPI,
    AddDrugAPI,
    GetDrugAPI,
    GetSideEffectAPI,
    DataImportView,
    DatabaseCleanView,
)


urlpatterns = [
    path('addDrugGroup/', AddDrugGroupAPI.as_view(), name='add_drug_group'),
    path('getDrugGroup/', GetDrugGroupAPI.as_view(), name='get_drug_group'),

    path('addDrug/', AddDrugAPI.as_view(), name='add_drug'),
    path('getDrug/', GetDrugAPI.as_view(), name='get_drug'),

    path('getSideEffect/', GetSideEffectAPI.as_view(), name='get_side_effect'),
    # Манипуляции с БД.
    path('load_to_db/', DataImportView.as_view(), name='load_to_db'),
    path('clean_db/', DatabaseCleanView.as_view(), name='clean_db'),
]
