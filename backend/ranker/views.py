import os
import traceback
import logging
import time
import json
from pathlib import Path

from django.utils import timezone
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings

from ranker.utils.fortran_calculator import FortranCalculator,FortranCalculatorNormalization
from drugs.utils.custom_response import CustomResponse
from drugs.models import Drug
from ranker.utils.check_banned import DrugPairChecker
from ranker.services.table_gerention import ExcelTableGenerater
from ranker.services.file_naming import generate_unique_filename
from ranker.constants import IDX_2_RANK_NAME


logger = logging.getLogger('fortran')


class CalculationAPI(APIView):
    """Вычисление рангов."""

    AGE = 65
    MAN = 'man'
    WOMEN = 'woman'

    def _exist_contraindications(self, drug_ids, contra_ids):
        """
        Проверка наличия противопоказаний.

        Проверка пересечения противопоказаний у ЛС из комбинации
        и противопоказаний, указанных в запросе.
        """
        exist = False
        submessages = []

        drugs = Drug.objects.filter(id__in=drug_ids).prefetch_related(
            "contraindications")
        for drug in drugs:
            intersect = drug.contraindications.filter(id__in=contra_ids)
            logger.debug(f'drug = {drug.drug_name}')
            for contra in drug.contraindications.all():
                logger.debug(f'contra - {contra.id}, {contra.name}')
            if intersect.exists():
                logger.debug('Противопоказание у ЛС есть')
                names = ", ".join(list(intersect.values_list("name",
                                                             flat=True)))
                submessages.append(f'{drug.drug_name}: {names}')
                exist = True

        if submessages:
            *rest, last = submessages
            message = ';\n'.join(rest + [last + '.'])
        else:
            message = None

        return exist, message

    def post(self, request, normalization_calculate=True):
        """Временный метод для просмотра изначальной структуры выхода."""
        # logger.debug(f'входная строка {request.build_absolute_uri()}')

        # logger.debug(f'request.query_params = {request.query_params}')

        drugs_line = request.data.get('drugs', None)

        if isinstance(drugs_line, str):
            drugs = json.loads(drugs_line)
        else:
            drugs = drugs_line

        # drugs = json.loads(drugs_line) if drugs_line else None

        # logger.debug(f'data = {data}')

        human_data_line = request.data.get('humanData', None)
        if isinstance(human_data_line, str):
            human_data = json.loads(human_data_line)
        else:
            human_data = human_data_line

        med_card = request.FILES.get('medCard', None)

        contraindications = None

        if human_data is not None:
            age = human_data.get('age', 30)
            if age is None:
                age = 30

            gender = human_data.get('gender', 'man')
            if gender is None:
                gender = 'man'

            contraindications = human_data.get('cont_list', None)

        print('contraindications =', contraindications)

        index = 0
        # index = None
        # if human_data is None:
        #     index = 0
        # else:
        #     if age < self.AGE and gender == self.MAN:
        #         index = 1
        #     elif age < self.AGE and gender == self.WOMEN:
        #         print('Молодая женщина')
        #         index = 2
        #     elif age >= self.AGE and gender == self.MAN:
        #         index = 3
        #     elif age >= self.AGE and gender == self.WOMEN:
        #         index = 4

        if drugs is None:
            message = (
                "Обязательный параметр drugs отсутствует"
                " или некорректный.")
            logger.error(message)
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message=message,
                http_status=status.HTTP_400_BAD_REQUEST)

        if index >= len(IDX_2_RANK_NAME):
            message = (
                "Обязательный параметр humanData отсутствует"
                " или некорректный.")
            logger.error(message)
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message=message,
                http_status=status.HTTP_400_BAD_REQUEST)

        if med_card:
            filename = generate_unique_filename(med_card.name)
            med_card_dir_path = Path(settings.CART_PATH) / filename
            with open(med_card_dir_path, 'wb') as f:
                for chunk in med_card.chunks():
                    f.write(chunk)

        сompatibility_fortran = None

        banned = DrugPairChecker().check_banned(drugs)
        logger.debug(f'banned = {banned}')
        if banned:
            сompatibility_fortran = "banned"
            return CustomResponse(
                status=status.HTTP_200_OK,
                message='Совместимость ЛС по Fortran успешно расcчитана',
                http_status=status.HTTP_200_OK,
                data={
                    "сompatibility_fortran": сompatibility_fortran,
                    "combinations": [
                        {
                            "сompatibility": сompatibility_fortran,
                            "drugs": banned

                        }],
                    "drugs": list(
                            Drug.objects.filter(id__in=drugs
                                                ).values_list(
                                                    'drug_name', flat=True)),
                    }
                )

        exist = None
        if contraindications:
            exist, description = (
                self._exist_contraindications(drugs, contraindications))

        if exist:
            logger.debug('Есть найдено противопоказание')
            сompatibility_fortran = 'banned-contraindications'

        print('exist =', exist)

        start_time = time.time()
        
        if normalization_calculate:
            calculator = FortranCalculatorNormalization()
        else:
            calculator = CalculatorMP()

        while len(drugs) < calculator.n_k:
            drugs.append(0)

        try:
            rank_name = IDX_2_RANK_NAME[index]
            logger.debug(f'filename во вьюшке = {rank_name}')
            if normalization_calculate:           
                canceling_effects_json_manual=[[2,3],[5,14],[7,13],[32,33],[51,52],[86,87]]
                context = calculator.calculate(
                    rank_name=rank_name,
                    nj=drugs,
                    canceling_groups=canceling_effects_json_manual)
            else:
                context = calculator.calculate(
                    rank_name=rank_name,
                    nj=drugs)
                
            elapsed_time = time.time() - start_time
            logger.debug(('Время выполнения экспорта данных '
                          f'и рассчёта: {elapsed_time:.2f} сек.'))

            if сompatibility_fortran:
                context["сompatibility_fortran"] = сompatibility_fortran

            return CustomResponse(
                status=status.HTTP_200_OK,
                message='Совместимость ЛС по Fortran успешно расcчитана',
                http_status=status.HTTP_200_OK,
                data=context)

        except Exception:
            logger.critical(traceback.format_exc())

            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Ошибка определения совместимости',
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TablesView(APIView):
    """
    Генерация таблиц.

    Таблицы:
        - ранги для ЛС;
        - исключения (они же запрещённые пары);
        - ЛС, противопоказания и их веса.
    """

    def post(self, request):
        """Генерация Excel-файла с таблицами."""
        try:
            buffer = ExcelTableGenerater().generate_tables()

            file_size = len(buffer.getvalue())
            logger.debug(f"Размер файла: {file_size} байт")

            if file_size < 1000:
                logger.error('Сгенерированный файл слишком маленький. '
                             'Вероятно, поврежден.')
                return CustomResponse(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message='Сгенерированный файл поврежден',
                    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return CustomResponse(
                status=status.HTTP_200_OK,
                message="Excel-файл с таблицы сгенерирован успешно",
                http_status=status.HTTP_200_OK)

        except Exception as error:
            message = 'Ошибка генерации таблиц'
            logger.error(f'{message}. {error}')
            print("=" * 80)
            print("КРИТИЧЕСКАЯ ОШИБКА в генерации таблиц:")
            traceback.print_exc()
            print("=" * 80)
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=message,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """Получение Excel-файла с таблицами."""
        path = Path(settings.GENERATED_TABLES)

        if not path.exists() or not path.is_dir:
            return CustomResponse(
                status=status.HTTP_404_NOT_FOUND,
                message="Нет директории с генерированными excel-таблицами",
                http_status=status.HTTP_404_NOT_FOUND
            )

        files = [f for f in path.iterdir() if f.is_file()]

        if not files:
            return CustomResponse(
                status=status.HTTP_404_NOT_FOUND,
                message="В директории нет сгенерированного excel-таблицами",
                http_status=status.HTTP_404_NOT_FOUND
            )

        tables_file = max(files, key=lambda f: f.stat().st_mtime)

        print('tables_file.name =', tables_file.name)

        return FileResponse(
                tables_file.open('rb'),
                content_type=('application/vnd.openxmlformats-officedocument.'
                              'spreadsheetml.sheet'),
                filename=tables_file.name,
                as_attachment=True)
