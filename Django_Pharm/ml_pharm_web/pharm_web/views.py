from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.db.models import Q

from .all_drug_table_views import all_drug_table
from .iteraction_medscape import *
from .medscape_out_date import *
from .alternative_madscape import *
from .LoadJSON import load_json_Medscape
from .forms import *
from .models import *
from .viewsAdd import *
from .Fortran_to_Python_IPM import *
from drugs.models import Drug
from pharm_web.auxiliary_module.text_getter_drugs import TextGetterDrugs


def get_menu_for_user(user):
    menu = [{'title': "Главная", 'url_name': 'home'}]
    
    if user.is_authenticated and user.is_staff:
        menu.append({'title': "Добавить данные", 'url_name': 'add_page'})
    
    return menu


DRUGS_PATH = 'txt_files_db\\drugs_xcn.txt'


def index_views(request):
    # Получаем все объекты, где is_visible=True
    ml = ml_model.objects.filter(is_visible=True)
    context = {
        'ml_model': ml,
        'menu': get_menu_for_user(request.user),
        'title': 'Главная страница',
        'ml_model_selected': 0,
        'main_element': 'Главная страница',
    }
    return render(request, 'pharm/index.html', context=context)


def aboutpage_views(request):
    context = {

    }
    return render(request, 'pharm/index.html', context=context)


def show_model_views(request, ml_model_slug):
    # Получаем все объекты, где is_visible=True
    ml = ml_model.objects.filter(is_visible=True)
    context = {
        'ml_model': ml,
        'menu': get_menu_for_user(request.user),
        'title': 'Главная страница',
        'main_element': 'show_model + ' + ml_model_slug,
    }

    if ml_model_slug == 'test-model':
        return render(request, 'pharm/index.html', context=context)

    elif ml_model_slug == 'vyvod-tablichki':
        context.update(all_drug_table(request))
        return render(request, 'pharm/vyvod-tablichki.html', context=context)

    elif ml_model_slug == 'zagruzka-dannyh-iz-medscape':
        s = load_json_Medscape(settings.BASE_DIR)
        context = {
            'main_element': 'show_model + ' + ml_model_slug + ' ' + s,
        }
        return render(request, 'pharm/index.html', context=context)

    elif ml_model_slug == 'iteraction_MedScape':
        context.update(iteraction_medscape_out(request))
        context.update(iteraction_medscape_two_drugs(request))
        return render(request, 'pharm/iterction_medscape.html', context=context)

    elif ml_model_slug == 'alternative-medscape':
        context.update(alternative_medscape_out(request))
        return render(request, 'pharm/iterction_medscape.html', context=context)

    elif ml_model_slug == 'vyvesti-dannye-medscape':
        context.update(medscape_out_date(request))
        return render(request, 'pharm/vivod_medscape.html', context=context)
    elif ml_model_slug == 'polifarmakoterapiya-fortran':
        context.update({'polypharma_files': files_all_iteractions})
        context.update(go_all_iteractions(request,settings.BASE_DIR))
        context.update(iteraction_medscape_out(request))
        context.update(iteraction_medscape_two_drugs(request))
        return render(request, 'pharm/iterction_polipharma.html', context=context)
    else:
        return render(request, 'pharm/index.html', context=context)


@require_GET
def search_drugs(request):
    # Получаем значение из параметра "q" в запросе
    query = request.GET.get('q')
    # Разделяем строку по запятой, чтобы получить отдельные названия препаратов
    drug_names = query.split(', ')
    # Создаем список с названиями препаратов и их id
    drugs = []
    #print('drug_names', drug_names)
    name=drug_names[-1]
#    for name in drug_names:
        # Ищем препараты, содержащие в названии введенное значение
    drug = Name_Drugs_MedScape.objects.filter(Q(Name_ru__startswith=name) | Q(Name_en__startswith=name))
    #print('drug', drug)
    for drug_el in drug:
        # Создаем список с названиями препаратов
        drugs.append({'id': drug_el.id, 'name': drug_el.Name_ru})
    # Возвращаем список в формате JSON
    return JsonResponse({'drugs': drugs})


@require_GET
def search_polipharma_drugs(request):
    # Получаем значение из параметра "q" в запросе
    query = request.GET.get('q')
    # Разделяем строку по запятой, чтобы получить отдельные названия препаратов
    drug_names = query.split(', ')
    # Создаем список с названиями препаратов и их id
    drugs = []
    #print('drug_names', drug_names)
    name = drug_names[-1].strip()  # Убираем пробелы
    #print('Searching for:', name)
    # Ищем препараты, содержащие в названии введенное значение
    drug = drugs_chf.objects.filter(name__icontains=name)
    #print('drug', drug)

    for drug_el in drug:
        # Создаем список с названиями препаратов
        drugs.append({'index': drug_el.index, 'name': drug_el.name})
    # Возвращаем список в формате JSON
    return JsonResponse({'drugs': drugs})


def finding_matches(request):
    """
    Вью-функция для сопосталения ЛС из файли и БД.

    Вспомогательная функция.
    Кандидат на удаление.
    """
    print('Drug.objects.all() =', Drug.objects.count())
    db_drug_names = [drug.name for drug in Drug.objects.all()]
    txt_drug_names = TextGetterDrugs(DRUGS_PATH).get_drug_names()
    identical = set(db_drug_names) & set(txt_drug_names)
    different = set(db_drug_names) ^ set(txt_drug_names)
    return JsonResponse({'Названий ЛС в БД': len(db_drug_names),
                         'Одинаковых элементов': len(identical),
                         'Разные': len(different),
                         'ЛС из БД': db_drug_names,
                         'ЛС из файла': txt_drug_names},
                        json_dumps_params={'ensure_ascii': False,
                                           'indent': 4})
