from django.urls import path
from .views import LoginUser, LogoutUser, TokenCheck


urlpatterns = [
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', LogoutUser.as_view(), name='logout'),
    path('check_token/', TokenCheck.as_view(), name='check_token'),
]
