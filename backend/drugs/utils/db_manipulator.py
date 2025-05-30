"""Модуль загрузки лекарств."""

import os
import logging

from django.conf import settings

from ..models import (DrugGroup,
                      Drug,
                      DrugSideEffect,
                      SideEffect)
from drugs.utils.loaders import Loader


logger = logging.getLogger('drugs')


class DBManipulator(Loader):
    """Загрузчик БД."""

    DRUGS_PATH = os.path.join(settings.TXT_DB_PATH, 'drugs_xcn.txt')
    SIDE_EFFECTS_PATH = os.path.join(settings.TXT_DB_PATH, 'side_effects.txt')
    RANGS_PATH = os.path.join(settings.TXT_DB_PATH, 'rangs.txt')
    RANGSF1_PATH = os.path.join(settings.TXT_DB_PATH, 'rangf1.txt')
    RANGSF2_PATH = os.path.join(settings.TXT_DB_PATH, 'rangf2.txt')
    RANGSM1_PATH = os.path.join(settings.TXT_DB_PATH, 'rangm1.txt')
    RANGSM2_PATH = os.path.join(settings.TXT_DB_PATH, 'rangm2.txt')
    RANGSBASE_PATH = os.path.join(settings.TXT_DB_PATH, 'rangbase.txt')
    RANGSFREQ_PATH = os.path.join(settings.TXT_DB_PATH, 'rangfreq.txt')

    @classmethod
    def _load_drugs(cls):
        """Метод загрузки ЛС."""
        try:
            logger.info('Загрузка ЛС началась')
            group, _ = DrugGroup.objects.get_or_create(
                id=1,
                defaults={'dg_name': 'Общая группа'})
            with open(cls.DRUGS_PATH, 'r', encoding='utf-8') as file:
                for drug in [drug.strip() for drug in file if drug != '\n']:
                    Drug.objects.create(drug_name=drug.split('\t')[1].strip(),
                                        drug_group=group)
            logger.info(f'Загружено ЛС: {Drug.objects.count()}')
        except Exception as error:
            raise Exception(f'Проблема с загрузкой ЛС: {error}')

    @classmethod
    def _load_side_effects(cls):
        """Метод загрузки ПД."""
        try:
            logger.info('Загрузка побочных действий началась')
            with open(cls.SIDE_EFFECTS_PATH, 'r', encoding='utf-8') as file:
                for s_e in [s_e.strip() for s_e in file if s_e != '\n']:
                    SideEffect.objects.create(
                        se_name=s_e.split('\t')[1].replace(';', '').strip(),
                        weight=float(
                            s_e.split('\t')[2].replace(',', '.').strip()))
            logger.info(f'Загружено побочных действий: {SideEffect.objects.count()}')
        except Exception as error:
            raise Exception(f'Проблема с загрузкой {error}')

    @classmethod
    def __load_file(cls, path):
        """Метод загрузки из файла."""
        with open(path, 'r', encoding='utf-8') as file:
            return [line.strip().replace(',', '.')
                    for line in file if line.strip()]

    @classmethod
    def _load_ranks(cls):
        """Метод загрузки рангов."""
        rangs = cls.__load_file(cls.RANGS_PATH)
        rangsf1 = cls.__load_file(cls.RANGSF1_PATH)
        rangsf2 = cls.__load_file(cls.RANGSF2_PATH)
        rangsm1 = cls.__load_file(cls.RANGSM1_PATH)
        rangsm2 = cls.__load_file(cls.RANGSM2_PATH)
        rangsbase = cls.__load_file(cls.RANGSBASE_PATH)
        rangsfreq = cls.__load_file(cls.RANGSFREQ_PATH)

        drugs = list(Drug.objects.order_by('id'))
        effects = list(SideEffect.objects.order_by('id'))
        assert len(rangs) == len(drugs) * len(effects), (
            "Размерность рангов не совпадает!")

        idx = 0
        for drug in drugs:
            for effect in effects:
                DrugSideEffect.objects.create(
                    drug=drug,
                    side_effect=effect,
                    rang_base=float(rangsbase[idx]),
                    rang_f1=float(rangsf1[idx]),
                    rang_f2=float(rangsf2[idx]),
                    rang_m1=float(rangsm1[idx]),
                    rang_m2=float(rangsm2[idx]),
                    probability=float(rangs[idx]),
                    rang_freq=float(rangsfreq[idx])
                )
                idx += 1
                logger.info(f"Прогресс: {idx}/{len(effects)*len(drugs)} итераций")

        logger.info(f'Загружено рангов: {idx}') 

    def load_to_db(self):
        """Метод загрузки данных в БД."""
        super().load_to_db()
        return DrugSideEffect.objects.count()

    def clean_db(self):
        """
        Метод очистки таблиц.

        Очищаются таблицы:
        - DrugGroup;
        - Drug;
        - SifeEffect;
        - DrugSifeEffect.
        """
        DrugGroup.objects.all().delete()
        DrugSideEffect.objects.all().delete()
        Drug.objects.all().delete()
        SideEffect.objects.all().delete()

    @classmethod
    def _export_drugs(cls):
        """Метод экспорта ЛС из БД в файл."""
        try:
            with open(cls.DRUGS_PATH, 'w', encoding='utf-8') as file:
                for i, drug in enumerate(
                    Drug.objects.order_by('id').iterator(),
                        start=1):
                    file.write(f'{i}\t{drug.drug_name}\n')
        except Exception as error:
            message = f'Проблема при экспорте ЛС в файл: {error}'
            logger.error(message)
            raise Exception(message)

    @classmethod
    def _export_side_effects(cls):
        """Метод экспорта ПД из БД в файл."""
        try:
            with open(cls.SIDE_EFFECTS_PATH, 'w', encoding='utf-8') as file:
                for i, effect in enumerate(
                    SideEffect.objects.order_by('id').iterator(),
                        start=1):
                    file.write(f'{i}\t{effect.se_name};\t{effect.weight}\n')
        except Exception as error:
            message = f'Проблема при экспорте ПД в файл: {error}'
            logging.error(message)
            raise Exception(message)

    @classmethod
    def __clean_file(cls, path):
        """Метод очистки файла."""
        with open(path, 'r+', encoding='utf-8') as file:
            file.truncate(0)

    @classmethod
    def __clean_rang_files(cls):
        """Метод очистки всех файлов с рагнами."""
        cls.__clean_file(cls.RANGS_PATH)
        cls.__clean_file(cls.RANGSBASE_PATH)
        cls.__clean_file(cls.RANGSFREQ_PATH)
        cls.__clean_file(cls.RANGSM1_PATH)
        cls.__clean_file(cls.RANGSM2_PATH)
        cls.__clean_file(cls.RANGSF1_PATH)
        cls.__clean_file(cls.RANGSF2_PATH)

    @classmethod
    def _export_rangs(cls):
        """Метод экспорта рангов из БД в файл."""
        try:
            cls.__clean_rang_files()

            drugs = list(Drug.objects.order_by('id'))
            effects = list(SideEffect.objects.order_by('id'))

            relations  = DrugSideEffect.objects.select_related('drug', 'side_effect').all()
            relation_map = {(relation.drug_id, relation.side_effect_id): relation
                      for relation in relations }

            files_content = {
                cls.RANGS_PATH: [],
                cls.RANGSBASE_PATH: [],
                cls.RANGSFREQ_PATH: [],
                cls.RANGSF1_PATH: [],
                cls.RANGSF2_PATH: [],
                cls.RANGSM1_PATH: [],
                cls.RANGSM2_PATH: []
            }

            for drug in drugs:
                for effect in effects:
                    relation = relation_map[(drug.id, effect.id)]
                    files_content[cls.RANGS_PATH].append(f"{relation.probability}\n")
                    files_content[cls.RANGSBASE_PATH].append(f"{relation.rang_base}\n")
                    files_content[cls.RANGSFREQ_PATH].append(f"{relation.rang_freq}\n")
                    files_content[cls.RANGSF1_PATH].append(f"{relation.rang_f1}\n")
                    files_content[cls.RANGSF2_PATH].append(f"{relation.rang_f2}\n")
                    files_content[cls.RANGSM1_PATH].append(f"{relation.rang_m1}\n")
                    files_content[cls.RANGSM2_PATH].append(f"{relation.rang_m2}\n")

            for path, lines in files_content.items():
                with open(path, 'w', encoding='utf-8') as file:
                    file.writelines(lines)

        except Exception as error:
            message = f'Проблема при экспорте рангов в файл: {error}'
            logger.error(message)
            raise Exception(message)

    def export_from_db(self):
        """Метод экспорта из БД."""
        super().export_from_db()
