from django.urls import path
from .views import (
    DrugGroupAPI,
    DrugAPI,
    SideEffectAPI,
    DrugSideEffectView,
    ExcelLoadView,
    ModifiedExcelLoadView,
    BannedPairLoadView)


urlpatterns = [
    path('addDrugGroup/', DrugGroupAPI.as_view(), name='add_drug_group'),
    path('getDrugGroup/', DrugGroupAPI.as_view(), name='get_drug_group'),
    path('deleteDrugGroup/', DrugGroupAPI.as_view(), name='delete_drug_group'),

    path('addDrug/', DrugAPI.as_view(), name='add_drug'),
    path('getDrug/', DrugAPI.as_view(), name='get_drug'),
    path('deleteDrug/', DrugAPI.as_view(), name='delete_drug'),

    path('addSideEffect/', SideEffectAPI.as_view(), name='add_side_effect'),
    path('getSideEffect/', SideEffectAPI.as_view(), name='get_side_effect'),
    path('deleteSideEffect/', SideEffectAPI.as_view(),
         name='delete_drug_group'),

    path('getRanks/', DrugSideEffectView.as_view(), name='get_ranks'),
    path('updateRanks/', DrugSideEffectView.as_view(), name='update_ranks'),

    path('export_from_db/', ExcelLoadView.as_view(), name='export_from_db'),
    path('import_to_db/', ExcelLoadView.as_view(), name='import_to_db'),

    path('simple_export_from_db/',
         ModifiedExcelLoadView.as_view(),
         name='simple_export_from_db'),

    path('import_banned_pair/',
         BannedPairLoadView.as_view(),
         name='import_banned_pair'),
]
