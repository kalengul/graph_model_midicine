from django.urls import path
from .views import (InteractionMedScape,
                    )


urlpatterns = [
    path('', InteractionMedScape.as_view(), name='interaction_medscape'),
]
