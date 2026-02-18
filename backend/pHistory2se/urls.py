from django.urls import path
from .views import MedicalHistoryToSideEffectsAPIView, LoaderSynonymDictFileView

urlpatterns = [
    path(
        'humandata_from_medcard/',
        MedicalHistoryToSideEffectsAPIView.as_view(),
        name='humandata_from_medcard'
    ),
    path('cont_synonym_dict/',
         LoaderSynonymDictFileView.as_view(),
         name='contraindication-file-api'),
]