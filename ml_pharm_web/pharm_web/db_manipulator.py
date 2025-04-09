"""Модуль загрузки лекарств."""

# from tqdm import tqdm

from pharm_web.models import (Medication,
                              SideEffect,
                              MedicationSideEffect)


class DBManipulator:
    """Загрузчик БД."""

    DRUGS_PATH = '..\\ml_pharm_web\\txt_files_db\\drugs_xcn.txt'
    SIDE_EFFECTS_PATH = '..\\ml_pharm_web\\txt_files_db\\side_effects.txt'
    RANGS_PATH = '..\\ml_pharm_web\\txt_files_db\\rangs.txt'
    RANGSF1_PATH = '..\\ml_pharm_web\\txt_files_db\\rangf1.txt'
    RANGSF2_PATH = '..\\ml_pharm_web\\txt_files_db\\rangf2.txt'
    RANGSM1_PATH = '..\\ml_pharm_web\\txt_files_db\\rangm1.txt'
    RANGSM2_PATH = '..\\ml_pharm_web\\txt_files_db\\rangm2.txt'
    RANGSBASE_PATH = '..\\ml_pharm_web\\txt_files_db\\rangbase.txt'
    RANGSFREQ_PATH = '..\\ml_pharm_web\\txt_files_db\\rangfreq.txt'

    @classmethod
    def __load_drugs(cls):
        """Метод загрузки ЛС."""
        try:
            with open(cls.DRUGS_PATH, 'r', encoding='utf-8') as file:
                for drug in [drug.strip() for drug in file if drug != '\n']:
                    Medication.objects.create(name=drug.split('\t')[1])
            print('ЛС успешно сохранены!')
        except Exception as error:
            raise Exception(f'Проблема с загрузкой ЛС: {error}')

    @classmethod
    def __load_side_effects(cls):
        """Метод загрузки ПД."""
        try:
            with open(cls.SIDE_EFFECTS_PATH, 'r', encoding='utf-8') as file:
                for s_e in [s_e.strip() for s_e in file if s_e != '\n']:
                    SideEffect.objects.create(
                        name=s_e.split('\t')[1].replace(';', ''),
                        weight=float(s_e.split('\t')[2].replace(',', '.')))
            print('ПД успешно сохранены!')
        except Exception as error:
            raise Exception(f'Проблема с загрузкой {error}')

    @classmethod
    def __load_file(cls, path):
        """Метод загрузки из файла."""
        with open(path, 'r', encoding='utf-8') as file:
            return [line.strip().replace(',', '.')
                    for line in file if line.strip()]

    @classmethod
    def __load_rangs(cls):
        """Метод загрузки рангов."""
        rangs = cls.__load_file(cls.RANGS_PATH)
        rangsf1 = cls.__load_file(cls.RANGSF1_PATH)
        rangsf2 = cls.__load_file(cls.RANGSF2_PATH)
        rangsm1 = cls.__load_file(cls.RANGSM1_PATH)
        rangsm2 = cls.__load_file(cls.RANGSM2_PATH)
        rangsbase = cls.__load_file(cls.RANGSBASE_PATH)
        rangsfreq = cls.__load_file(cls.RANGSFREQ_PATH)

        drugs = list(Medication.objects.order_by('id'))
        effects = list(SideEffect.objects.order_by('id'))

        print('len(drugs) =', len(drugs))
        print('len(effects) =', len(effects))
        assert len(rangs) == len(drugs) * len(effects), "Размерность рангов не совпадает"

        idx = 0
        for drug in tqdm(drugs, ncols=80):
            for effect in effects:
                MedicationSideEffect.objects.create(
                    medication=drug,
                    side_effect=effect,
                    rang_base=float(rangsbase[idx]),
                    rang_f1=float(rangsf1[idx]),
                    rang_f2=float(rangsf2[idx]),
                    rang_m1=float(rangsm1[idx]),
                    rang_m2=float(rangsm2[idx]),
                    rang_s=float(rangs[idx]),
                    rang_freq=float(rangsfreq[idx])
                )
                idx += 1

    def load_to_db(self):
        """Метод загрузки данных в БД."""
        self.__load_drugs()
        self.__load_side_effects()
        self.__load_rangs()
        return MedicationSideEffect.objects.count()

    def clean_db(self):
        """
        Метод очистки таблиц.

        Очищаются таблицы:
        - Medication;
        - SifeEffect;
        - MedicationSifeEffect.
        """
        MedicationSideEffect.objects.all().delete()
        Medication.objects.all().delete()
        SideEffect.objects.all().delete()

    def export_from_db(self):
        """Метод экспорта из БД."""
