from django.db.models import Q
from pharm_web.models import *



def get_group_drug(drug):
    pass

def alternative_medscape_out(request):
    drugs = request.GET.get('drugs', '').lower()
    if drugs:
        drugs_list = [drug.strip() for drug in drugs.split(',')]
        drugs_list = [x for x in drugs_list if x != '']
        for i in range(len(drugs_list)):
            drug = drugs_list[i].strip()
            group = get_group_drug(drug)
    context={'drug_group': group}
    return context
