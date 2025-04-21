from django.urls import path
from .views import (InteractionMedScapeView,
                    MedscapeOutDateView,
                    InteractionMedscapeOutView,
                    AlternativeMedscapeOutView,
                    AllDrugTableView,
                    LoadJSONView)


urlpatterns = [
    path('iteraction_medscape/',
         InteractionMedScapeView.as_view(),
         name='interaction_medscape'),
    path('medscape_out_date/',
         MedscapeOutDateView.as_view(),
         name='medscape_out_date'),
    path('interaction_medscape_out/',
         InteractionMedscapeOutView.as_view(),
         name='interaction_medscape_out'),
    path('alternative_medscape_out/',
         AlternativeMedscapeOutView.as_view(),
         name='alternative_medscape_out'),
    path('all_drug_table', AllDrugTableView.as_view(), name='all_drug_table'),
    path('load_json', LoadJSONView.as_view(), name='load_json'),
]
