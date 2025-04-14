import json

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings

from ranker.models import DrugCHF
from ranker.utils.file_loader import FileLoader
from ranker.utils.fortran_calculator import FortranCalculator


class CalculationAPI(APIView):
    """Вычисление рангов."""

    def get(self, request):
        """Метод для GET-запроса."""
        # Получаем параметры
        # base_dir = settings.BASE_DIR
        # drugs_param = request.GET.get('drugs', '')
        # file_name = request.GET.get('file_upload', '')

        base_dir = settings.BASE_DIR
        drug_indices = request.GET.get('drugs', '')
        file_name = request.GET.get('humanData', '')

        print('file_name =', file_name)

        drug_indices = json.loads(drug_indices)
        file_name = json.loads(file_name)

        print('drugs_param =', drug_indices)
        print('type(drugs_param) =', type(drug_indices))
        print('type(drugs_param[0]) =', type(drug_indices[0]))

        print('file_name =', file_name)
        print('type(file_name) =', type(file_name['age']))
        print('type(file_name[0]) =', type(file_name['age'][0]))

        # Принудительная перезагрузка БД из файлов
        FileLoader.load_drugs_from_file(base_dir)
        FileLoader.load_disease_chf_from_file(base_dir)

        calculator = FortranCalculator()

        while len(drug_indices) < calculator.n_k:
            drug_indices.append(0)

        print('len(drug_indices) =', len(drug_indices))

        try:
            context = calculator.load_data_in_file(base_dir,
                                                   file_name,
                                                   drug_indices)
            return Response(context, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
