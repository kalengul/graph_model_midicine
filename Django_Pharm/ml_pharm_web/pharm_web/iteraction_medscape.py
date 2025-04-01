from django.db.models import Q
from pharm_web.models import *
from .GoExcel import *


def iteraction_medscape_out(request):
    drugs = Name_Drugs_MedScape.objects.all()
    context = {
        'drugs': drugs,
    }
    return context


def get_two_interactions(name, second_drug_name=None):
    drugs_info = Drugs_information_MedScape.objects.filter(
        Q(Name_Drug__Name_ru=name) | Q(Name_Drug__Name_en=name)
    )
    interactions = Interaction_MedScape.objects.filter(
        drugs_information_medscape__in=drugs_info,
    )

    if second_drug_name:
        second_drug_info = Name_Drugs_MedScape.objects.filter(
            Q(Name_ru=second_drug_name) | Q(Name_en=second_drug_name)
        )

        second_interactions = interactions.filter(interaction_with__in=second_drug_info)
    results = []

    for interaction in second_interactions:
        result = {'name': name, 'classification': interaction.classification_type_ru, 'description': interaction.description_ru}
        if second_drug_name:
            result['interaction_with'] = interaction.interaction_with.Name_ru
        else:
            result['interaction_with'] = None
        results.append(result)

        words = interaction.description_ru.split()
        for word in words:
            if word not in word_count:
                # создаем новый словарь для хранения информации о слове
                word_count[word] = {'count': 1, 'classifications': interaction.classification_type_ru}
            else:
                # увеличиваем счетчик для слова
                word_count[word]['count'] += 1

    return results


def get_interactions(drugs):
    drugs = [x for x in drugs if x != '']
    interactions = []
    for i in range(len(drugs)):
        for j in range(i + 1, len(drugs)):
            drug1 = drugs[i].strip()
            drug2 = drugs[j].strip()
            interactions.append(get_two_interactions(drug1, drug2))
    return interactions


def iteraction_medscape_two_drugs(request):
    drugs = request.GET.get('drugs', '').lower()
   # classification_type = request.GET.get('classification_type', '')
    interactions = []
    global word_count
    word_count = {}
    if drugs:
        drugs_list = [drug.strip() for drug in drugs.split(',')]
        interactions = get_interactions(drugs_list)
    context = {
        'drugs': drugs,
#        'classification_type': classification_type,
        'interactions': interactions
    }
#    print('interactions context',context)
    save_word_count_excel(word_count)
    return context
