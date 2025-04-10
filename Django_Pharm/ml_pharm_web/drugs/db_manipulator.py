from tqdm import tqdm
from .models import Drug, SideEffect, DrugSideEffect
from django.contrib.auth.models import User
from .models import DrugGroup
from django.utils.text import slugify


class DBManipulator:
    """Загрузчик БД."""

    DRUGS_PATH = '..\\ml_pharm_web\\txt_files_db\\drugs_xcn.txt'
    SIDE_EFFECTS_PATH = '..\\ml_pharm_web\\txt_files_db\\side_effects.txt'
    RANGS_PATH = '..\\ml_pharm_web\\txt_files_db\\rangs.txt'

    @classmethod
    def __load_drugs(cls):
        """Метод загрузки ЛС."""
        try:
            # Получим или создадим дефолтного пользователя и группу
            default_user, _ = User.objects.get_or_create(username='import_user')
            default_group, _ = DrugGroup.objects.get_or_create(
                title='Импортированная группа',
                defaults={
                    'user': default_user,
                    'slug': 'import-group'
                }
            )

            with open(cls.DRUGS_PATH, 'r', encoding='utf-8') as file:
                for i, line in enumerate(file):
                    if not line.strip():
                        continue
                    name = line.strip().split('\t')[1]
                    base_slug = slugify(name)
                    slug = base_slug
                    counter = 1
                    while Drug.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1

                    Drug.objects.create(
                        name=name,
                        user=default_user,
                        slug=slug,
                        pg=default_group
                    )
            print('ЛС успешно сохранены!')
        except Exception as error:
            raise Exception(f'Проблема с загрузкой ЛС: {error}')

    @classmethod
    def __load_side_effects(cls):
        """Метод загрузки ПД."""
        try:
            with open(cls.SIDE_EFFECTS_PATH, 'r', encoding='utf-8') as file:
                for line in [l.strip() for l in file if l.strip()]:
                    name = line.split('\t')[1].replace(';', '')
                    SideEffect.objects.create(name=name)
            print('ПД успешно сохранены!')
        except Exception as error:
            raise Exception(f'Проблема с загрузкой побочных эффектов: {error}')

    @classmethod
    def __load_file(cls, path):
        """Метод загрузки из файла."""
        with open(path, 'r', encoding='utf-8') as file:
            return [line.strip().replace(',', '.') for line in file if line.strip()]

    @classmethod
    def __load_rangs(cls):
        """Метод загрузки коэффициентов побочных эффектов."""
        rangs = cls.__load_file(cls.RANGS_PATH)

        drugs = list(Drug.objects.order_by('id'))
        effects = list(SideEffect.objects.order_by('id'))

        assert len(rangs) == len(drugs) * len(effects), "Размерность рангов не совпадает"

        idx = 0
        for drug in tqdm(drugs, ncols=80):
            for effect in effects:
                DrugSideEffect.objects.create(
                    drug=drug,
                    side_effect=effect,
                    probability=float(rangs[idx])
                )
                idx += 1

    def load_to_db(self):
        """Метод загрузки данных в БД."""
        self.__load_drugs()
        self.__load_side_effects()
        self.__load_rangs()
        return DrugSideEffect.objects.count()

    def clean_db(self):
        """
        Метод очистки таблиц:
        - DrugSideEffect;
        - Drug;
        - SideEffect.
        """
        DrugSideEffect.objects.all().delete()
        Drug.objects.all().delete()
        SideEffect.objects.all().delete()

    def export_from_db(self):
        """Метод экспорта из БД."""
        pass  # пока заглушка
