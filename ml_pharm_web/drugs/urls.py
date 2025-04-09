from django.urls import path

from .views import DrugGroupAPI, DrugAPI


urlpatterns = [
    path('addDrugGroup/', DrugGroupAPI.as_view(), name='add_drug_group'),
    path('addDrugGroups/<int:pk>/', DrugGroupAPI.as_view(), name='add_drug_group_detail'),

    path('addDrug/', DrugAPI.as_view(), name='add_drug'),
    path('addDrugs/<int:pk>/', DrugAPI.as_view(), name='add_drug_detail'),
]
