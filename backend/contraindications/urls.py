from django.urls import path

from contraindications.views import ContraindicationView


urlpatterns = [
    path('contraindications/', ContraindicationView.as_view(),
         name='contraindications-list-create'),
    path('contraindications/<int:id>/', ContraindicationView.as_view(),
         name='contraindications-detail'),
]
