from django.urls import path

from .views import LoginUser, RegisterUser, logout_user


urlpatterns = [
    path('login/', LoginUser.as_view(), name='login'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('logout/', logout_user, name='logout'),
]
