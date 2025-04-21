import json
import ast
import traceback

from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings

from ranker.models import DrugCHF
from ranker.utils.file_loader import FileLoader
from ranker.utils.fortran_calculator import FortranCalculator
from drugs.utils.custom_response import CustomResponse


class CalculationAPI(APIView):
    """Вычисление рангов."""

    def get(self, request):
        """Метод для GET-запроса."""
        # Получаем параметры
        base_dir = settings.BASE_DIR

        drugs_raw = request.query_params.get('drugs', [])
        human_data_raw = request.query_params.get('humanData', {})
        try:
            drug_indices = list(map(int, ast.literal_eval(drugs_raw)))
        except (ValueError, SyntaxError):
            drug_indices = []

        try:
            human_data = json.loads(human_data_raw)
            file_name = human_data.get('age', ['rangbase.txt'])[0]
        except (json.JSONDecodeError, TypeError, IndexError, KeyError):
            file_name = 'rangbase.txt'
        # Принудительная перезагрузка БД из файлов
        FileLoader.load_drugs_from_file(base_dir)
        FileLoader.load_disease_chf_from_file(base_dir)

        calculator = FortranCalculator()

        drug_indices2 = drug_indices[:]

        while len(drug_indices) < calculator.n_k:
            drug_indices.append(0)

        print('base_dir =', base_dir)
        print('file_name =', file_name)
        print('drug_indices =', drug_indices)
        print('drug_indices2 =', drug_indices2)

        try:
            context = calculator.load_data_in_file(base_dir,
                                                   file_name,
                                                   drug_indices,
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
