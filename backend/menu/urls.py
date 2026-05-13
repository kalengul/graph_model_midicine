from django.urls import path
from menu.views import GetMenuAPI


urlpatterns = [
    path('getMenu/', GetMenuAPI.as_view(), name='get_menu'),
]
