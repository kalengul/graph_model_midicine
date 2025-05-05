import traceback
import logging

from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings

from ranker.utils.file_loader import FileLoader
from ranker.utils.fortran_calculator import FortranCalculator
from drugs.utils.custom_response import CustomResponse
from ranker.serializers import QueryParamsSerializer


TXT_FILENAMES = [
    'rangbase.txt', 
    'rangm1.txt', 
    'rangf1.txt'
    'rangfreq.txt', 
    'rangm2.txt', 
    'rangf2.txt', 

    # 'side_effects.txt', 
    # 'drugs_xcn.txt', 
    # 'rangs.txt', 
    ]

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
        drugs = data.get('drugs')
        file_index = data.get('humanData')
        
        if not drugs:
            logger.error("Обязательный параметр drugs отсутствует или некорректный.")
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Обязательный параметр drugs отсутствует или некорректный.",
                http_status=status.HTTP_400_BAD_REQUEST)

        if not file_index or file_index >= len(TXT_FILENAMES):
            logger.error("Обязательный параметр file_index отсутствует или некорректный.")
            return CustomResponse.response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Обязательный параметр file_index отсутствует или некорректный.",
                http_status=status.HTTP_400_BAD_REQUEST)

        FileLoader.load_drugs_from_file(base_dir)
        FileLoader.load_disease_chf_from_file(base_dir)

        calculator = FortranCalculator()

        drug_indices2 = drugs[:]

        while len(drugs) < calculator.n_k:
            drugs.append(0)

        try:
            context = calculator.calculate(
                base_dir,
                TXT_FILENAMES[file_index],
                drugs,
                drug_indices2
            )
            
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
