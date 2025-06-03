import traceback
import logging
import time
from types import MappingProxyType

from rest_framework.views import APIView
from rest_framework import status

from ranker.utils.fortran_calculator import FortranCalculator
from drugs.utils.custom_response import CustomResponse
from ranker.serializers import QueryParamsSerializer


IDX_2_RANK_NAME = MappingProxyType({
        0: 'rang_base',
        1: 'rang_m1',
        2: 'rang_f1',
        3: 'rang_freq',
        4: 'rang_m2',
        5: 'rang_f2'
    })

logger = logging.getLogger('fortran')


class CalculationAPI(APIView):
    """Вычисление рангов."""

    def get(self, request):
        """Временный метод для просмотра изначальной структуры выхода."""
        logger.debug(f'входная строка {request.build_absolute_uri()}')

        logger.debug(f'request.query_params = {request.query_params}')
        serializer = QueryParamsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        drugs = data.get('drugs')
        logger.debug(f'data = {data}')
        index = data.get('humanData')

        if drugs is None:
            message = "Обязательный параметр drugs отсутствует или некорректный."
            logger.error(message)
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message=message,
                http_status=status.HTTP_400_BAD_REQUEST)

        if index is None or index >= len(IDX_2_RANK_NAME):
            message = "Обязательный параметр humanData отсутствует или некорректный."
            logger.error(message)
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message=message,
                http_status=status.HTTP_400_BAD_REQUEST)

        start_time = time.time()

        calculator = FortranCalculator()

        while len(drugs) < calculator.n_k:
            drugs.append(0)

        try:
            rank_name = IDX_2_RANK_NAME[index]
            logger.debug(f'filename во вьюшке = {rank_name}')
            context = calculator.calculate(
                rank_name=rank_name,
                nj=drugs)

            elapsed_time = time.time() - start_time
            logger.debug(f'Время выполнения экспорда данных и рассчёта: {elapsed_time:.2f} сек.')

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
