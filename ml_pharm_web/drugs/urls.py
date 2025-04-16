from django.urls import path
from .views import (
    DrugGroupAPI,
    # AddDrugGroupAPI,
    # GetDrugGroupAPI,
    DrugAPI,
    # AddDrugAPI,
    # GetDrugAPI,
    SideEffectAPI,
    # GetSideEffectAPI,
    DrugSideEffectView,
    DataImportView,
    DatabaseCleanView,
)


urlpatterns = [
    path('addDrugGroup/', DrugGroupAPI.as_view(), name='add_drug_group'),
    path('getDrugGroup/', DrugGroupAPI.as_view(), name='get_drug_group'),
    # path('detele/?dg_id', DrugGroupAPI.as_view(), name='get_drug_group'),
    # path('addDrugGroup/', AddDrugGroupAPI.as_view(), name='add_drug_group'),
    # path('getDrugGroup/', GetDrugGroupAPI.as_view(), name='get_drug_group'),

    path('addDrug/', DrugAPI.as_view(), name='add_drug'),
    path('getDrug/', DrugAPI.as_view(), name='get_drug'),
    # path('addDrug/', AddDrugAPI.as_view(), name='add_drug'),
    # path('getDrug/', GetDrugAPI.as_view(), name='get_drug'),

    path('addSideEffect/', SideEffectAPI.as_view(), name='add_side_effect'),
    path('getSideEffect/', SideEffectAPI.as_view(), name='get_side_effect'),

    path('updateRanks/', DrugSideEffectView.as_view(), name='update_Ranks'),

    # Манипуляции с БД.
    path('load_to_db/', DataImportView.as_view(), name='load_to_db'),
    path('clean_db/', DatabaseCleanView.as_view(), name='clean_db'),
]
