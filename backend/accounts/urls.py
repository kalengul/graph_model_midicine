from django.urls import path
from .views import LoginUser, LogoutUser, TokenCheck, BackupView


urlpatterns = [
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', LogoutUser.as_view(), name='logout'),
    path('check_token/', TokenCheck.as_view(), name='check_token'),
    path('download_backup/', BackupView.as_view(), name='download_backup'),
]
