"""Модуль абстрактный загрузчик."""

import os
import logging
from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd

from django.conf import settings

from drugs.models import (Drug,
                      DrugSideEffect,
                      SideEffect,
                      SideEffectsGender
                      )

from drugs.utils.universal_cleaner import universal_cleaner
from drugs.utils.custom_exception import IncorrectFile

logger = logging.getLogger('drugs')


class Loader(ABC):
    """Абстрактный загрузчик."""

    @abstractmethod
    def _load_drugs(self):
        """Загрузка ЛС."""

    @abstractmethod
    def _load_side_effects(self):
        """Загрузка ПД."""

    @abstractmethod
    def _load_ranks(self):
        """Загрузка рангов."""

    def load_to_db(self):
        """Загрузка в БД всех данных."""
        
        # Очищаем старые связи
        universal_cleaner(
            table_names=['drugs_drugsideeffect', 'drugs_sideeffectsgender', 'drugs_sideeffect'],
            model_classes=[DrugSideEffect, SideEffectsGender, SideEffect]
        ).clear_table()
        logger.info('Таблицы: DrugSideEffect, SideEffectsGender очищены')

        stats = {
            'drugs': None,
            'side_effects': None,
            'ranks': None,
        }
        
        try:
            stats['drugs'] = self._load_drugs()
            stats['side_effects'] = self._load_side_effects()
            stats['ranks'] = self._load_ranks()
        except IncorrectFile as e:
            logger.error(f"Загрузка прервана: {e}")
            raise
        except Exception as e:
            logger.exception(f"Непредвиденная ошибка: {e}")
            raise
        
        return stats

    @abstractmethod
    def _export_drugs(self):
        """Экспорт ЛС."""

    @abstractmethod
    def _export_side_effects(self):
        """Экспорт ПД."""

    @abstractmethod
    def _export_rangs(self):
        """Экспорт рангов."""

    def export_from_db(self):
        """Экспорт из БД."""
        self._export_drugs()
        self._export_side_effects()
        self._export_rangs()


class ExcelLoader(Loader):
    """Загрузчик из excel-файлов."""

    EXCEL_PATH = os.path.join(settings.TXT_DB_PATH,
                              'Список побочных эффектов edit_2.xlsx')
    EXPORT_PATH = os.path.join(settings.TXT_DB_PATH, 'TOSH_table.xlsx')

    # Листы
    RANKS_SHEET = 'Common'
    SIDE_EFFECTS_SHEET = 'Side_e'
    DRUGS_SHEET = 'Drugs'
    DRUG_SIDE_EFFECT = 'ЛС/ПЭ'
    EXPORT_DATE_SHEET = 'Export Date'
    
    # Колонки(общие)
    NUMBER_COLUMN = '№'
    # Колонки (препараты)
    DRUG_COLUMN = 'ЛС'
    # Колонки (побочные эффекты)
    EFFECT_COLUMN = 'эффект'
    EFFECT_COLUMN_EN = 'эффект_en'
    RANK_COLUMN = 'ранг'
    GENDER_COLUMN = 'пол'
    LIFE_THREATENING_COLUMN = 'жизнеугрожающий'

    # Доступный выбор
    GENDER_CHOICES = ['man', 'woman']

    def __init__(self, import_path=None, export_path=None, transpose=False):
        """
        Конструктор.

        Принимает путь к файл с данными.
        Если путь не указан, загружается из файл по умолчанию.
        
        Args:
            import_path: путь к файлу импорта
            export_path: путь для экспорта
            transpose: флаг транспонирования матрицы рангов
        """
        self.transpose = transpose  # Сохраняем флаг

        if import_path:
            self.import_path = import_path
        else:
            self.import_path = self.EXCEL_PATH
        if export_path:
            self.export_path = export_path
        else:
            now = datetime.now()
            self.date_in_name = now.strftime('%Y.%m.%d_%H.%M')
            self.date_in_sheet = now.strftime('%d.%m.%Y')
            self.time_in_name = now.strftime('%H:%M:%S')
            self.export_path = self.EXPORT_PATH.replace(
                '.xlsx', f'_{self.date_in_name}.xlsx')

    def _check_excel_file(self):
        """Проверка корректности excel-файла (регистронезависимо).
        
        Returns:
            list: Список строк с описанием ошибок. Пустой список = файл валиден.
        """
        errors = []
        
        try:
            excel_file = pd.ExcelFile(self.import_path)
        except Exception as e:
            return [f"Не удалось открыть файл: {e}"]

        # --- 1. Проверка листов ---
        required_sheets = [self.DRUGS_SHEET, self.SIDE_EFFECTS_SHEET, self.RANKS_SHEET]
        missing_sheets = [s for s in required_sheets if s not in excel_file.sheet_names]
        if missing_sheets:
            errors.append(f"Отсутствуют листы: {', '.join(missing_sheets)}")
            logger.error(f"Ошибки валидации: {'; '.join(errors)}")
            return errors

        # --- 2. Проверка колонок ---
        try:
            sheets_data = pd.read_excel(self.import_path, sheet_name=None)
            all_columns = [col for df in sheets_data.values() for col in df.columns]
            required_cols = [self.NUMBER_COLUMN, self.DRUG_COLUMN, self.EFFECT_COLUMN, self.RANK_COLUMN]
            missing_cols = [c for c in required_cols if c not in all_columns]
            if missing_cols:
                errors.append(f"Отсутствуют колонки: {', '.join(missing_cols)}")
                logger.error(f"Ошибки валидации: {'; '.join(errors)}")
                return errors
        except Exception as e:
            errors.append(f"Ошибка чтения таблиц: {e}")
            logger.error(f"Ошибки валидации: {'; '.join(errors)}")
            return errors

        # Загружаем данные листов один раз
        df_drugs = pd.read_excel(self.import_path, sheet_name=self.DRUGS_SHEET)
        df_effects = pd.read_excel(self.import_path, sheet_name=self.SIDE_EFFECTS_SHEET)

        # Нормализуем: удаляем NaN, приводим к строке, убираем пробелы, приводим к нижнему регистру
        drugs_clean = df_drugs[self.DRUG_COLUMN].dropna().astype(str).str.strip().str.lower()
        effects_ru_clean = df_effects[self.EFFECT_COLUMN].dropna().astype(str).str.strip().str.lower()
        effects_en_clean = df_effects[self.EFFECT_COLUMN_EN].dropna().astype(str).str.strip().str.lower()

        # Вспомогательная функция для форматирования сообщений
        def format_dupes(dupes, prefix):
            if not dupes:
                return None
            return f"{prefix}: {', '.join(map(str, dupes))}"

        # --- 3. Проверка дубликатов ВНУТРИ файла ---
        if err := format_dupes(drugs_clean[drugs_clean.duplicated(keep=False)].unique(),
                               "Дублируются ЛС в файле"):
            errors.append(err)
        if err := format_dupes(effects_ru_clean[effects_ru_clean.duplicated(keep=False)].unique(),
                               "Дублируются ПД (рус) в файле"):
            errors.append(err)
        if err := format_dupes(effects_en_clean[effects_en_clean.duplicated(keep=False)].unique(),
                               "Дублируются ПД (англ) в файле"):
            errors.append(err)

        if errors:
            logger.error(f"Ошибки валидации (структура файла): {'; '.join(errors)}")
            return errors  # Прерываем, если файл сам по себе некорректен

        # --- Итог ---
        if errors:
            logger.error(f"Ошибки валидации (данные в БД): {'; '.join(errors)}")
        else:
            logger.info(f"✅ Файл {self.import_path} успешно прошел все проверки")
            
        return errors

    def _load_drugs(self):
        """Загрузка ЛС — только существующие препараты."""
        df = pd.read_excel(self.import_path, sheet_name=self.DRUGS_SHEET)
        # Используем set, чтобы сразу хранить только уникальные значения
        not_found_drugs = set()
        
        logger.info('Загрузка ЛС началась')

        # Оптимизация: загружаем все существующие имена один раз, 
        # чтобы не делать запрос к БД в цикле (N+1 проблема)
        existing_drugs = set(Drug.objects.all().values_list('drug_name', flat=True))

        for drug in df.iloc[:, 1].dropna().to_list():
            drug_name = str(drug).strip().casefold()
            
            if drug_name not in existing_drugs:
                not_found_drugs.add(drug_name)
                logger.debug(f'Препарат не найден в БД: "{drug_name}"')
        
        # Формируем отчет
        if not_found_drugs:
            count = len(not_found_drugs)
            
            # 1. Полная информация — только в лог (для админа/разработчика)
            logger.error(
                f"Не найдено {count} препаратов.\n"
                f"Полный список отсутствующих ЛС: {not_found_drugs}"
            )
            
            # 2. Краткая информация — в исключение
            error_msg = (
                f"В файле обнаружены неизвестные препараты ({count} шт.).\n"
                f"Примеры: {', '.join(f'«{d}»' for d in not_found_drugs)}.\n"
            )
            
            # Используем конкретный тип ошибки, который вы определили ранее
            raise IncorrectFile(error_msg)
                
        logger.info(f'Проверка ЛС завершена успешно. Найдено в файле: {len(df)}, в БД: {Drug.objects.count()}')

    def _load_side_effects(self):
        """Загрузка ПД с обновлением существующих и обработкой пола."""

        df = pd.read_excel(self.import_path,
                        sheet_name=self.SIDE_EFFECTS_SHEET).fillna('')
        try:
            logger.info('Загрузка побочных действий началась')
            
            created_count = 0
            updated_count = 0
            gender_changes = 0
            
            for _, row in df.iterrows():
                side_effect = row[self.EFFECT_COLUMN]
                side_effect_en = row.get(self.EFFECT_COLUMN_EN, '')
                weight = row.get(self.RANK_COLUMN, 0.0)
                gender_value = row[self.GENDER_COLUMN]
                is_life_threatening = row.get(self.LIFE_THREATENING_COLUMN, '+')
                
                if not side_effect or not str(side_effect).strip():
                    logger.warning(f"Пропущена запись с пустым названием ПД")
                    continue
                
                # Создаём или обновляем SideEffect
                obj, created = SideEffect.objects.update_or_create(
                    se_name=side_effect.strip().lower(),
                    defaults={
                        'se_name_en': side_effect_en.strip().lower() if side_effect_en else '',
                        'weight': weight if weight is not None else 0.0,
                        'is_life_threatening': is_life_threatening.strip() == '+'
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                
                # Обработка пола
                if gender_value and gender_value in self.GENDER_CHOICES:
                    _, gender_created = SideEffectsGender.objects.update_or_create(
                        side_effect=obj,
                        gender=gender_value
                    )
                    gender_changes += 1
            
            logger.info(f'Побочных действий: создано {created_count}, обновлено {updated_count}')
            logger.info(f'Изменений в связях по полу: {gender_changes}')
            logger.info(f'Всего в БД: SideEffect: {SideEffect.objects.count()}, SideEffectsGender: {SideEffectsGender.objects.count()}')
            
        except Exception as error:
            logger.error(f'Ошибка при загрузке ПД: {error}')
            raise Exception(f'Проблема с загрузкой ПД: {error}')

    def _load_ranks(self) -> dict:
        """
        Загружает ранги для ВСЕХ комбинаций препаратов и побочных эффектов из БД.
        Требует, чтобы в Excel были указаны ранги для каждой возможной пары.
        """

        # Функция нормализации
        def normalize_name(name):
            return str(name).lower().strip()

        # 1. Все объекты из БД
        all_drugs = list(Drug.objects.all())
        all_effects = list(SideEffect.objects.all())
        total_pairs = len(all_drugs) * len(all_effects)

        # Множества нормализованных имён из БД
        drug_names_db = {normalize_name(drug.drug_name) for drug in all_drugs}
        effect_names_db = {normalize_name(effect.se_name) for effect in all_effects}

        # 2. Читаем Excel и строим словарь рангов
        df = pd.read_excel(self.import_path, sheet_name=self.RANKS_SHEET)
        df = df.iloc[0:, 1:].reset_index(drop=True).fillna(0)

        # Чтение заголовков (в зависимости от транспонирования)
        if self.transpose:
            drug_names_from_file = [normalize_name(name) for name in df.iloc[0, 1:].values]
            effect_names_from_file = [normalize_name(name) for name in df.iloc[1:, 0].values]
        else:
            drug_names_from_file = [normalize_name(name) for name in df.iloc[1:, 0].values]
            effect_names_from_file = [normalize_name(name) for name in df.iloc[0, 1:].values]

        # Очистка
        drug_names_from_file = [n for n in drug_names_from_file if n and n != 'nan']
        effect_names_from_file = [n for n in effect_names_from_file if n and n != 'nan']

        # Данные рангов (матрица)
        data_df = df.iloc[1:, 1:].reset_index(drop=True).fillna(0)
        if self.transpose:
            data_df = data_df.T.reset_index(drop=True)

        # Проверка размерности (количество имён должно совпадать с размером матрицы)
        assert data_df.shape == (len(drug_names_from_file), len(effect_names_from_file)), \
            "Размерность данных не совпадает с заголовками"

        # Словарь: (drug_name, effect_name) -> rank
        rank_dict = {}
        for i, drug_name in enumerate(drug_names_from_file):
            for j, effect_name in enumerate(effect_names_from_file):
                rank_dict[(drug_name, effect_name)] = data_df.iloc[i, j]

        # 3. Генерируем все ожидаемые пары из БД
        missing_drugs = drug_names_db - set(drug_names_from_file)
        missing_effects = effect_names_db - set(effect_names_from_file)

        # 4. Строгая валидация: никаких пропусков и лишних пар
        errors = []
        if missing_drugs:
            errors.append(f"В файле отсутствуют препараты: {len(missing_drugs)} (пример: {list(missing_drugs)[:5]})")
        if missing_effects:
            errors.append(f" файле отсутствуют побочные эффекты: {len(missing_effects)} (пример: {list(missing_effects)[:5]})")

        if errors:
            full_msg = (
                f"Ошибка валидации рангов в файле '{os.path.basename(self.import_path)}':\n"
                + "\n - ".join(errors)
            )
            logger.error(full_msg)
            raise IncorrectFile(full_msg)

        # 5. Формируем список для загрузки (все пары из БД, ранг из файла или 0, но при валидации все пары есть)
        bulk = []
        for drug in all_drugs:
            drug_norm = drug.drug_name.lower().strip()
            for effect in all_effects:
                effect_norm = effect.se_name.lower().strip()
                rank = rank_dict.get((drug_norm, effect_norm), 0)
                bulk.append(DrugSideEffect(
                    drug=drug,
                    side_effect=effect,
                    rang_base=rank
                ))

        # 6. Загрузка
        DrugSideEffect.objects.bulk_create(bulk, batch_size=500)
        logger.info(f"✅ Загружено рангов: {len(bulk)} (все возможные пары)")

        # 7. Статистика (теперь pairs_found == total_pairs)
        return {
            'pairs_expected': total_pairs,
            'pairs_loaded': len(bulk),
            'drugs_in_db': len(all_drugs),
            'effects_in_db': len(all_effects),
        }

    def load_to_db(self):
        """Загрузка в БД всех данных."""
        return super().load_to_db()

    def _export_drugs(self):
        """Экспорт ЛС."""
        drugs = Drug.objects.order_by('id')
        numbers = [drug.id for drug in drugs]
        drug_names = [drug.drug_name for drug in drugs]
        self.drugs_df = pd.DataFrame(
            {
                self.NUMBER_COLUMN: numbers,
                self.DRUG_COLUMN: drug_names
            }
        )

    def _export_side_effects(self):
        """Экспорт ПД."""
        side_effects = SideEffect.objects.order_by('id')
        numbers = [side_effect.id for side_effect in side_effects]
        side_effect_names = [side_effect.se_name for side_effect in side_effects]
        side_effect_names_en = [side_effect.se_name_en for side_effect in side_effects]
        weights = [side_effect.weight for side_effect in side_effects]

        self.side_effects_df = pd.DataFrame(
            {
                self.NUMBER_COLUMN: numbers,
                self.EFFECT_COLUMN: side_effect_names,
                self.EFFECT_COLUMN_EN: side_effect_names_en,
                self.RANK_COLUMN: weights
            }
        )

    def _export_rangs(self):
        """Экспорт рангов."""
        side_effects = SideEffect.objects.order_by('id')
        drugs = Drug.objects.order_by('id')
        column_headers = [side_effect.id for side_effect in side_effects]
        side_effect_names = [side_effect.se_name for side_effect in side_effects]

        rows = []
        rows.append(side_effect_names)

        for drug in drugs:
            row = []
            for effect in side_effects:
                try:
                    dse = DrugSideEffect.objects.get(drug=drug, side_effect=effect)
                    row.append(dse.rang_base)  # или другой ранг
                except DrugSideEffect.DoesNotExist:
                    logger.info('Нет таблицы рангов')
            rows.append(row)

        df = pd.DataFrame(rows, columns=column_headers)

        with pd.ExcelWriter(self.export_path, engine='openpyxl') as writer:
            self.drugs_df.to_excel(writer,
                                   sheet_name=self.DRUGS_SHEET,
                                   index=False,
                                   startcol=0)
            self.side_effects_df.to_excel(writer,
                                          sheet_name=self.SIDE_EFFECTS_SHEET,
                                          index=False,
                                          startcol=0)

            self.drugs_df.columns = [''] * len(self.drugs_df.columns)
            new_row = pd.DataFrame([[None, self.DRUG_SIDE_EFFECT]], columns=self.drugs_df.columns)
            self.drugs_df = pd.concat([new_row, self.drugs_df], ignore_index=True)

            df_combined = pd.concat([self.drugs_df, df], ignore_index=False, axis=1)

            df_combined.to_excel(writer, sheet_name=self.RANKS_SHEET, index=False)

    def _add_export_date_sheet(self):
        """Добавляет отдельный лист с текущей датой экспорта."""
        df = pd.DataFrame(
            {
                'Дата экспорта данных о рангах из БД': [
                    self.date_in_sheet],
                'Время экспорта данных о рангах из БД': [
                    self.time_in_name]
            }
        )

        with pd.ExcelWriter(self.export_path,
                            engine='openpyxl',
                            mode='a',
                            if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=self.EXPORT_DATE_SHEET, index=False)

    def export_from_db(self):
        """Экспорт из БД."""

        open(self.export_path, 'w', encoding='utf-8').close()
        super().export_from_db()
        self._add_export_date_sheet()
