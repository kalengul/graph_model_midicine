import re

from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.http import HttpResponse

from .forms import *
from .models import *
from . import services
from .db_manipulator import DBManipulator

add_menu = [
    {'name_model': "Добавить группу ЛС", 'pk': "1", 'url_name': 'add_DrugGroup'},
    {'name_model': "Добавить ЛС", 'pk': "1", 'url_name': 'add_Drug'},
    {'name_model': "Изменить побочки", 'pk': "1", 'url_name': 'update_SideEffects'},
]


@staff_member_required
def addpage_views(request):
    context = {
        'add_element': add_menu,
        'title': 'Добавить данные в БД',
        'add_element_selected': 0,
    }
    return render(request, 'drugs/addElementDB.html', context)


@staff_member_required
def add_drug_views(request):
    if request.method == 'POST':
        form = AddDrugForm(request.POST)
        if form.is_valid():
            # try:
            services.handle_add_drug(form.cleaned_data)
            return redirect('home')
            # except Exception as e:
            #     form.add_error(None, f'Ошибка добавления ЛС: {e}')
    else:
        form = AddDrugForm()

    context = {
        'form': form,
        'title': 'Добавление нового ЛС',
        'add_element': add_menu,
        'add_element_selected': 0,
        'form_action': reverse('add_Drug'),
    }
    return render(request, 'drugs/addDrugGroup.html', context=context)


@staff_member_required
def add_drugGroup_views(request):
    if request.method == 'POST':
        form = AddDrugGroupForm(request.POST)
        if form.is_valid():
            try:
                services.handle_add_drug_group(form.cleaned_data)
                return redirect('home')
            except Exception as e:
                form.add_error(None, f'Ошибка добавления группы ЛС: {e}')
    else:
        form = AddDrugGroupForm()

    context = {
        'form': form,
        'title': 'Добавление новой группы ЛС',
        'add_element': add_menu,
        'add_element_selected': 0,
        'form_action': reverse('add_DrugGroup'),
    }
    return render(request, 'drugs/addDrugGroup.html', context=context)


@staff_member_required
def updateSideEffects_views(request):
    tipe_view, data_obj, side_effects, form_check = services.get_side_effects_view(request)
    
    context = {
        'form_check_type_view': form_check,
        'side_effects': side_effects,
        'title_type_view_side_effects': data_obj.name if tipe_view == 'drug' and data_obj else "Побочные эффекты",
        'tipe_view': tipe_view,
        'form_add_SideEffect': AddSideEffect(), 
        'form_add_SideEffect_rande': UpdateSideEffectProbabilityForm(),  
        'title': 'Изменить побочки',
        'add_element': add_menu,
        'add_element_selected': 0,
    }
    
    return render(request, 'drugs/updateSideEffects.html', context)


@staff_member_required
def list_side_effects_view(request):
    form_check_type_view = DisplaySideEffectsForm(request.POST or None)
    tipe_view = None
    data_obj = None
    side_effects = None

    if request.method == 'POST' and form_check_type_view.is_valid():
        display_method = form_check_type_view.cleaned_data['display_method']
        if display_method == 'all':
            tipe_view = "all"
            side_effects = SideEffect.objects.all()
        else:
            try:
                drug = Drug.objects.get(id=display_method)
                tipe_view = "drug"
                data_obj = drug
                side_effects = DrugSideEffect.objects.filter(drug=drug).select_related('side_effect')
            except Drug.DoesNotExist:
                form_check_type_view.add_error(None, "Лекарство не найдено")

    context = {
        'form_check_type_view': form_check_type_view,
        'tipe_view': tipe_view,
        'data_obj': data_obj,
        'side_effects': side_effects,
        'form_add_SideEffect': AddSideEffect(),  
        'form_add_SideEffect_rande': UpdateSideEffectProbabilityForm(), 
        'title': 'Побочные эффекты',
        'title_type_view_side_effects': "Побочные эффекты" if tipe_view == "all" else data_obj.name if data_obj else "",
    }

    return render(request, 'drugs/updateSideEffects.html', context)


@staff_member_required
def add_side_effect_view(request):
    if request.method == 'POST':
        form = AddSideEffect(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            if not re.search(r'[a-zA-Zа-яА-Я]', name):
                form.add_error("name", "Некорректное название побочного эффекта")
            else:
                new_se = SideEffect.objects.create(name=name)
                for drug in Drug.objects.all():
                    DrugSideEffect.objects.create(drug=drug, side_effect=new_se, probability=0.0)
                return redirect('side_effects_list')
    else:
        form = AddSideEffect()

    context = {
        'form_check_type_view': DisplaySideEffectsForm(),
        'tipe_view': 'all',
        'data_obj': None,
        'side_effects': SideEffect.objects.all(),
        'form_add_SideEffect': form,
        'form_add_SideEffect_rande': UpdateSideEffectProbabilityForm(),
        'title': 'Побочные эффекты',
        'title_type_view_side_effects': "Побочные эффекты",
    }

    return render(request, 'drugs/updateSideEffects.html', context)


@staff_member_required
def update_side_effect_view(request, drug_id):
    try:
        drug = Drug.objects.get(id=drug_id)
        side_effects_qs = DrugSideEffect.objects.filter(drug=drug).select_related('side_effect')
    except Drug.DoesNotExist:
        return redirect('side_effects_list')

    if request.method == 'POST':
        form = UpdateSideEffectProbabilityForm(request.POST)
        if form.is_valid():
            side_effect_id = form.cleaned_data.get('side_effect')
            probability = form.cleaned_data.get('probability')
            try:
                dse = DrugSideEffect.objects.get(drug=drug, side_effect_id=side_effect_id)
                dse.probability = probability
                dse.save()
                return redirect('side_effects_update', drug_id=drug.id)
            except DrugSideEffect.DoesNotExist:
                form.add_error(None, "Побочный эффект не найден")
    else:
        form = UpdateSideEffectProbabilityForm()

    context = {
        'form_check_type_view': DisplaySideEffectsForm(initial={'display_method': str(drug.id)}),
        'tipe_view': 'drug',
        'data_obj': drug,
        'side_effects': side_effects_qs,
        'form_add_SideEffect': AddSideEffect(),
        'form_add_SideEffect_rande': form,
        'title': 'Побочные эффекты',
        'title_type_view_side_effects': drug.name,
    }
    return render(request, 'drugs/updateSideEffects.html', context)


def load_to_db(request):
    """Вью-функция импорта данных из файлов в БД."""
    try:
        rangs_count = DBManipulator().load_to_db()
        return HttpResponse(('Данные из файлов импортированы успешно!'
                             f'Рангов {rangs_count}'))
    except Exception as error:
        return HttpResponse(('При импортировании данных возника ошибка:'
                             f'{error}'))


def clean_db(request):
    """
    Вью-функция очистки таблиц БД.

    Очищаются таблицы:
        - Medication;
        - SifeEffect;
        - MedicationSifeEffect.
    """
    try:
        DBManipulator().clean_db()
        return HttpResponse('Очистка таблиц прошла успешно!')
    except Exception as error:
        return HttpResponse(('При очистке БД возника ошибка:'
                             f'{error}'))
