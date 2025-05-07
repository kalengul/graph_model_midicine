import traceback
import logging
import time

from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings

from ranker.utils.file_loader import FileLoader
from drugs.utils.db_manipulator import DBManipulator
from ranker.utils.fortran_calculator import FortranCalculator
from drugs.utils.custom_response import CustomResponse
from ranker.serializers import QueryParamsSerializer


TXT_FILENAMES = [
    'rangbase.txt', 
    'rangm1.txt', 
    'rangf1.txt',
    'rangfreq.txt', 
    'rangm2.txt', 
    'rangf2.txt', 
    ]

logger = logging.getLogger('fortran')


class CalculationAPI(APIView):
    """Вычисление рангов."""

    def get(self, request):
        """Временный метод для просмотра изначальной структуры выхода."""
        logger.debug(f'входная строка {request.build_absolute_uri()}')
        base_dir = settings.BASE_DIR

        logger.debug(f'request.query_params = {request.query_params}')
        serializer = QueryParamsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        drugs = data.get('drugs')
        logger.debug(f'data = {data}')
        file_index = data.get('humanData')

        if drugs is None:
            message = "Обязательный параметр drugs отсутствует или некорректный."
            logger.error(message)
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message=message,
                http_status=status.HTTP_400_BAD_REQUEST)

        if file_index is None or file_index >= len(TXT_FILENAMES):
            message = "Обязательный параметр humanData отсутствует или некорректный."
            logger.error(message)
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message=message,
                http_status=status.HTTP_400_BAD_REQUEST)

        start_time = time.time()

        DBManipulator().export_from_db()
        FileLoader.load_all(base_dir)

        calculator = FortranCalculator()

        while len(drugs) < calculator.n_k:
            drugs.append(0)

        try:
            filename = TXT_FILENAMES[file_index]

            context = calculator.calculate(
                base_dir=base_dir,
                file_name=filename,
                nj=drugs)

            elapsed_time = time.time() - start_time
            print('elapsed_time =', elapsed_time)
            logger.info(f'Время выполнения экспорда данных и рассчёта: {elapsed_time:.2f} сек.')

            return CustomResponse.response(
                status=status.HTTP_200_OK,
                message='Совместимость ЛС по Fortran успешно расcчитана',
                http_status=status.HTTP_200_OK,
                data=context)
        
        except Exception:
            logger.critical(traceback.format_exc())

            return CustomResponse.response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Ошибка определения совместимости',
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
