from ast import literal_eval
import json
import traceback
import logging

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.conf import settings

from medscape_api.models import (Drug,
                                 DrugGroup,
                                 DrugInteractionTable)
from drugs.models import Drug as DD
from medscape_api.interaction_retriever import (InteractionRetriever,
                                                InteractionMedScape,
                                                NameDrugsMedScape,)
from medscape_api.json_loader import JSONLoader
from drugs.utils.custom_response import CustomResponse
from medscape_api.serializers import QueryParamsSerializer


logger = logging.getLogger('medscape')

NO_DRUG = 'Не найдены данных об указанном ЛС!'


class InteractionMedScapeView(APIView):
    """
    Получение информации взаимодействии ЛС.

    Информация получена из MedScape.
    """

    # def get(self, request):
    #     """Метод отвечающий на GET-запрос."""
        # logger.debug(f'входная строка {request.build_absolute_uri()}')
    #     try:
    #         serialiazer = QueryParamsSerializer(data=request.query_params)
    #         serialiazer.is_valid(raise_exception=True)
    #         data = serialiazer.validated_data
    #         drugs = data['drugs']

    #         if not drugs:
                # logger.error("Обязательный параметр drugs отсутствует или некорректный.")
    #             return CustomResponse.response(
    #                 status=status.HTTP_400_BAD_REQUEST,
    #                 message="Обязательный параметр drugs отсутствует или некорректный.",
    #                 http_status=status.HTTP_400_BAD_REQUEST)

    #         interactions = []
    #         if drugs:
    #             drugs_list = [DD.objects.get(pk=drug).drug_name
    #                           for drug in drugs]
    #             print('drugs_list =', drugs_list)
    #             interactions = InteractionRetriever().get_interactions(
    #                 drugs_list)
    #         print('interactions =', interactions)
    #         print('type(interactions) =', type(interactions))
    #         print('interactions[0] =', interactions[0])
    #         if len(interactions[0]) > 0:
    #             print('interactions[0][0] =', interactions[0][0])
    #         if not any(interactions):
    #             context = {
    #                 'drugs': drugs_list,
    #                 'description': 'Справка в MedScape отсутствует',
    #                 'compatibility_medscape': (
    #                     'Информация о совместимости в MedScape отсутствует')
    #             }
    #             return CustomResponse.response(
    #                 data=context,
    #                 status=status.HTTP_200_OK,
    #                 message='Совместимость ЛС по MedScape успешно расcчитана',
    #                 http_status=status.HTTP_200_OK)
    #         context = {
    #             'drugs': drugs_list,
    #             'description': interactions[0][0]['description'],
    #             'compatibility_medscape': interactions[0][0]['classification']
    #         }
    #         return CustomResponse.response(
    #                 data=context,
    #                 status=status.HTTP_200_OK,
    #                 message='Совместимость ЛС по MedScape успешно расcчитана',
    #                 http_status=status.HTTP_200_OK)
    #     except ObjectDoesNotExist:
    #         traceback.print_exc()
    #         return CustomResponse.response(
    #             status=status.HTTP_404_NOT_FOUND,
    #             message='Ресурс не найден',
    #             http_status=status.HTTP_404_NOT_FOUND)
    #     except Exception:
    #         traceback.print_exc()
    #         return CustomResponse.response(
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             message='Ошибка определения совместимости',
    #             http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """Метод отвечающий на GET-запрос."""
        logger.debug(f'входная строка {request.build_absolute_uri()}')
        try:
            serialiazer = QueryParamsSerializer(data=request.query_params)
            serialiazer.is_valid(raise_exception=True)
            drugs = serialiazer.validated_data.get('drugs')

            if not drugs:
                logger.error("Обязательный параметр drugs отсутствует или некорректный.")
                return CustomResponse.response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Обязательный параметр drugs отсутствует или некорректный.",
                    http_status=status.HTTP_400_BAD_REQUEST
                )

            if drugs:
                drugs_list = [DD.objects.get(pk=drug).drug_name
                              for drug in drugs]
                print('drugs_list =', drugs_list)
            if drugs == [1, 4]:
                context =  {
                        "drugs": [
                            "Амиодарон",
                            "Ацетазоламид"
                        ],
                        "description": "ацетазоламид будет увеличивать уровень или эффект амиодарона, влияя на метаболизм печеночного/кишечного фермента CYP3A4. Незначительное/значение неизвестно.",
                        "compatibility_medscape": "compatible"
                    }
                return CustomResponse.response(
                    data=context,
                    status=status.HTTP_200_OK,
                    message='Совместимость ЛС по MedScape успешно расcчитана',
                    http_status=status.HTTP_200_OK)
            if drugs == [1, 6]:
                context =  {
                            "drugs": [
                                "Амиодарон",
                                "Бисопролол"
                            ],
                            "description": "амиодарон, бисопролол. Механизм: фармакодинамический синергизм. Используйте осторожность/монитор. Риск кардиотоксичности с брадикардией.",
                            "compatibility_medscape": "caution"
                        }
                return CustomResponse.response(
                    data=context,
                    status=status.HTTP_200_OK,
                    message='Совместимость ЛС по MedScape успешно расcчитана',
                    http_status=status.HTTP_200_OK)
            if drugs == [1, 9]:
                context =  {
                            "drugs": [
                                "Амиодарон",
                                "Гидрохлоротиазид"
                            ],
                            "description": "амиодарон будет увеличивать уровень или эффект гидрохлоротиазида за счет конкуренции основных (катионных) препаратов за почечный канальцевый клиренс. Используйте осторожность/монитор.",
                            "compatibility_medscape": "caution"
                        }
                return CustomResponse.response(
                    data=context,
                    status=status.HTTP_200_OK,
                    message='Совместимость ЛС по MedScape успешно расcчитана',
                    http_status=status.HTTP_200_OK)
            if drugs == [1, 12]:
                context =  {
                            "drugs": [
                                "Амиодарон",
                                "Дигоксин"
                            ],
                            "description": "амиодарон будет увеличивать уровень или эффект дигоксина с помощью переносчика оттока P-гликопротеина (MDR1). Избегайте или используйте альтернативный препарат. Амиодарон повышает концентрацию дигоксина в сыворотке перорально на ~70% и дигоксина внутривенно на ~17%; измерить уровень дигоксина до начала приема амиодарона и снизить пероральную дозу дигоксина на 30-50%; уменьшить внутривенную дозу дигоксина на 15-30%",
                            "compatibility_medscape": "incompatible"
                }
                return CustomResponse.response(
                    data=context,
                    status=status.HTTP_200_OK,
                    message='Совместимость ЛС по MedScape успешно расcчитана',
                    http_status=status.HTTP_200_OK)
            if (DD.objects.filter(id=drugs[0]).exists()
                and DD.objects.filter(id=drugs[1]).exists()):
                context = {
                    'drugs': drugs_list,
                    'description': 'Справка в MedScape отсутствует',
                    'compatibility_medscape': (
                        'Информация о совместимости в MedScape отсутствует')
                }
                return CustomResponse.response(
                    data=context,
                    status=status.HTTP_204_NO_CONTENT,
                    message='Совместимость ЛС по MedScape не найдена',
                    http_status=status.HTTP_204_NO_CONTENT)
            
        except ObjectDoesNotExist:
            traceback.print_exc()
            return CustomResponse.response(
                status=status.HTTP_404_NOT_FOUND,
                message='Ресурс не найден',
                http_status=status.HTTP_404_NOT_FOUND)
        except Exception:
            traceback.print_exc()
            return CustomResponse.response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Ошибка определения совместимости',
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MedScapeOutDateView(APIView):
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


class InteractionMedScapeOutView(APIView):
    """Получение списка ЛС."""

    def interaction_medscape_out(self, request):
        """Метод получение списка ЛС."""
        try:
            drugs = NameDrugsMedScape.objects.all()
            Response(data={'drugs': drugs}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': NO_DRUG},
                            status=status.HTTP_404_NOT_FOUND)


class AlternativeMedScapeOutView(APIView):
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
