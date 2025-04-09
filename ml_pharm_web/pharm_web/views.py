from django.conf import settings, Settings
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.list import ListView
from django.views.decorators.http import require_GET
from django.db.models import Q

from rest_framework.generics import (ListAPIView,
                                     CreateAPIView,
                                     RetrieveUpdateAPIView)
from pharm_web.models import (MedicationSideEffect,
                              SideEffect,
                              Medication)
from pharm_web.serializers import (MedicationSideEffectSerializer,
                                   MedicationSerializer,
                                   SideEffectSerializer)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .all_drug_table_views import all_drug_table
from .iteraction_medscape import *
from .medscape_out_date import *
from .alternative_madscape import *
from .LoadJSON import load_json_Medscape
from .forms import *
from .models import *
from .viewsAdd import *
from .Fortran_to_Python_IPM import *

from pharm_web.auxiliary_module.text_getter_drugs import TextGetterDrugs
from drugs.utils.db_manipulator import DBManipulator


menu = [{'title': "Главная", 'url_name': 'home'},
        {'title': "Добавить данные", 'url_name': 'add_page'},
        ]

add_menu = [{'name_model': "Добавить группу ЛС", 'pk': "1", 'url_name': 'add_DrugGroup'},
            {'name_model': "Добавить ЛС", 'pk': "1", 'url_name': 'add_Drug'},
            {'name_model': "Изменить побочки", 'pk': "1", 'url_name': 'update_SideEffects'},
            ]

DRUGS_PATH = 'txt_files_db\\drugs_xcn.txt'

RANG_START = 0.0


def index_views(request):
    # Получаем все объекты, где is_visible=True
    ml = ml_model.objects.filter(is_visible=True)
    context = {
        'ml_model': ml,
        'menu': menu,
        'title': 'Главная страница',
        'ml_model_selected': 0,
        'main_element': 'Главная страница',
    }
    return render(request, 'pharm/index.html', context=context)


def addpage_views(request):
    context = {
        'add_element': add_menu,
        'menu': menu,
        'title': 'Добавить данные в БД',
        'add_element_selected': 0,
    }
    return render(request, 'pharm/addElementDB.html', context=context)


def aboutpage_views(request):
    context = {

    }
    return render(request, 'pharm/index.html', context=context)



def addDrugGroup_views(request):
    form = addDrugGroup(request)
    context = {
        'add_element': add_menu,
        'menu': menu,
        'form': form,
        'title': 'Добавление новой группы ЛС',
        'add_element_selected': 0,
    }
    return render(request, 'pharm/addDrugGroup.html', context=context)


def addDrug_views(request):
    form = addDrug(request)
    context = {
        'add_element': add_menu,
        'menu': menu,
        'form': form,
        'title': 'Добавление нового ЛС',
        'add_element_selected': 0,
    }
    return render(request, 'pharm/addDrugGroup.html', context=context)

def updateSideEffects_views(request):
    tipe_view, title_type_view_side_effects, side_effects, form_check_type_view,  = CheckSideEffectsView(request)
    form_add_SideEffect = AddNewSideEffect(request)
    form_add_SideEffect_rande = UpdateSeideEffectRande(request, title_type_view_side_effects)
    context = {
        'add_element': add_menu,                        # боковое меню
        'menu': menu, # Шапка сайта

        'form_check_type_view': form_check_type_view, # Форма для выбора способа отображения побочек
        "side_effects": side_effects,
        "title_type_view_side_effects": title_type_view_side_effects,
        "tipe_view": tipe_view,

        "form_add_SideEffect": form_add_SideEffect,
        "form_add_SideEffect_rande": form_add_SideEffect_rande,

        'title': 'Изменить побочки',
        'add_element_selected': 0,
    }
    return render(request, 'pharm/updateSideEffects.html', context=context)


def show_model_views(request, ml_model_slug):
    # Получаем все объекты, где is_visible=True
    ml = ml_model.objects.filter(is_visible=True)
    context = {
        'ml_model': ml,
        'menu': menu,
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


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'pharm/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'pharm/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('login')


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


def show_list_med_side_effect(request):
    """Вью отображения таблицы."""
    # print('ЛС:', list(Medication.objects.all()))
    # print('ПД:', list(SideEffect.objects.all()))
    # print('ЛС-ПД:', list(MedicationSifeEffect.objects.all()))
    return render(request, 'pharm/show_list_med_side_effect.html')


class MedicationSideEffectPagination(PageNumberPagination):
    """Класс пагинации."""

    page_size = 1000


class MedicationSideEffectListView(ListAPIView):
    """Вью для вывода списка рангов."""

    serializer_class = MedicationSideEffectSerializer
    pagination_class = MedicationSideEffectPagination

    def get_queryset(self):
        """Фильтрация по лекарству."""
        queryset = MedicationSideEffect.objects.select_related('medication',
                                                               'side_effect')
        medication_id = self.request.query_params.get('medication_id', None)

        if medication_id:
            queryset = queryset.filter(medication_id=medication_id)

        return queryset


class MedicationCreateView(CreateAPIView):
    """Вью-класс добавления лС."""

    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer

    def perform_create(self, serializer):
        """Действия выполнемые при добавлении ЛС."""
        medication = serializer.save()

        for side in SideEffect.objects.all():
            MedicationSideEffect.objects.create(
                medication=medication,
                side_effect=side,
                rang_base=RANG_START,
                rang_f1=RANG_START,
                rang_f2=RANG_START,
                rang_freq=RANG_START,
                rang_m1=RANG_START,
                rang_m2=RANG_START,
                rang_s=RANG_START
            )


class SideEffectCreateView(CreateAPIView):
    """Вью-класс добавления ПД."""

    queryset = SideEffect.objects.all()
    serializer_class = SideEffectSerializer

    def perform_create(self, serializer):
        """Действия выполняется при добавлении ПД."""
        side_effect = serializer.save()

        for med in Medication.objects.all():
            MedicationSideEffect.objects.create(
                medication=med,
                side_effect=side_effect,
                rang_base=RANG_START,
                rang_f1=RANG_START,
                rang_f2=RANG_START,
                rang_freq=RANG_START,
                rang_m1=RANG_START,
                rang_m2=RANG_START,
                rang_s=RANG_START
            )


class MedicationSideEffectDetailView(RetrieveUpdateAPIView):
    """Вью-класс редакирования рангов."""

    queryset = MedicationSideEffect.objects.all()
    serializer_class = MedicationSideEffectSerializer


class SomeApiView(APIView):
    """Вью-класс разрешения доступа для всех и ко всему."""

    permission_classes = [AllowAny]
