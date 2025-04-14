from django.urls import path
from .views import *


urlpatterns = [
    path('getMenu/', GetMenuAPI.as_view(), name='get_menu'),
]
