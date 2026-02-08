from django.urls import path
from .views import MedicalHistoryToSideEffectsAPIView

urlpatterns = [
    path(
        'medical-history-to-side-effects/',
        MedicalHistoryToSideEffectsAPIView.as_view(),
        name='medical-history-to-side-effects'
    ),
]