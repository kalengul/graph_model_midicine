from django.db.models import Q
from pharm_web.models import *

def medscape_out_date(request):
    interactions = Interaction_MedScape.objects.all().distinct('classification_type_ru').order_by('classification_type_ru')
    print(interactions)
    context = {
        'interactions': interactions
    }
    return context