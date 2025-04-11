from django.urls import path
from . import views


urlpatterns = [
    path('', views.CalculationAPI.as_view(), name='rank_calculation')
]
