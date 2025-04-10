from .models import Drug, DrugGroup, SideEffect, DrugSideEffect
from .forms import UpdateSideEffectProbabilityForm, DisplaySideEffectsForm, AddSideEffect
import re


def handle_add_drug(drug_data):
    side_effects = drug_data.pop('side_effects', [])

    new_drug = Drug.objects.create(**drug_data)

    for se in side_effects:
        DrugSideEffect.objects.create(drug=new_drug, side_effect=se, probability=0.0)

    return new_drug


def handle_add_drug_group(data):
    DrugGroup.objects.create(**data)


def get_side_effects_view(request):
    form = DisplaySideEffectsForm(request.POST if request.method == 'POST' else None)

    if request.method == 'POST' and request.POST.get('form_type') == 'view_type' and form.is_valid():
        display_method = form.cleaned_data['display_method']

        if display_method == 'all':
            return "all", None, SideEffect.objects.all(), form
        try:
            drug = Drug.objects.get(id=display_method)
            side_effects = DrugSideEffect.objects.filter(drug=drug).select_related('side_effect')
            return "drug", drug, side_effects, form
        
        except Drug.DoesNotExist:
            return None, None, [], form

    return None, None, None, form


def handle_add_side_effect(request):
    if request.method == 'POST':
        form = AddSideEffect(request.POST)

        if form.is_valid():
            name = form.cleaned_data.get('name')

            if not re.search(r'[a-zA-Zа-яА-Я]', name):
                form.add_error("name", "Некорректное название побочного эффекта")
                return form
            
            new_side_effect = SideEffect.objects.create(name=name)

            for drug in Drug.objects.all():
                DrugSideEffect.objects.create(drug=drug, side_effect=new_side_effect, probability=0.0)

        return form
    
    else:
        form = AddSideEffect()

    return form


def handle_update_side_effect_probability(request, drug_id):
    if request.method == 'POST':
        form = UpdateSideEffectProbabilityForm(request.POST)

        if form.is_valid():
            side_effect_id = form.cleaned_data.get('side_effect')
            probability = form.cleaned_data.get('probability')
            print(f"Обновляем: Drug ID = {drug_id}, SE ID = {side_effect_id}, New probability = {probability}")
            
            try:
                drug = Drug.objects.get(id=drug_id)
                dse = DrugSideEffect.objects.get(drug=drug, side_effect_id=side_effect_id)

            except (Drug.DoesNotExist, DrugSideEffect.DoesNotExist):
                form.add_error(None, "Лекарство или побочный эффект не найдены")

            else:
                dse.probability = probability
                dse.save()

        return form
    
    else:
        form = UpdateSideEffectProbabilityForm()

    return form
