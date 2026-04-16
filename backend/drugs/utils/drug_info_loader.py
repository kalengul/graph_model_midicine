import logging

from ..models import Drug, DrugGroup, BannedDrugPair, Nosology, DrugsAgeContraindications, TradeName
from .banned_pairs_loader import JSONBannedPairLoader
from contraindications.utils.loader import LoadAndBuildDrugContraindications
from contraindications.utils.cleaner import ContraindicationCleanProcessor
from drugs.utils.cleaner import DrugCleanProcessor, BannedDrugPairCleanProcessor


logger = logging.getLogger(__name__)


class DrugDataLoader:
    """Загрузчик данных о ЛС."""

    def __init__(self, clear_before_load=True):
        self.clear_before_load = clear_before_load
        self.loader_banned = JSONBannedPairLoader()
        self.loader_contra = LoadAndBuildDrugContraindications()
        self.stats = {
            'drug_groups': 0,
            'drugs_updated': 0,
            'banned_pairs': 0,
            'contraindications': 0,
            'nosology': 0,
            'tradenames': 0,
            'age_contraindications': 0,
        }

    def load_all(self, data):
        """Загрузка всех данных."""
        if self.clear_before_load:
            logger.info('Очистка таблиц БД: Противопоказания; Запрещенные пары; Препараты')
            # Противопоказания
            ContraindicationCleanProcessor().get_cleaner().clean()
            BannedDrugPairCleanProcessor().get_cleaner().clear_table()
            DrugCleanProcessor().get_cleaner().clear_table()

            # Запрещенные пары
            self.loader_banned.clear_db()

        # Загрузка групп
        logger.info(f'Загрузка групп...')
        self._load_groups_and_link_drugs(data)

        # Загрузка запрещенных пар
        logger.info(f'Загрузка запрещенных пар...')
        self._load_banned(data)

        # Загрузка противопоказаний
        logger.info(f'Загрузка противопоказаний...')
        self._load_contraindications(data)

        # Загрузка возрастных противопоказаний
        logger.info(f'Загрузка возрастных противопоказаний...')
        self._load_age_contraindications(data)

        logger.info(f"Загрузка завершена: {self.stats}")
        return self.stats
    
    def load_trade_names(self, trade_names_data):
        """
        Загрузка торговых названий.
        
        Формат данных:
        {
            "гликлазид": ["глидиаб", "глидиаб мв", ...],
            "ибупрофен": ["бруфен ср", "бумидол®", ...]
        }
        """
        stats = {
            'trade_names_processed': 0,
            'trade_names_created': 0,
            'trade_names_updated': 0,
            'errors': []
        }
        
        for drug_name, trade_names in trade_names_data.items():
            drug_name = drug_name.strip().casefold()
            
            try:
                drug = Drug.objects.get(drug_name__iexact=drug_name)
            except Drug.DoesNotExist:
                nosology, _ = Nosology.objects.get_or_create(name='общая нозология')
                drug = Drug.objects.create(
                    drug_name=drug_name,
                    nosology=nosology
                )
                stats['trade_names_processed'] += 1
                logger.info(f"Создано новое МНН: {drug_name}")
            
            if not isinstance(trade_names, list):
                stats['errors'].append(f"Для {drug_name}: данные не являются списком")
                continue
            
            # Загружаем торговые названия
            for trade_name in trade_names:
                trade_name = trade_name.strip()
                if not trade_name:
                    continue
                
                trade_obj, created = TradeName.objects.get_or_create(
                    name=trade_name,
                    defaults={'drug': drug}
                )
                
                if created:
                    stats['trade_names_created'] += 1
                else:
                    # Если уже существует, но привязан к другому МНН - обновляем
                    if trade_obj.drug != drug:
                        trade_obj.drug = drug
                        trade_obj.save()
                        stats['trade_names_updated'] += 1
            
            stats['trade_names_processed'] += 1
        
        logger.info(f"Загрузка торговых названий завершена: {stats}")
        return stats

    def _load_groups_and_link_drugs(self, data):
        """Загрузка групп и связывание с лекарствами."""

        # Создание общей нозологии
        nosology_default, nosology_default_created = Nosology.objects.get_or_create(
                name='общая нозология'
            )
        
        for item in data:
            drug_name = item.get('drug', '').strip()
            groups = item.get('group', [])
            nosology_name = item.get('nosology', '').strip()
            
            if not drug_name:
                continue
            
            drug, _ = Drug.objects.get_or_create(
                drug_name__iexact=drug_name,
                defaults={'drug_name': drug_name}
            )
            
            if groups:
                for group_name in groups:
                    if group_name:
                        group, group_created = DrugGroup.objects.get_or_create(
                            dg_name__iexact=group_name,
                            defaults={'dg_name': group_name}
                        )
                        if group_created:
                            self.stats['drug_groups'] += 1
                        
                        drug.drug_groups.add(group)
                
                self.stats['drugs_updated'] += 1
            
            if nosology_name:
                nosology, nosology_created = Nosology.objects.get_or_create(
                    name__iexact=nosology_name,
                    defaults={'name': nosology_name}
                )
                if nosology_created:
                    self.stats['nosology'] = self.stats.get('nosology', 0) + 1
                
                # Если отличается, то обновить
                if drug.nosology != nosology:
                    drug.nosology = nosology
                    drug.save(update_fields=['nosology'])
            
            # Если нет, то устанавливается по дефолту
            else:
                drug.nosology = nosology_default
                drug.save(update_fields=['nosology'])

    def _load_banned(self, data):
        """Загрузка запрещенных пар через существующий загрузчик."""
        # Сохраняем статистику
        old_count = BannedDrugPair.objects.count()
        
        # Используем существующий загрузчик
        self.loader_banned.load_to_db(data=data)
        
        # Считаем новые пары
        new_count = BannedDrugPair.objects.count()
        self.stats['banned_pairs'] = new_count - old_count

    def _load_contraindications(self, data):
        """Загрузка противопоказаний через существующий загрузчик."""
        # Сохраняем статистику
        old_count = Drug.contraindications.through.objects.count()
        
        # Используем существующий загрузчик
        self.loader_contra.load(data=data)

        # Загрузка из словаря
        self.loader_contra.load_from_keys()
        
        # Считаем новые связи
        new_count = Drug.contraindications.through.objects.count()
        self.stats['contraindications'] = new_count - old_count

    def _load_age_contraindications(self, data):
        """Загрузка возрастных противопоказаний."""
        
        for item in data:
            drug_name = item.get('drug', '').strip()
            
            if not drug_name:
                continue
            
            # Получаем препарат
            try:
                drug = Drug.objects.get(drug_name__iexact=drug_name)
            except Drug.DoesNotExist:
                logger.warning(f"Препарат '{drug_name}' не найден при загрузке возрастных ограничений")
                continue
            
            # Обрабатываем banned_under_18
            banned_under_age = item.get('banned_under_age')
            banned_after_age = item.get('banned_after_age')
            if banned_under_age is not None or banned_after_age is not None:
                DrugsAgeContraindications.objects.create(
                    drug=drug,
                    age_from=banned_under_age,
                    age_to=banned_after_age,
                )
                self.stats['age_contraindications'] += 1
            