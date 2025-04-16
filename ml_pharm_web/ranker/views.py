import json

from rest_framework.response import Response
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

        base_dir = settings.BASE_DIR
        drugs_raw = request.query_params.get('drugs')
        file_name = request.query_params.get('humanData', '')
        drug_indices = [int(x.strip())
                        for x in drugs_raw.split(",")] if drugs_raw else []

        # print('file_name =', file_name)
        # print('type(file_name) =', type(file_name['age']))
        # print('type(file_name[0]) =', type(file_name['age'][0]))
        if file_name:
            file_name = json.loads(file_name)
            file_name = file_name['age'][0]
        else:
            file_name = 'rangbase.txt'
        # Принудительная перезагрузка БД из файлов
        FileLoader.load_drugs_from_file(base_dir)
        FileLoader.load_disease_chf_from_file(base_dir)

        calculator = FortranCalculator()

        drug_indices2 = drug_indices[:]

        while len(drug_indices) < calculator.n_k:
            drug_indices.append(0)

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
            return CustomResponse.response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Ошибка определения совместимости',
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Поиск препаратов в БД
        # drug_names = [name.strip().lower() for name in drugs_param.split(',')]

        # print('drug_names =', drug_names)
        # print('type(drug_names) =', type(drug_names))

        # drugs = DrugCHF.objects.filter(name__in=drugs_param)
        # drug_indices = list(drugs.values_list('index', flat=True))

        # calculator = FortranCalculator()

        # while len(drug_indices) < calculator.n_k:
        #     drug_indices.append(0)

        # try:
        #     context = calculator.load_data_in_file(base_dir,
        #                                            file_name,
        #                                            drug_indices)
        #     return Response(context, status=status.HTTP_200_OK)
        # except Exception as e:
        #     return Response({'error': str(e)},
