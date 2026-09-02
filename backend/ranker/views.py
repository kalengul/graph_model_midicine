import traceback
import logging
import time
import json
from pathlib import Path

from django.http import FileResponse
from django.conf import settings

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from ranker.utils.fortran_calculator import FortranCalculatorSimple, FortranCalculator
from ranker.utils.check_banned import DrugPairChecker
from ranker.services.table_gerention import ExcelTableGenerater
from ranker.constants import IDX_2_RANK_NAME

from drugs.utils.custom_response import CustomResponse
from drugs.models import Drug, SideEffect, DrugSideEffect

from ranker.serializers import (CalculationRequestSerializer,
                                CalculationDataSerializer
                                )

from logging_system.services import CalculationLoggingService

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes


logger = logging.getLogger('fortran')


@extend_schema_view(
    post=extend_schema(
        operation_id='rank_calculation',
        tags=['ranker'],
        request=CalculationRequestSerializer,
        responses={
            200: CalculationDataSerializer,
            400: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
    ),
)
class CalculationAPI(APIView):
    """Вычисление рангов."""

    # Константы для совместимости
    COMPATIBILITY_BANNED = 'banned'
    COMPATIBILITY_BANNED_CONTRAINDICATIONS = 'banned-contraindications'

    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def post(self, request, normalization_calculate=True):
        """
        POST-запрос для расчета совместимости лекарственных средств.
        
        Args:
            request: HTTP запрос с данными
            normalization_calculate: флаг использования нормализации
            
        Returns:
            CustomResponse с результатами расчета
        """

        # Получаем пользователя
        user = request.user if request.user.is_authenticated else None

        try:

            # Валидация и подготовка данных
            validation_result = self._validate_input_data(request)
            
            # Проверяем, не вернулась ли ошибка
            if isinstance(validation_result, CustomResponse):
                return validation_result
            
            # Распаковываем данные
            drugs, human_data, med_card = validation_result

            # Логгирование
            CalculationLoggingService.log_request(user, drug_ids=drugs)

            # Создаем базовый шаблон ответа
            response_data = self._create_base_response_template(drugs)
            
            # Проверка запрещенных пар (banned)
            banned_pairs = DrugPairChecker().check_banned(drugs)
            if banned_pairs:
                resp = self._create_banned_response(response_data, banned_pairs)
                return resp
            
            # Проверка противопоказаний (если есть)
            if human_data and (human_data.get('cont_list') or human_data.get('age')):
                logger.debug(f'Наличие данных о человеке: {human_data}')
                contraindications_result = self._exist_contraindications(
                    drugs, human_data
                )
                if contraindications_result:
                    return self._create_contraindications_response(
                        response_data, contraindications_result)
            
            # Расчёт совместимости
            gender = human_data.get('gender') if human_data else None
            resp = self._calculate_compatibility(response_data, drugs,
                                                 normalization_calculate,
                                                 gender)
            return resp
            
        except Exception as e:
            logger.critical(f"Критическая ошибка: {traceback.format_exc()}")
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Ошибка определения совместимости',
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
               
    def _validate_input_data(self, request):
        """
        Валидация и подготовка входных данных из request.
        Поддерживает JSON и form-data форматы.
        
        Args:
            request: HTTP запрос
            
        Returns:
            - Если ошибка: CustomResponse с описанием ошибки
            - Если успех: кортеж (drugs, human_data, med_card)
        """

        def parse_field(data, field_name, required=False):
            """Парсит JSON поле или возвращает ошибку"""
            value = data.get(field_name)
            
            if required and value is None:
                return CustomResponse(status=400, message=f'Поле {field_name} обязательно', http_status=400)
            
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return CustomResponse(status=400, message=f'Неверный JSON в поле {field_name}', http_status=400)
            return value
        
        # Парсим drugs
        drugs = parse_field(request.data, 'drugs', required=True)
        if isinstance(drugs, CustomResponse):
            return drugs
        
        # Парсим human_data
        human_data = parse_field(request.data, 'humanData', required=False)
        if isinstance(human_data, CustomResponse):
            return human_data
        
        med_card = request.FILES.get('medCard')
        
        return (drugs, human_data, med_card)
    
    def _create_base_response_template(self, drugs):
        """
        Создание базового шаблона ответа.
        """
        return {
            "side_effects": [],
            "SEFromDrug": [],
            "drugs": list(Drug.objects.filter(id__in=drugs).values_list('drug_name', flat=True)),
            "compatibility_fortran": None,
            "bannedPairs": [],
            "bannedPairsCont": [],
        }
    
    def _exist_contraindications(self, drug_ids, human_data):
        """
        Проверка наличия противопоказаний.
        """
        result = []
        
        explicit_contra_ids = human_data.get('cont_list', [])
        age = human_data.get('age')
        
        drugs = Drug.objects.filter(id__in=drug_ids).prefetch_related(
            "contraindications"
        )
        
        if age is not None:
            drugs = drugs.prefetch_related("age_restrictions")
        
        for drug in drugs:
            explicit_intersect = drug.contraindications.filter(id__in=explicit_contra_ids)
            has_explicit = explicit_intersect.exists()
            
            has_age_violation = False
            age_violation_names = []
            
            if age is not None:
                for restriction in drug.age_restrictions.all(): # type: ignore
                    if restriction.age_from and age < restriction.age_from:
                        has_age_violation = True
                        age_violation_names.append(f"возраст до {restriction.age_from} лет")
                    elif restriction.age_to and age > restriction.age_to:
                        has_age_violation = True
                        age_violation_names.append(f"возраст после {restriction.age_to} лет")
            
            if has_explicit or has_age_violation:
                contra_names = []
                
                if has_explicit:
                    contra_names.extend(explicit_intersect.values_list("name", flat=True))
                
                if has_age_violation:
                    contra_names.extend(age_violation_names)
                
                result.append({
                    "drug": drug.drug_name,
                    "contraindications": contra_names
                })
        
        return result

    def _create_banned_response(self, template_data, banned_pairs):
        """
        Создание ответа при обнаружении запрещенных пар.
        """

        logger.debug('Найдены запрещённые пары')
        logger.debug(f'Результат: {banned_pairs}')

        # Заполняем шаблон
        template_data.update({"compatibility_fortran": self.COMPATIBILITY_BANNED})
        template_data["bannedPairs"] = banned_pairs

        return CustomResponse(
            status=status.HTTP_200_OK,
            message='Совместимость ЛС по Fortran успешно рассчитана',
            http_status=status.HTTP_200_OK,
            data=template_data
        )
    
    def _create_contraindications_response(self, template_data, contraindications_result):
        """
        Создание ответа при обнаружении противопоказаний.
        """
        logger.debug('Найдены противопоказания')
        logger.debug(f'Результат: {contraindications_result}')

        # Заполняем шаблон
        template_data.update({"compatibility_fortran": self.COMPATIBILITY_BANNED_CONTRAINDICATIONS})
        template_data["bannedPairsCont"] = contraindications_result
        
        return CustomResponse(
            status=status.HTTP_200_OK,
            message='Совместимость ЛС по Fortran успешно рассчитана',
            http_status=status.HTTP_200_OK,
            data=template_data
        )
       

    def _calculate_compatibility(self, template_data, drugs, normalization_calculate, gender):
        """
        Расчет совместимости лекарственных средств.
        """
        # 1. Валидация полноты весов
        validation_error = self._validate_weights_completeness()
        if validation_error:
            return validation_error
        
        # 2. Основной расчёт
        calculator = FortranCalculator(
            normalize=normalization_calculate,
            cuttoff_not_life_threats_side_e = True
            )
        
        context = calculator.calculate(
            rank_name=IDX_2_RANK_NAME[0],
            n_drug=drugs,
            gender=gender
        )

        # Объединяем шаблон с результатами расчета
        final_data = {**template_data, **context}    
        
        return CustomResponse(
            status=status.HTTP_200_OK,
            message='Совместимость ЛС по Fortran успешно рассчитана',
            http_status=status.HTTP_200_OK,
            data=final_data
        )
    
    def _validate_weights_completeness(self):
        """
        Проверяет контрольные суммы: 
        1) Количество побочных эффектов должно быть больше 0
        2) Общее количество записей DrugSideEffect
        для общего количества препаратов должно равняться
        (количество препаратов) × (количество побочных эффектов).
            
        Returns:
            None, если всё OK, иначе CustomResponse с ошибкой 400
        """
        
        total_se_count = SideEffect.objects.count()

        if total_se_count == 0:
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message=("Побочные эффекты и записи весов не загружены."),
                http_status=status.HTTP_400_BAD_REQUEST
            )
        
        total_drugs_count = Drug.objects.count()
        actual = DrugSideEffect.objects.count()
        expected = total_drugs_count * total_se_count

        if actual != expected:     
            return CustomResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message=(
                    f'Нарушена целостность данных:'
                    f'ожидается {expected} записей весов, найдено {actual}.'
                ),
                http_status=status.HTTP_400_BAD_REQUEST
            )
        return None


@extend_schema_view(
    post=extend_schema(
        operation_id='table_generation',
        tags=['ranker'],
        request=None,
        responses={
            200: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
    ),
    get=extend_schema(
        operation_id='table_download',
        tags=['ranker'],
        responses={
            200: OpenApiTypes.BINARY,
            404: OpenApiTypes.OBJECT,
        },
    ),
)
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

        if not path.exists() or not path.is_dir():
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
