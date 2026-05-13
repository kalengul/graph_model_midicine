import logging

from drugs.models import (  BannedDrugPair,
                        DrugSideEffect,
                        Drug,
                        SideEffect,
                        DrugGroup,
                        Nosology,
                        DrugsAgeContraindications,
                        SideEffectsGender,
                        TradeName)
from contraindications.models import Contraindication
from .banned_pairs_loader import JSONBannedPairLoader
from contraindications.utils.loader import LoadAndBuildDrugContraindications
from drugs.utils.universal_cleaner import universal_cleaner

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
            'trade_names_created': 0,
            'trade_names_updated': 0,
            'age_contraindications_created': 0,
            'errors':[]
        }

    def load_all(self, data):
        """Загрузка всех данных."""
        if self.clear_before_load:
            logger.info('Очистка таблиц БД: Противопоказания; Запрещенные пары; '
                        'Побочные эффекты; Нозологии; Возрастные противопоказания; '
                        'Группы препаратов; Торговые наименования; Препараты; '
                        'Половая принадлежность побочного эффекта; '
                        )
            universal_cleaner(
                model_classes=[ Drug,
                                DrugGroup,
                                DrugsAgeContraindications,
                                DrugSideEffect,
                                Contraindication,
                                BannedDrugPair,
                                SideEffect,
                                Nosology,
                                SideEffectsGender,
                                TradeName
                                ]
            ).clear_table()

        logger.info(f'Загрузка групп...')
        self._load_groups_and_link_drugs(data)

        logger.info(f'Загрузка запрещенных пар...')
        self._load_banned(data)

        logger.info(f'Загрузка противопоказаний...')
        self._load_contraindications(data)

        logger.info(f'Загрузка возрастных противопоказаний...')
        self._load_age_contraindications(data)

        logger.info(f'Загрузка торговых наименований...')
        self._load_trade_names(data)

        logger.info(f"Загрузка завершена: {self.stats}")
        return self.stats
    
    def _load_trade_names(self, data):
        """
        Загрузка торговых названий.
        
        Формат данных:
        [
            {
                "drug": "амброксол",
                "trade_name": ["амбробене", "амброксол", ...],
                ...
            },
            ...
        ]
        """
        
        for item in data:
            # Извлекаем основное МНН и торговые названия
            drug_name = item.get('drug', '').strip().casefold()
            trade_names = item.get('trade_name', [])
            nosology_name = item.get('nosology', 'общая нозология')
            
            if not drug_name:
                self.stats['errors'].append("Пропущена запись: отсутствует поле 'drug'")
                continue
            
            try:
                # Пытаемся найти существующее МНН
                drug = Drug.objects.get(drug_name__iexact=drug_name)
            except Drug.DoesNotExist:
                self.stats['errors'].append(f"МНН '{drug_name}' не найдено в базе данных")
                continue
            except Exception as e:
                self.stats['errors'].append(f"Ошибка при поиске МНН '{drug_name}': {str(e)}")
                continue
            
            if not isinstance(trade_names, list):
                self.stats['errors'].append(f"Для {drug_name}: поле 'trade_name' не является списком")
                continue
            
            # Загружаем торговые названия
            for trade_name in trade_names:
                trade_name = trade_name.strip()
                if not trade_name:
                    continue
                
                try:
                    trade_obj, created = TradeName.objects.get_or_create(
                        name=trade_name,
                        defaults={'drug': drug}
                    )
                    
                    if created:
                        self.stats['trade_names_created'] += 1
                    else:
                        # Если уже существует, но привязан к другому МНН - обновляем
                        if trade_obj.drug != drug:
                            trade_obj.drug = drug
                            trade_obj.save()
                            self.stats['trade_names_updated'] += 1
                            
                except Exception as e:
                    self.stats['errors'].append(f"Ошибка при сохранении торгового названия '{trade_name}' для {drug_name}: {str(e)}")
        
        return {k: v
                for k, v in self.stats.items()
                if k in ['trade_names_created', 'trade_names_updated', 'errors']}

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
            drug_name = item.get('drug')
            if not drug_name:
                continue
            try:
                drug = Drug.objects.get(drug_name__iexact=drug_name)
            except Drug.DoesNotExist:
                logger.warning(f"Препарат '{drug_name}' не найден при загрузке возрастных ограничений")
                continue

            banned_under_age = item.get('banned_under_age')
            banned_after_age = item.get('banned_after_age')
            if banned_under_age is None and banned_after_age is None:
                continue

            # update_or_create, чтобы не плодить дубликаты
            obj, created = DrugsAgeContraindications.objects.update_or_create(
                drug=drug,
                defaults={
                    'age_from': banned_under_age,
                    'age_to': banned_after_age,
                }
            )
            if created:
                self.stats['age_contraindications_created'] += 1