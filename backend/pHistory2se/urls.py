from django.urls import path
from pHistory2se.views import (MedicalHistoryToSideEffectsAPIView,
                               ModelConfigView,
                               DictionaryView,
                               DictionaryDirectoryView
                               )

urlpatterns = [
    path(
        'humandata_from_medcard/',
        MedicalHistoryToSideEffectsAPIView.as_view(),
        name='humandata_from_medcard'
    ),

    # Эндпоинт для работы с моделью
    path('st_model/',
         ModelConfigView.as_view(),
         name='model-config'
    ),

    # Эндпоинты для словаря
    path('dictionary/',
         DictionaryView.as_view(),
         name='dictionary'
    ),
    path('dictionary/directory/',
         DictionaryDirectoryView.as_view(),
         name='dictionary-reload'
    )
]