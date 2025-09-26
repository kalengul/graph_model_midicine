from django.urls import path

from contraindications.views import (ContraindicationView,
                                     LoadContraindicationView,
                                     ClearContraindication)


urlpatterns = [
    path('contraindications/', ContraindicationView.as_view(),
         name='contraindications-list-create'),
    path('contraindications/<int:id>/', ContraindicationView.as_view(),
         name='contraindications-detail'),
    path('contraindications/load_and_link/',
         LoadContraindicationView.as_view(), name='load_and_link'),
    path('contraindications/clean/', ClearContraindication.as_view(),
         name='clean'),
]
