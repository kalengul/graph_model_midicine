from django.urls import path
from .views import HelloWorld, Menu


urlpatterns = [
    path('hello/', HelloWorld.as_view(), name='hello_world'),
    path('getMenu/', Menu.as_view(), name='menu')
]
