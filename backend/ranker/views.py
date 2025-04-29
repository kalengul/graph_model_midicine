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

    def get(self, request):
        """Временный метод для просмотра изначальной структуры выхода."""
        logger.debug(f'входная строка {request.build_absolute_uri()}')
        base_dir = settings.BASE_DIR
        serializer = QueryParamsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        drugs = data['drugs']
        human_data_raw = data['humanData']
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
        try:
            human_data = json.loads(human_data_raw)
            file_name = human_data.get('age', ['rangbase.txt'])[0]
        except (json.JSONDecodeError, TypeError, IndexError, KeyError):
            file_name = 'rangbase.txt'

        FileLoader.load_drugs_from_file(base_dir)
        FileLoader.load_disease_chf_from_file(base_dir)

        calculator = FortranCalculator()

        drug_indices2 = drugs[:]

        while len(drugs) < calculator.n_k:
            drugs.append(0)

        print('base_dir =', base_dir)
        print('file_name =', file_name)
        print('drug_indices =', drugs)
        print('drug_indices2 =', drug_indices2)

        try:
            context = calculator.calculate(base_dir,
                                                   file_name,
                                                   drugs,
                                                   drug_indices2)
            return CustomResponse.response(
                status=status.HTTP_200_OK,
                message='Совместимость ЛС по Fortran успешно расcчитана',
                http_status=status.HTTP_200_OK,
                data=context)
        except Exception:
            print(traceback.format_exc())
            return CustomResponse.response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Ошибка определения совместимости',
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
