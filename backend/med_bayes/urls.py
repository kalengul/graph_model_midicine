from django.urls import path
from .views import BayeseView, BayesColor


urlpatterns = [
    path('polifarmakoterapiya-bayes/', BayeseView.as_view(), name='bayes'),
    path('bayes_colors/', BayesColor.as_view(), name='bayes'),
]
