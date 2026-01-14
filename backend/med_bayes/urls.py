from django.urls import path
from .views import BayeseView


urlpatterns = [
    path('polifarmakoterapiya-bayes/', BayeseView.as_view(), name='bayes'),
]
