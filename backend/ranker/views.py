import json
import traceback
import logging

from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings

from ranker.utils.file_loader import FileLoader
from drugs.utils.db_manipulator import DBManipulator
from ranker.utils.fortran_calculator import FortranCalculator
from drugs.utils.custom_response import CustomResponse
from ranker.serializers import QueryParamsSerializer


logger = logging.getLogger('fortran')


class CalculationAPI(APIView):
    """Вычисление рангов."""

    CANONICAL_KEY = 'humanData'
    NOCANONICAL_KEY = 'humanData[age]'

    def get(self, request):
        """Временный метод для просмотра изначальной структуры выхода."""
        logger.debug(f'входная строка {request.build_absolute_uri()}')
        base_dir = settings.BASE_DIR
        print('request.query_params =', request.query_params)
        serializer = QueryParamsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        drugs = data.get('drugs')
        print('data =', data)
        human_data_raw = data.get(self.CANONICAL_KEY)
        if not drugs:
            logger.error("Обязательный параметр drugs отсутствует или некорректный.")
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Обязательный параметр drugs отсутствует или некорректный.",
                http_status=status.HTTP_400_BAD_REQUEST)
        nocanonical = request.query_params.get(self.NOCANONICAL_KEY)
        if not human_data_raw and nocanonical:
            logger.debug('Не стантарный ключ в параметрах')
            human_data_raw = data.get(self.NOCANONICAL_KEY)
            human_data_raw = {'age': [nocanonical.strip('[]').strip()]}
        elif not human_data_raw:
            logger.error("Обязательный параметр humanData отсутствует или некорректный.")
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Обязательный параметр humanData отсутствует или некорректный.",
                http_status=status.HTTP_400_BAD_REQUEST)
        try:
            file_name = human_data_raw.get('age', ['rangbase.txt'])[0]
        except (json.JSONDecodeError, TypeError, IndexError, KeyError):
            file_name = 'rangbase.txt'

        FileLoader.load_drugs_from_file(base_dir)
        FileLoader.load_disease_chf_from_file(base_dir)
        # DBManipulator().export_from_db()

        calculator = FortranCalculator()

        while len(drugs) < calculator.n_k:
            drugs.append(0)

        try:
            context = calculator.calculate(base_dir,
                                           file_name,
                                           drugs)
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
