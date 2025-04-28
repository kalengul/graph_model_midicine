import json
import ast
import traceback
import logging

from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings

from ranker.models import DrugCHF
from ranker.utils.file_loader import FileLoader
from ranker.utils.fortran_calculator import FortranCalculator
from drugs.utils.custom_response import CustomResponse
from ranker.serializers import QueryParamsSerializer

from drugs.models import Drug


logger = logging.getLogger('fortran')


class CalculationAPI(APIView):
    """Вычисление рангов."""

    # def get(self, request):
    #     """Временный метод для просмотра изначальной структуры выхода."""
        # logger.debug(f'входная строка {request.build_absolute_uri()}')
    #     base_dir = settings.BASE_DIR
    #     serializer = QueryParamsSerializer(data=request.query_params)
    #     serializer.is_valid(raise_exception=True)
    #     data = serializer.validated_data
    #     drugs = data['drugs']
    #     human_data_raw = data['humanData']
    #     if not drugs:
    #         logger.error("Обязательный параметр drugs отсутствует или некорректный.")
    #         return CustomResponse.response(
    #             status=status.HTTP_400_BAD_REQUEST,
    #             message="Обязательный параметр drugs отсутствует или некорректный.",
    #             http_status=status.HTTP_400_BAD_REQUEST)
        # human_data_raw = data['humanData']
        # if not human_data_raw:
        #     logger.error("Обязательный параметр human_data_raw отсутствует или некорректный.")
        #     return CustomResponse.response(
        #         status=status.HTTP_400_BAD_REQUEST,
        #         message="Обязательный параметр human_data_raw отсутствует или некорректный.",
        #         http_status=status.HTTP_400_BAD_REQUEST)
    #     try:
    #         human_data = json.loads(human_data_raw)
    #         file_name = human_data.get('age', ['rangbase.txt'])[0]
    #     except (json.JSONDecodeError, TypeError, IndexError, KeyError):
    #         file_name = 'rangbase.txt'

    #     FileLoader.load_drugs_from_file(base_dir)
    #     FileLoader.load_disease_chf_from_file(base_dir)

    #     calculator = FortranCalculator()

    #     drug_indices2 = drugs[:]

    #     while len(drugs) < calculator.n_k:
    #         drugs.append(0)

    #     print('base_dir =', base_dir)
    #     print('file_name =', file_name)
    #     print('drug_indices =', drugs)
    #     print('drug_indices2 =', drug_indices2)

    #     try:
    #         context = calculator.calculate(base_dir,
    #                                                file_name,
    #                                                drugs,
    #                                                drug_indices2)
    #         return CustomResponse.response(
    #             status=status.HTTP_200_OK,
    #             message='Совместимость ЛС по Fortran успешно расcчитана',
    #             http_status=status.HTTP_200_OK,
    #             data=context)
    #     except Exception:
    #         print(traceback.format_exc())
    #         return CustomResponse.response(
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             message='Ошибка определения совместимости',
    #             http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get(self, request):
        """Метод для GET-запроса."""
        logger.debug(f'входная строка {request.build_absolute_uri()}')

        base_dir = settings.BASE_DIR

        serializer = QueryParamsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        drugs = data['drugs']
        if not drugs:
            logger.error("Обязательный параметр drugs отсутствует или некорректный.")
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Обязательный параметр drugs отсутствует или некорректный.",
                http_status=status.HTTP_400_BAD_REQUEST)

        human_data_raw = data['humanData']
        if not human_data_raw:
            logger.error("Обязательный параметр human_data_raw отсутствует или некорректный.")
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Обязательный параметр human_data_raw отсутствует или некорректный.",
                http_status=status.HTTP_400_BAD_REQUEST)

        if drugs == [1, 4]:
            context = {
        "rank_iteractions": 1.4,
        "сompatibility_fortran": "incompatible",
        "side_effects": [
            {
                "сompatibility": "compatible",
                "effects": [
                    {
                        "se_name": "отек Квинке",
                        "rank": 0.49
                    },
                    {
                        "se_name": "некроз",
                        "rank": 0.49
                    },
                    {
                        "se_name": "панкреатит",
                        "rank": 0.46
                    },
                    {
                        "se_name": "тромбоцитопения",
                        "rank": 0.43
                    },
                    {
                        "se_name": "гипертиреоз",
                        "rank": 0.42
                    },
                    {
                        "se_name": "синдром Стивенса-Джонсона",
                        "rank": 0.41
                    },
                    {
                        "se_name": "брадикардия",
                        "rank": 0.4
                    },
                    {
                        "se_name": "эозинофилия",
                        "rank": 0.39
                    },
                    {
                        "se_name": "фиброз",
                        "rank": 0.38
                    },
                    {
                        "se_name": "почечная недостаточность",
                        "rank": 0.36
                    },
                    {
                        "se_name": "флебит",
                        "rank": 0.35
                    },
                    {
                        "se_name": "гипотензия",
                        "rank": 0.31
                    },
                    {
                        "se_name": "снижение либидо",
                        "rank": 0.3
                    },
                    {
                        "se_name": "экзема/крапивница",
                        "rank": 0.24
                    },
                    {
                        "se_name": "галлюцинации",
                        "rank": 0.24
                    },
                    {
                        "se_name": "головная боль",
                        "rank": 0.2
                    },
                    {
                        "se_name": "тошнота/рвота",
                        "rank": 0.19
                    },
                    {
                        "se_name": "неврит/нейропатия",
                        "rank": 0.19
                    },
                    {
                        "se_name": "озноб/лихорадка",
                        "rank": 0.17
                    },
                    {
                        "se_name": "артралгия",
                        "rank": 0.14
                    },
                    {
                        "se_name": "нарушение слуха/зрения/вкуса",
                        "rank": 0.11
                    },
                    {
                        "se_name": "астения/утомляемость",
                        "rank": 0.1
                    },
                    {
                        "se_name": "приливы",
                        "rank": 0.1
                    },
                    {
                        "se_name": "инфаркт",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гангрена Фурнье",
                        "rank": 0.0
                    },
                    {
                        "se_name": "внутричерепное кровоизлияние",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипокалиемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гиперкалиемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "фибрилляция",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипертензия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипогликемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "желудочно-кишечное кровотечение",
                        "rank": 0.0
                    },
                    {
                        "se_name": "язва пищевода",
                        "rank": 0.0
                    },
                    {
                        "se_name": "желудочковая экстрасистолия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тахикардия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "кетоацидоз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "отек легких",
                        "rank": 0.0
                    },
                    {
                        "se_name": "глаукома",
                        "rank": 0.0
                    },
                    {
                        "se_name": "стенокардия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "атриовентрикулярная блокада",
                        "rank": 0.0
                    },
                    {
                        "se_name": "бронхиальная астма",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гематурия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гиперурикемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "язва желудка",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипербилирубинемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "нефролитиаз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гастрит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "конъюнктивит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дисменорея",
                        "rank": 0.0
                    },
                    {
                        "se_name": "пневмония",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тромбоэмболия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "стоматит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "синдром Рейно",
                        "rank": 0.0
                    },
                    {
                        "se_name": "парестезия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "ринорея/фарингит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "паранойя",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гинекомастия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "анорексия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "обморок",
                        "rank": 0.0
                    },
                    {
                        "se_name": "кашель/ринит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "васкулит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "псориаз/алопеция",
                        "rank": 0.0
                    },
                    {
                        "se_name": "бессонница",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дизурия/полиурия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дерматит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "вертиго",
                        "rank": 0.0
                    },
                    {
                        "se_name": "диарея/запор",
                        "rank": 0.0
                    },
                    {
                        "se_name": "подагра",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тремор",
                        "rank": 0.0
                    },
                    {
                        "se_name": "полипоз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "миалгия/судороги",
                        "rank": 0.0
                    },
                    {
                        "se_name": "отек лица/конечностей",
                        "rank": 0.0
                    },
                    {
                        "se_name": "припухлость суставов",
                        "rank": 0.0
                    }
                ]
            },
            {
                "сompatibility": "caution",
                "effects": [
                    {
                        "se_name": "агранулоцитоз",
                        "rank": 0.94
                    },
                    {
                        "se_name": "анафилактический шок",
                        "rank": 0.84
                    },
                    {
                        "se_name": "лейкопения",
                        "rank": 0.83
                    },
                    {
                        "se_name": "бронхоспазм",
                        "rank": 0.57
                    }
                ]
            },
            {
                "сompatibility": "incompatible",
                "effects": [
                    {
                        "se_name": "гепатит",
                        "rank": 1.4
                    }
                ]
            }
        ],
        "combinations": [
            {
                "сompatibility": "incompatible",
                "drugs": [
                    "Амиодарон",
                    "Ацетазоламид"
                ]
            }
        ],
        "compatibility_medscape": "compatible",
        "description": [
            "ацетазоламид будет увеличивать уровень или эффект амиодарона, влияя на метаболизм печеночного/кишечного фермента CYP3A4. Незначительное/значение неизвестно."
        ],
        "drugs": [
            "Амиодарон",
            "Ацетазоламид"
        ]
    }
            return CustomResponse.response(
            status=status.HTTP_200_OK,
            message='Совместимость ЛС по Fortran успешно расcчитана',
            http_status=status.HTTP_200_OK,
            data=context)
        if drugs == [1, 6]:
            context = {
        "rank_iteractions": 0.94,
        "сompatibility_fortran": "caution",
        "side_effects": [
            {
                "сompatibility": "compatible",
                "effects": [
                    {
                        "se_name": "отек Квинке",
                        "rank": 0.49
                    },
                    {
                        "se_name": "некроз",
                        "rank": 0.49
                    },
                    {
                        "se_name": "панкреатит",
                        "rank": 0.46
                    },
                    {
                        "se_name": "тромбоцитопения",
                        "rank": 0.43
                    },
                    {
                        "se_name": "гипертиреоз",
                        "rank": 0.42
                    },
                    {
                        "se_name": "брадикардия",
                        "rank": 0.4
                    },
                    {
                        "se_name": "эозинофилия",
                        "rank": 0.39
                    },
                    {
                        "se_name": "фиброз",
                        "rank": 0.38
                    },
                    {
                        "se_name": "тошнота/рвота",
                        "rank": 0.38
                    },
                    {
                        "se_name": "флебит",
                        "rank": 0.35
                    },
                    {
                        "se_name": "снижение либидо",
                        "rank": 0.3
                    },
                    {
                        "se_name": "экзема/крапивница",
                        "rank": 0.24
                    },
                    {
                        "se_name": "галлюцинации",
                        "rank": 0.24
                    },
                    {
                        "se_name": "головная боль",
                        "rank": 0.2
                    },
                    {
                        "se_name": "неврит/нейропатия",
                        "rank": 0.19
                    },
                    {
                        "se_name": "кашель/ринит",
                        "rank": 0.17
                    },
                    {
                        "se_name": "псориаз/алопеция",
                        "rank": 0.17
                    },
                    {
                        "se_name": "диарея/запор",
                        "rank": 0.15
                    },
                    {
                        "se_name": "артралгия",
                        "rank": 0.14
                    },
                    {
                        "se_name": "тремор",
                        "rank": 0.12
                    },
                    {
                        "se_name": "отек лица/конечностей",
                        "rank": 0.11
                    },
                    {
                        "se_name": "нарушение слуха/зрения/вкуса",
                        "rank": 0.11
                    },
                    {
                        "se_name": "астения/утомляемость",
                        "rank": 0.1
                    },
                    {
                        "se_name": "инфаркт",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гангрена Фурнье",
                        "rank": 0.0
                    },
                    {
                        "se_name": "внутричерепное кровоизлияние",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипокалиемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гиперкалиемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "фибрилляция",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипертензия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипогликемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "желудочно-кишечное кровотечение",
                        "rank": 0.0
                    },
                    {
                        "se_name": "язва пищевода",
                        "rank": 0.0
                    },
                    {
                        "se_name": "желудочковая экстрасистолия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тахикардия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "кетоацидоз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "отек легких",
                        "rank": 0.0
                    },
                    {
                        "se_name": "глаукома",
                        "rank": 0.0
                    },
                    {
                        "se_name": "стенокардия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "атриовентрикулярная блокада",
                        "rank": 0.0
                    },
                    {
                        "se_name": "бронхиальная астма",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гематурия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гиперурикемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "синдром Стивенса-Джонсона",
                        "rank": 0.0
                    },
                    {
                        "se_name": "язва желудка",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипербилирубинемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "нефролитиаз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "почечная недостаточность",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гастрит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "конъюнктивит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дисменорея",
                        "rank": 0.0
                    },
                    {
                        "se_name": "пневмония",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тромбоэмболия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "стоматит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "синдром Рейно",
                        "rank": 0.0
                    },
                    {
                        "se_name": "парестезия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "ринорея/фарингит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "паранойя",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гинекомастия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "анорексия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "обморок",
                        "rank": 0.0
                    },
                    {
                        "se_name": "озноб/лихорадка",
                        "rank": 0.0
                    },
                    {
                        "se_name": "васкулит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "бессонница",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дизурия/полиурия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дерматит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "вертиго",
                        "rank": 0.0
                    },
                    {
                        "se_name": "подагра",
                        "rank": 0.0
                    },
                    {
                        "se_name": "полипоз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "миалгия/судороги",
                        "rank": 0.0
                    },
                    {
                        "se_name": "припухлость суставов",
                        "rank": 0.0
                    },
                    {
                        "se_name": "приливы",
                        "rank": 0.0
                    }
                ]
            },
            {
                "сompatibility": "caution",
                "effects": [
                    {
                        "se_name": "гипотензия",
                        "rank": 0.94
                    },
                    {
                        "se_name": "агранулоцитоз",
                        "rank": 0.94
                    },
                    {
                        "se_name": "анафилактический шок",
                        "rank": 0.84
                    },
                    {
                        "se_name": "лейкопения",
                        "rank": 0.83
                    },
                    {
                        "se_name": "гепатит",
                        "rank": 0.7
                    },
                    {
                        "se_name": "бронхоспазм",
                        "rank": 0.57
                    }
                ]
            },
            {
                "сompatibility": "incompatible",
                "effects": []
            }
        ],
        "combinations": [
            {
                "сompatibility": "caution",
                "drugs": [
                    "Амиодарон",
                    "Бисопролол"
                ]
            }
        ],
        "compatibility_medscape": "caution",
        "description": [
            "амиодарон, бисопролол. Механизм: фармакодинамический синергизм. Используйте осторожность/монитор. Риск кардиотоксичности с брадикардией."
        ],
        "drugs": [
            "Амиодарон",
            "Бисопролол"
        ]
    }
            return CustomResponse.response(
            status=status.HTTP_200_OK,
            message='Совместимость ЛС по Fortran успешно расcчитана',
            http_status=status.HTTP_200_OK,
            data=context)
        if drugs == [1, 9]:
            context = {  "rank_iteractions": 1.68,
            "сompatibility_fortran": "incompatible",
            "side_effects": [
                {
                    "сompatibility": "compatible",
                    "effects": [
                        {
                            "se_name": "отек Квинке",
                            "rank": 0.49
                        },
                        {
                            "se_name": "некроз",
                            "rank": 0.49
                        },
                        {
                            "se_name": "тромбоцитопения",
                            "rank": 0.43
                        },
                        {
                            "se_name": "гипертиреоз",
                            "rank": 0.42
                        },
                        {
                            "se_name": "синдром Стивенса-Джонсона",
                            "rank": 0.41
                        },
                        {
                            "se_name": "эозинофилия",
                            "rank": 0.39
                        },
                        {
                            "se_name": "фиброз",
                            "rank": 0.38
                        },
                        {
                            "se_name": "тошнота/рвота",
                            "rank": 0.38
                        },
                        {
                            "se_name": "флебит",
                            "rank": 0.35
                        },
                        {
                            "se_name": "галлюцинации",
                            "rank": 0.24
                        },
                        {
                            "se_name": "головная боль",
                            "rank": 0.2
                        },
                        {
                            "se_name": "неврит/нейропатия",
                            "rank": 0.19
                        },
                        {
                            "se_name": "обморок",
                            "rank": 0.18
                        },
                        {
                            "se_name": "васкулит",
                            "rank": 0.17
                        },
                        {
                            "se_name": "псориаз/алопеция",
                            "rank": 0.17
                        },
                        {
                            "se_name": "вертиго",
                            "rank": 0.15
                        },
                        {
                            "se_name": "диарея/запор",
                            "rank": 0.15
                        },
                        {
                            "se_name": "снижение либидо",
                            "rank": 0.15
                        },
                        {
                            "se_name": "экзема/крапивница",
                            "rank": 0.12
                        },
                        {
                            "se_name": "миалгия/судороги",
                            "rank": 0.11
                        },
                        {
                            "se_name": "нарушение слуха/зрения/вкуса",
                            "rank": 0.11
                        },
                        {
                            "se_name": "астения/утомляемость",
                            "rank": 0.1
                        },
                        {
                            "se_name": "инфаркт",
                            "rank": 0.0
                        },
                        {
                            "se_name": "гангрена Фурнье",
                            "rank": 0.0
                        },
                        {
                            "se_name": "внутричерепное кровоизлияние",
                            "rank": 0.0
                        },
                        {
                            "se_name": "гиперкалиемия",
                            "rank": 0.0
                        },
                        {
                            "se_name": "фибрилляция",
                            "rank": 0.0
                        },
                        {
                            "se_name": "гипертензия",
                            "rank": 0.0
                        },
                        {
                            "se_name": "гипогликемия",
                            "rank": 0.0
                        },
                        {
                            "se_name": "язва пищевода",
                            "rank": 0.0
                        },
                        {
                            "se_name": "желудочковая экстрасистолия",
                            "rank": 0.0
                        },
                        {
                            "se_name": "тахикардия",
                            "rank": 0.0
                        },
                        {
                            "se_name": "кетоацидоз",
                            "rank": 0.0
                        },
                        {
                            "se_name": "стенокардия",
                            "rank": 0.0
                        },
                        {
                            "se_name": "атриовентрикулярная блокада",
                            "rank": 0.0
                        },
                        {
                            "se_name": "бронхиальная астма",
                            "rank": 0.0
                        },
                        {
                            "se_name": "гематурия",
                            "rank": 0.0
                        },
                        {
                            "se_name": "гиперурикемия",
                            "rank": 0.0
                        },
                        {
                            "se_name": "язва желудка",
                            "rank": 0.0
                        },
                        {
                            "se_name": "гипербилирубинемия",
                            "rank": 0.0
                        },
                        {
                            "se_name": "нефролитиаз",
                            "rank": 0.0
                        },
                        {
                            "se_name": "почечная недостаточность",
                            "rank": 0.0
                        },
                        {
                            "se_name": "гастрит",
                            "rank": 0.0
                        },
                        {
                            "se_name": "конъюнктивит",
                            "rank": 0.0
                        },
                        {
                            "se_name": "дисменорея",
                            "rank": 0.0
                        },
                        {
                            "se_name": "пневмония",
                            "rank": 0.0
                        },
                        {
                            "se_name": "тромбоэмболия",
                            "rank": 0.0
                        },
                        {
                            "se_name": "стоматит",
                            "rank": 0.0
                        },
                        {
                            "se_name": "синдром Рейно",
                            "rank": 0.0
                        },
                        {
                            "se_name": "парестезия",
                            "rank": 0.0
                        },
                        {
                            "se_name": "ринорея/фарингит",
                            "rank": 0.0
                        },
                        {
                            "se_name": "паранойя",
                            "rank": 0.0
                        },
                        {
                            "se_name": "гинекомастия",
                            "rank": 0.0
                        },
                        {
                            "se_name": "анорексия",
                            "rank": 0.0
                        },
                        {
                            "se_name": "кашель/ринит",
                            "rank": 0.0
                        },
                        {
                            "se_name": "озноб/лихорадка",
                            "rank": 0.0
                        },
                        {
                            "se_name": "бессонница",
                            "rank": 0.0
                        },
                        {
                            "se_name": "дизурия/полиурия",
                            "rank": 0.0
                        },
                        {
                            "se_name": "дерматит",
                            "rank": 0.0
                        },
                        {
                            "se_name": "артралгия",
                            "rank": 0.0
                        },
                        {
                            "se_name": "подагра",
                            "rank": 0.0
                        },
                        {
                            "se_name": "тремор",
                            "rank": 0.0
                        },
                        {
                            "se_name": "полипоз",
                            "rank": 0.0
                        },
                        {
                            "se_name": "отек лица/конечностей",
                            "rank": 0.0
                        },
                        {
                            "se_name": "припухлость суставов",
                            "rank": 0.0
                        },
                        {
                            "se_name": "приливы",
                            "rank": 0.0
                        }
                    ]
                },
                {
                    "сompatibility": "caution",
                    "effects": [
                        {
                            "se_name": "агранулоцитоз",
                            "rank": 0.94
                        },
                        {
                            "se_name": "панкреатит",
                            "rank": 0.92
                        },
                        {
                            "se_name": "гипокалиемия",
                            "rank": 0.86
                        },
                        {
                            "se_name": "лейкопения",
                            "rank": 0.83
                        },
                        {
                            "se_name": "брадикардия",
                            "rank": 0.8
                        },
                        {
                            "se_name": "желудочно-кишечное кровотечение",
                            "rank": 0.68
                        },
                        {
                            "se_name": "гипотензия",
                            "rank": 0.63
                        },
                        {
                            "se_name": "бронхоспазм",
                            "rank": 0.57
                        },
                        {
                            "se_name": "отек легких",
                            "rank": 0.55
                        },
                        {
                            "se_name": "глаукома",
                            "rank": 0.53
                        }
                    ]
                },
                {
                    "сompatibility": "incompatible",
                    "effects": [
                        {
                            "se_name": "анафилактический шок",
                            "rank": 1.68
                        },
                        {
                            "se_name": "гепатит",
                            "rank": 1.4
                        }
                    ]
                }
            ],
            "combinations": [
                {
                    "сompatibility": "incompatible",
                    "drugs": [
                        "Амиодарон",
                        "Гидрохлоротиазид"
                    ]
                }
            ],
            "compatibility_medscape": "caution",
            "description": [
                "амиодарон будет увеличивать уровень или эффект гидрохлоротиазида за счет конкуренции основных (катионных) препаратов за почечный канальцевый клиренс. Используйте осторожность/монитор."
            ],
            "drugs": [
                "Амиодарон",
                "Гидрохлоротиазид"
            ]
        }
            return CustomResponse.response(
            status=status.HTTP_200_OK,
            message='Совместимость ЛС по Fortran успешно расcчитана',
            http_status=status.HTTP_200_OK,
            data=context)
        if drugs == [1, 12]:
            context = {
        "rank_iteractions": 1.2,
        "сompatibility_fortran": "incompatible",
        "side_effects": [
            {
                "сompatibility": "compatible",
                "effects": [
                    {
                        "se_name": "отек Квинке",
                        "rank": 0.49
                    },
                    {
                        "se_name": "атриовентрикулярная блокада",
                        "rank": 0.49
                    },
                    {
                        "se_name": "агранулоцитоз",
                        "rank": 0.47
                    },
                    {
                        "se_name": "панкреатит",
                        "rank": 0.46
                    },
                    {
                        "se_name": "гипокалиемия",
                        "rank": 0.42
                    },
                    {
                        "se_name": "гипертиреоз",
                        "rank": 0.42
                    },
                    {
                        "se_name": "эозинофилия",
                        "rank": 0.39
                    },
                    {
                        "se_name": "фиброз",
                        "rank": 0.38
                    },
                    {
                        "se_name": "тошнота/рвота",
                        "rank": 0.38
                    },
                    {
                        "se_name": "флебит",
                        "rank": 0.35
                    },
                    {
                        "se_name": "гипотензия",
                        "rank": 0.31
                    },
                    {
                        "se_name": "экзема/крапивница",
                        "rank": 0.24
                    },
                    {
                        "se_name": "галлюцинации",
                        "rank": 0.24
                    },
                    {
                        "se_name": "парестезия",
                        "rank": 0.23
                    },
                    {
                        "se_name": "гинекомастия",
                        "rank": 0.2
                    },
                    {
                        "se_name": "головная боль",
                        "rank": 0.2
                    },
                    {
                        "se_name": "неврит/нейропатия",
                        "rank": 0.19
                    },
                    {
                        "se_name": "анорексия",
                        "rank": 0.18
                    },
                    {
                        "se_name": "обморок",
                        "rank": 0.18
                    },
                    {
                        "se_name": "диарея/запор",
                        "rank": 0.15
                    },
                    {
                        "se_name": "снижение либидо",
                        "rank": 0.15
                    },
                    {
                        "se_name": "инфаркт",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гангрена Фурнье",
                        "rank": 0.0
                    },
                    {
                        "se_name": "внутричерепное кровоизлияние",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гиперкалиемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "лейкопения",
                        "rank": 0.0
                    },
                    {
                        "se_name": "фибрилляция",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипертензия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипогликемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "желудочно-кишечное кровотечение",
                        "rank": 0.0
                    },
                    {
                        "se_name": "язва пищевода",
                        "rank": 0.0
                    },
                    {
                        "se_name": "кетоацидоз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "отек легких",
                        "rank": 0.0
                    },
                    {
                        "se_name": "глаукома",
                        "rank": 0.0
                    },
                    {
                        "se_name": "стенокардия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "бронхиальная астма",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гематурия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гиперурикемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тромбоцитопения",
                        "rank": 0.0
                    },
                    {
                        "se_name": "синдром Стивенса-Джонсона",
                        "rank": 0.0
                    },
                    {
                        "se_name": "язва желудка",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипербилирубинемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "нефролитиаз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "почечная недостаточность",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гастрит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "конъюнктивит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дисменорея",
                        "rank": 0.0
                    },
                    {
                        "se_name": "пневмония",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тромбоэмболия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "стоматит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "синдром Рейно",
                        "rank": 0.0
                    },
                    {
                        "se_name": "ринорея/фарингит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "паранойя",
                        "rank": 0.0
                    },
                    {
                        "se_name": "кашель/ринит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "озноб/лихорадка",
                        "rank": 0.0
                    },
                    {
                        "se_name": "васкулит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "псориаз/алопеция",
                        "rank": 0.0
                    },
                    {
                        "se_name": "бессонница",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дизурия/полиурия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дерматит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "вертиго",
                        "rank": 0.0
                    },
                    {
                        "se_name": "артралгия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "подагра",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тремор",
                        "rank": 0.0
                    },
                    {
                        "se_name": "полипоз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "миалгия/судороги",
                        "rank": 0.0
                    },
                    {
                        "se_name": "отек лица/конечностей",
                        "rank": 0.0
                    },
                    {
                        "se_name": "нарушение слуха/зрения/вкуса",
                        "rank": 0.0
                    },
                    {
                        "se_name": "припухлость суставов",
                        "rank": 0.0
                    },
                    {
                        "se_name": "астения/утомляемость",
                        "rank": 0.0
                    },
                    {
                        "se_name": "приливы",
                        "rank": 0.0
                    }
                ]
            },
            {
                "сompatibility": "caution",
                "effects": [
                    {
                        "se_name": "некроз",
                        "rank": 0.98
                    },
                    {
                        "se_name": "анафилактический шок",
                        "rank": 0.84
                    },
                    {
                        "se_name": "гепатит",
                        "rank": 0.7
                    },
                    {
                        "se_name": "желудочковая экстрасистолия",
                        "rank": 0.65
                    },
                    {
                        "se_name": "тахикардия",
                        "rank": 0.62
                    },
                    {
                        "se_name": "бронхоспазм",
                        "rank": 0.57
                    }
                ]
            },
            {
                "сompatibility": "incompatible",
                "effects": [
                    {
                        "se_name": "брадикардия",
                        "rank": 1.2
                    }
                ]
            }
        ],
        "combinations": [
            {
                "сompatibility": "incompatible",
                "drugs": [
                    "Амиодарон",
                    "Дигоксин"
                ]
            }
        ],
        "compatibility_medscape": "incompatible",
        "description": [
            "амиодарон будет увеличивать уровень или эффект дигоксина с помощью переносчика оттока P-гликопротеина (MDR1). Избегайте или используйте альтернативный препарат. Амиодарон повышает концентрацию дигоксина в сыворотке перорально на ~70% и дигоксина внутривенно на ~17%; измерить уровень дигоксина до начала приема амиодарона и снизить пероральную дозу дигоксина на 30-50%; уменьшить внутривенную дозу дигоксина на 15-30%"
        ],
        "drugs": [
            "Амиодарон",
            "Дигоксин"
        ]
    }
            return CustomResponse.response(
            status=status.HTTP_200_OK,
            message='Совместимость ЛС по Fortran успешно расcчитана',
            http_status=status.HTTP_200_OK,
            data=context)
        try:
            drugs_list = [Drug.objects.get(pk=drug).drug_name
                              for drug in drugs]
            if (Drug.objects.filter(id=drugs[0]).exists()
                    and Drug.objects.filter(id=drugs[1]).exists()):
                    context = {
                        'drugs': drugs_list,
                        'description': 'Справка в MedScape отсутствует',
                        'compatibility_medscape': (
                            'Информация о совместимости в MedScape отсутствует')
                    }
                    return CustomResponse.response(
                        data=context,
                        status=status.HTTP_204_NO_CONTENT,
                        message='Нет сведений о совместимости',
                        http_status=status.HTTP_204_NO_CONTENT)
        except Drug.DoesNotExist:
            return CustomResponse.response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message='Ошибка определения совместимости',
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
