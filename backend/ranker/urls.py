from django.urls import path
from ranker.views import TablesView, CalculationAPI


urlpatterns = [
    path('generate-tables/', TablesView.as_view(), name='table_generation'),
    path('polifarmakoterapiya-fortran/', CalculationAPI.as_view(), name='rank_calculation'),
]
