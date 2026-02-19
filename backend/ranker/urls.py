from django.urls import path
from . import views


urlpatterns = [
    path('generate-tables/', views.TablesView.as_view(),
         name='table_generation'),
    path('', views.CalculationAPI.as_view(), name='rank_calculation'),
]
