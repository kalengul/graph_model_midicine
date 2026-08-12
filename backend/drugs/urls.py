from django.urls import path
from drugs.views import (
    DrugGroupAPI,
    DrugAPI,
    SideEffectAPI,
#     DrugSideEffectView,
    ExcelLoadView,
    ModifiedExcelLoadView,
    BannedPairLoadView,
    DrugDataLoadView,
    TradeNameView,
    DrugTradeSearchView)


urlpatterns = [
    path('DrugGroup/', DrugGroupAPI.as_view(), name='group_process'),
    path('Drug/', DrugAPI.as_view(), name='drug_process'),
    path('SideEffect/', SideEffectAPI.as_view(), name='side_e_process'),
    path('Weights/', ExcelLoadView.as_view(), name='ranks_process'),
    path('TradeName/', TradeNameView.as_view(), name='trade_name_process'),
     # path('Ranks/', DrugSideEffectView.as_view(), name='ranks_process'),

    path('simple_export_from_db/', ModifiedExcelLoadView.as_view(), name='simple_export_from_db'),

    path('BannedPair/', BannedPairLoadView.as_view(), name='banned_pair_process'),

     # Загрузка информации о препаратах
     path('drug_data_load/', DrugDataLoadView.as_view(), name='drug_data_load'),

     path('search-drugs/', DrugTradeSearchView.as_view(), name='search_drugs'),
]
