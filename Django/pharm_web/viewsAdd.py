from django.shortcuts import redirect

from pharm_web.forms import *


def addDrugGroup(request):
    if request.method == 'POST':
        form = AddDrugGroupForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            try:
                DrugGroup.objects.create(**form.cleaned_data)
                return redirect('home')
            except:
                form.add_error(None, 'Ошибка добавления поста')
    else:
        form = AddDrugGroupForm()

    return form


def addDrug(request):
    if request.method == 'POST':
        form = AddDrugForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            try:
                DrugGroup.objects.create(**form.cleaned_data)
                return redirect('home')
            except:
                form.add_error(None, 'Ошибка добавления поста')
    else:
        form = AddDrugForm()
    return form