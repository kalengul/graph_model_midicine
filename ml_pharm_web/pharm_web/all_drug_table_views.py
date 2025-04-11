from django.db.models import Q
from pharm_web.models import *


def all_drug_table(request):
    dg = DrugGroup.objects.all()
    dr = Drug.objects.all()
    dit = {}
    string_table = ''
    selected_drug2 = ''
    if request.method == 'POST':
        selected_drug = request.POST.get('selected_drug')
        selected_drug2 = request.POST.get('selected_drug2')
    else:
        selected_drug = 'Амиодарон'

    selected_drug_obj = Drug.objects.get(name=selected_drug)
    if selected_drug2 != '':
        string_table = 'Другие взаимодействия с лекарственным средством'
    else:
        string_table = 'Взаимодействие с лекарственным средством'
    dit = DrugInteractionTable.objects.filter(Q(DrugOne=selected_drug_obj.id) | Q(DrugTwo=selected_drug_obj.id))

    if selected_drug2 != '':
        selected_drug_obj2 = Drug.objects.get(name=selected_drug2)
        dit2 = DrugInteractionTable.objects.filter(
            Q(DrugOne=selected_drug_obj.id, DrugTwo=selected_drug_obj2.id) | Q(DrugOne=selected_drug_obj2.id,
                                                                               DrugTwo=selected_drug_obj.id))
    else:
        dit2 = {}

    context = {
        'DrugGroup': dg,
        'sd': selected_drug,
        'sd2': selected_drug2,
        'Drug': dr,
        'DrugInteractionTable': dit,
        'DrugInteraction': dit2,
        'StringTable': string_table,
    }
    return context
