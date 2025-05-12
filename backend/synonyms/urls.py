from django.urls import path
from .views import (SynonymGroupAPI, SynonymListAPI)


urlpatterns = [
    path('getSynonymGroups/', SynonymGroupAPI.as_view(), name='get_synonym_groups'),
    path('getSynonymList/', SynonymListAPI.as_view(), name='get_synonym_list'),
    path('updateSynonymList/', SynonymListAPI.as_view(), name='update_synonym_list'),
]
