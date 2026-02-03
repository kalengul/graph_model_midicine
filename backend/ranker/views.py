import traceback
import logging
import time

from django.utils import timezone
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework import status

from ranker.utils.fortran_calculator import FortranCalculator
from drugs.utils.custom_response import CustomResponse
from drugs.models import Drug
from ranker.utils.check_banned import DrugPairChecker
from ranker.services.table_gerention import ExcelTableGenerater
from ranker.constants import IDX_2_RANK_NAME


logger = logging.getLogger('fortran')


class CalculationAPI(APIView):
    """Вычисление рангов."""

    AGE = 65
    MAN = 'man'
    WOMEN = 'woman'

    def post(self, request):
        """Временный метод для просмотра изначальной структуры выхода."""
        # logger.debug(f'входная строка {request.build_absolute_uri()}')

        # logger.debug(f'request.query_params = {request.query_params}')

        # serializer = QueryParamsSerializer(data=request.query_params)
        # serializer.is_valid(raise_exception=True)
        # data = serializer.validated_data

        drugs = request.data.get('drugs')
        # logger.debug(f'data = {data}')
        human_data = request.data.get('humanData', None)

        if human_data is not None:
            age = human_data.get('age', 18)
            if age is None:
                age = 18

            gender = human_data.get('gender', 'man')
            if gender is None:
                gender = 'man'

        print('drugs', drugs)
        print('human_data', human_data)

        index = None
        if human_data is None:
            index = 0
        else:
            if age < self.AGE and gender == self.MAN:
                index = 1
            elif age < self.AGE and gender == self.WOMEN:
                print('Моложая женщина')
                index = 2
            elif age >= self.AGE and gender == self.MAN:
                index = 3
            elif age >= self.AGE and gender == self.WOMEN:
                index = 4

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
        banned = DrugPairChecker().check_banned(drugs)
        logger.debug(f'banned = {banned}')
        if banned:
            return CustomResponse(
                status=status.HTTP_200_OK,
                message='Совместимость ЛС по Fortran успешно расcчитана',
                http_status=status.HTTP_200_OK,
                data={
                    "сompatibility_fortran": "banned",
                    "combinations": [
                        {
                            "сompatibility": "banned",
                            "drugs": banned

                        }],
                    "drugs": list(
                            Drug.objects.filter(id__in=drugs
                                                ).values_list(
                                                    'drug_name', flat=True)),
                    }
                )

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
            logger.debug(('Время выполнения экспорда данных '
                          f'и рассчёта: {elapsed_time:.2f} сек.'))

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


class GetTablesView(APIView):
    """
    Экспорт таблиц.

    Таблицы:
        - ранги для ЛС;
        - исключения (они же запрещённые пары);
        - ЛС, противопоказния и их веса.
    """

    def get(self, request):
        """Получение Excel-файла с таблицами."""
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

            return FileResponse(
                buffer,
                content_type=('application/vnd.openxmlformats-officedocument.'
                              'spreadsheetml.sheet'),
                filename=(f'tables_{timezone.now().strftime("%Y%m%d_%H%M%S")}'
                          '.xlsx'),
                as_attachment=True)
        except Exception as error:
            message = 'Ошибка генерации таблиц'
            logger.error(f'{message}. {error}')
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=message,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
