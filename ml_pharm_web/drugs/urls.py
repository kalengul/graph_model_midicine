from django.urls import path

from .views import DrugGroupAPI, DrugAPI


urlpatterns = [
    path('addDrugGroup/', DrugGroupAPI.as_view(), name='add_drug_group'),
    path('addDrug/', DrugAPI.as_view(), name='add_drug'),
]
