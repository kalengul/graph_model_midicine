from django.urls import path
from .views import (SynonymGroupAPI, SynonymListAPI, LoadSynonymView)


urlpatterns = [
    path('getSynonymGroups/', SynonymGroupAPI.as_view(), name='get_synonym_groups'),
    path('getSynonymList/', SynonymListAPI.as_view(), name='get_synonym_list'),
    path('updateSynonymList/', SynonymListAPI.as_view(), name='update_synonym_list'),
    path('createSynonym/', SynonymListAPI.as_view(), name='create_synonym'),

    path('import_synonyms/', LoadSynonymView.as_view(), name='import_synonyms'),
    path('export_synonyms/', LoadSynonymView.as_view(), name='export_synonyms'),
]
