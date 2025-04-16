from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.conf import settings

from .models import (Drug,
                     DrugGroup,
                     DrugInteractionTable)
from .interaction_retriever import (InteractionRetriever,
                                    InteractionMedScape,
                                    NameDrugsMedScape,)
from .json_loader import JSONLoader
from drugs.utils.custom_response import CustomResponse


NO_DRUG = 'Не найдены данных об указанном ЛС!'


class InteractionMedScapeView(APIView):
    """
    Получение информации взаимодействии ЛС.

    Информация получена из MedScape.
    """

    def get(self, request):
        """Метод отвечающий на GET-запрос."""
        try:
            drugs = request.GET.get('drugs', '').lower()
            # classification_type = request.GET.get('classification_type', '')
            interactions = []
            # global word_count
            # word_count = {}
            if drugs:
                drugs_list = [drug.strip() for drug in drugs.split(',')]
                interactions = InteractionRetriever.get_interactions(
                    drugs_list)
            context = {
                'drugs': drugs,
                #        'classification_type': classification_type,
                'description': interactions[0]['description'],
                'compatible': interactions[0]['classification']
            }
            return CustomResponse.response(
                data=context,
                status=status.HTTP_200_OK,
                message='Совместимость ЛС по MedScape успешно расcчитана',
                http_status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return CustomResponse.response(
                status=status.HTTP_404_NOT_FOUND,
                message='Ресурс не найден',
                http_status=status.HTTP_404_NOT_FOUND)


class MedscapeOutDateView(APIView):
    """Получение списка взаимодействии ЛС."""

    def get(self, request):
        """Метод получения списка зваимодействий."""
        try:
            interactions = InteractionMedScape.objects.all().distinct(
                'classification_type_ru').order_by('classification_type_ru')
            return Response(data={'interactions': interactions},
                            status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': NO_DRUG},
                            status=status.HTTP_404_NOT_FOUND)


class InteractionMedscapeOutView(APIView):
    """Получение списка ЛС."""

    def interaction_medscape_out(self, request):
        """Метод получение списка ЛС."""
        try:
            drugs = NameDrugsMedScape.objects.all()
            Response(data={'drugs': drugs}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': NO_DRUG},
                            status=status.HTTP_404_NOT_FOUND)


class AlternativeMedscapeOutView(APIView):
    """Получение альтернативного списка ЛС."""

    @classmethod
    def get_group_drug(cls, drug):
        """
        Метод получения списка групп ЛС.

        Пустой изначально!
        ПОка ничего не делает.
        """

    def get(self, request):
        """Метод получения альтернативного списка ЛС."""
        try:
            drugs = request.GET.get('drugs', '').lower()
            if drugs:
                drugs_list = [drug.strip() for drug in drugs.split(',')]
                drugs_list = [x for x in drugs_list if x != '']
                for i in range(len(drugs_list)):
                    drug = drugs_list[i].strip()
                    group = self.get_group_drug(drug)
            return Response({'drug_group': group},
                            status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {'error': 'Не найдены данных об указанном группы ЛС!'},
                status=status.HTTP_404_NOT_FOUND)


class AllDrugTableView(APIView):
    """Работа с таблицей со всеми ЛС."""

    def post(self, request):
        """Вывод таблицы ЛС и их взаимодействия."""
        try:
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
                string_table = ('Другие взаимодействия'
                                'с лекарственным средством')
            else:
                string_table = 'Взаимодействие с лекарственным средством'
            dit = DrugInteractionTable.objects.filter(
                Q(DrugOne=selected_drug_obj.id)
                | Q(DrugTwo=selected_drug_obj.id))

            if selected_drug2 != '':
                selected_drug_obj2 = Drug.objects.get(name=selected_drug2)
                dit2 = DrugInteractionTable.objects.filter(
                    Q(DrugOne=selected_drug_obj.id,
                      DrugTwo=selected_drug_obj2.id)
                    | Q(DrugOne=selected_drug_obj2.id,
                        DrugTwo=selected_drug_obj.id))
            else:
                dit2 = {}

            Response(
                {
                    'DrugGroup': dg,
                    'sd': selected_drug,
                    'sd2': selected_drug2,
                    'Drug': dr,
                    'DrugInteractionTable': dit,
                    'DrugInteraction': dit2,
                    'StringTable': string_table,
                },
                status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {'error': NO_DRUG},
                status=status.HTTP_404_NOT_FOUND)


class LoadJSONView(APIView):
    """Загрузка данных в БД MedScape."""

    def post(self, request):
        """Метод загрузки."""
        try:
            return Response(
                {
                    'main_element': ('show_model + ',
                                     JSONLoader().load_json_Medscape(
                                         settings.BASE_DIR))
                })
        except Exception:
            return Response(
                {'error': 'Проблемы загрузки данных!'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
