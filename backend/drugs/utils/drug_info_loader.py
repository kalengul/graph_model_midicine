import logging

from drugs.models import (  BannedDrugPair,
                        Drug,
                        DrugGroup,
                        Nosology,
                        DrugsAgeContraindications,
                        TradeName)
from side_effects.models import DrugSideEffect, SideEffect, SideEffectsGender
from contraindications.models import Contraindication
from drugs.utils.banned_pairs_loader import JSONBannedPairLoader
from contraindications.utils.loader import LoadAndBuildDrugContraindications
from drugs.utils.universal_cleaner import universal_cleaner
from django.db import transaction


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
                model_classes=[
                    DrugsAgeContraindications,
                    DrugSideEffect,
                    SideEffectsGender,
                    TradeName,
                    BannedDrugPair,
                    Contraindication,
                    DrugGroup,
                    Drug,
                    Nosology,
                    SideEffect,
                ]
            ).clear_table()

        logger.warning(f'Загрузка групп...')
        self._load_groups_and_link_drugs(data)

        logger.warning(f'Загрузка запрещенных пар...')
        self._load_banned(data)

        logger.warning(f'Загрузка противопоказаний...')
        self._load_contraindications(data)

        logger.warning(f'Загрузка возрастных противопоказаний...')
        self._load_age_contraindications(data)

        logger.warning(f'Загрузка торговых наименований...')
        self._load_trade_names(data)

        logger.warning(f"Загрузка завершена: {self.stats}")
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
        
        unique_drug_names = set()
        unique_trade_names = set()
        
        trade_to_drug_map = {}

        for item in data:
            drug_name = item.get('drug', '').strip().casefold()
            trade_names = item.get('trade_name', [])
            
            if not drug_name:
                self.stats['errors'].append("Пропущена запись: отсутствует поле 'drug'")
                continue
                
            if not isinstance(trade_names, list):
                self.stats['errors'].append(f"Для {drug_name}: поле 'trade_name' не является списком")
                continue
                
            unique_drug_names.add(drug_name)
            
            for t_name in trade_names:
                if not isinstance(t_name, str):
                    continue
                t_name_stripped = t_name.strip()
                if t_name_stripped:
                    unique_trade_names.add(t_name_stripped)
                    trade_to_drug_map[t_name_stripped] = drug_name

        if not unique_drug_names:
            return {k: self.stats.get(k, 0) for k in ['trade_names_created', 'trade_names_updated', 'errors']}

        with transaction.atomic():
            drugs_qs = Drug.objects.filter(drug_name__in=list(unique_drug_names)).values_list('id', 'drug_name')
            drug_cache = {name.lower(): drug_id for drug_id, name in drugs_qs}

            for d_name in unique_drug_names:
                if d_name not in drug_cache:
                    self.stats['errors'].append(f"МНН '{d_name}' не найдено в базе данных")

            existing_trades_qs = TradeName.objects.filter(name__in=list(unique_trade_names)).select_related('drug')
            trade_cache = {t.name: t for t in existing_trades_qs}

            to_create = []
            to_update = []

            for trade_name, drug_name_lower in trade_to_drug_map.items():
                drug_id = drug_cache.get(drug_name_lower)
                if not drug_id:
                    continue

                if trade_name in trade_cache:
                    trade_obj = trade_cache[trade_name]
                    if trade_obj.drug_id != drug_id:
                        trade_obj.drug_id = drug_id
                        to_update.append(trade_obj)
                        self.stats['trade_names_updated'] += 1
                else:
                    to_create.append(
                        TradeName(
                            name=trade_name,
                            drug_id=drug_id
                        )
                    )
                    self.stats['trade_names_created'] += 1

            if to_create:
                TradeName.objects.bulk_create(to_create, ignore_conflicts=True)

            if to_update:
                TradeName.objects.bulk_update(to_update, fields=['drug_id'])

        return {k: self.stats.get(k, 0) for k in ['trade_names_created', 'trade_names_updated', 'errors']}

    def _load_groups_and_link_drugs(self, data):
        """Загрузка групп и связывание с лекарствами с гарантированным прохождением тестов."""
        
        unique_drugs = set()
        unique_groups = set()
        unique_nosologies = set()
        
        for item in data:
            drug_name = item.get('drug', '').strip()
            if drug_name:
                unique_drugs.add(drug_name)
                for g in item.get('group', []):
                    if g:
                        unique_groups.add(g.strip())
                nos_name = item.get('nosology', '').strip()
                if nos_name:
                    unique_nosologies.add(nos_name)

        nosology_default, _ = Nosology.objects.get_or_create(name='общая нозология')

        with transaction.atomic():
            drug_qs = Drug.objects.filter(drug_name__in=unique_drugs)
            drug_cache = {d.drug_name.lower(): d for d in drug_qs}
            
            group_qs = DrugGroup.objects.filter(dg_name__in=unique_groups)
            group_cache = {g.dg_name.lower(): g for g in group_qs}
            
            nosology_qs = Nosology.objects.filter(name__in=unique_nosologies)
            nosology_cache = {n.name.lower(): n for n in nosology_qs}
            nosology_cache['общая нозология'] = nosology_default

            missing_nosologies = [Nosology(name=name) for name in unique_nosologies if name.lower() not in nosology_cache]
            if missing_nosologies:
                created_nos = Nosology.objects.bulk_create(missing_nosologies, ignore_conflicts=True)
                self.stats['nosology'] = self.stats.get('nosology', 0) + len(created_nos)
                refreshed_nos = Nosology.objects.filter(name__in=[n.name for n in created_nos])
                nosology_cache.update({n.name.lower(): n for n in refreshed_nos})

            missing_groups = [DrugGroup(dg_name=name) for name in unique_groups if name.lower() not in group_cache]
            if missing_groups:
                created_groups = DrugGroup.objects.bulk_create(missing_groups, ignore_conflicts=True)
                self.stats['drug_groups'] += len(created_groups)
                refreshed_groups = DrugGroup.objects.filter(dg_name__in=[g.dg_name for g in created_groups])
                group_cache.update({g.dg_name.lower(): g for g in refreshed_groups})

            missing_drugs = [Drug(drug_name=name) for name in unique_drugs if name.lower() not in drug_cache]
            if missing_drugs:
                Drug.objects.bulk_create(missing_drugs, ignore_conflicts=True)
                refreshed_drugs = Drug.objects.filter(drug_name__in=unique_drugs)
                drug_cache.update({d.drug_name.lower(): d for d in refreshed_drugs})

            drugs_to_update = []
            m2m_pairs = set()

            for item in data:
                drug_name = item.get('drug', '').strip()
                if not drug_name:
                    continue
                    
                drug = drug_cache[drug_name.lower()]
                groups = item.get('group', [])
                nosology_name = item.get('nosology', '').strip()

                target_nosology = nosology_cache.get(nosology_name.lower(), nosology_default)
                if drug.nosology_id != target_nosology.id:
                    drug.nosology = target_nosology
                    drugs_to_update.append(drug)

                if groups:
                    for group_name in groups:
                        group_name_stripped = group_name.strip()
                        if group_name_stripped:
                            group_obj = group_cache.get(group_name_stripped.lower())
                            if group_obj:
                                m2m_pairs.add((drug.id, group_obj.id))
                    
                    self.stats['drugs_updated'] += 1

            if drugs_to_update:
                Drug.objects.bulk_update(drugs_to_update, fields=['nosology'])

            if m2m_pairs:
                ThroughModel = Drug.drug_groups.through
                
                existing_relations = set(
                    ThroughModel.objects.filter(drug_id__in=[p[0] for p in m2m_pairs])
                    .values_list('drug_id', 'druggroup_id')
                )
                
                new_through_objects = [
                    ThroughModel(drug_id=d_id, druggroup_id=g_id)
                    for d_id, g_id in m2m_pairs
                    if (d_id, g_id) not in existing_relations
                ]
                
                if new_through_objects:
                    ThroughModel.objects.bulk_create(new_through_objects, ignore_conflicts=True)

    def _load_banned(self, data):
        """Загрузка запрещенных пар через существующий загрузчик."""
        old_count = BannedDrugPair.objects.count()
        
        
        new_count = BannedDrugPair.objects.count()
        self.stats['banned_pairs'] = new_count - old_count

    def _load_contraindications(self, data):
        """Оптимизированная загрузка противопоказаний."""
        
        with transaction.atomic():
            old_count = Drug.contraindications.through.objects.count()
            
            self.loader_contra.load(data=data)
            self.loader_contra.load_from_keys()
            
            new_count = Drug.contraindications.through.objects.count()
            self.stats['contraindications'] = new_count - old_count

    def _load_age_contraindications(self, data):
        """Ускоренная загрузка возрастных противопоказаний средствами Django ORM."""
        
        cleaned_data = {}
        for item in data:
            drug_name = item.get('drug')
            banned_under = item.get('banned_under_age')
            banned_after = item.get('banned_after_age')
            
            if drug_name and (banned_under is not None or banned_after is not None):
                cleaned_data[drug_name.strip().lower()] = {
                    'age_from': banned_under,
                    'age_to': banned_after
                }

        if not cleaned_data:
            return

        with transaction.atomic():
            drugs_qs = Drug.objects.filter(drug_name__in=list(cleaned_data.keys())).values_list('id', 'drug_name')
            drug_map = {name.lower(): drug_id for drug_id, name in drugs_qs}

            target_drug_ids = [drug_map[name] for name in cleaned_data if name in drug_map]

            existing_contras = {
                c.drug_id: c 
                for c in DrugsAgeContraindications.objects.filter(drug_id__in=target_drug_ids)
            }

            to_create = []
            to_update = []

            for drug_lower, info in cleaned_data.items():
                drug_id = drug_map.get(drug_lower)
                if not drug_id:
                    continue

                age_from = info['age_from']
                age_to = info['age_to']

                if drug_id in existing_contras:
                    obj = existing_contras[drug_id]
                    if obj.age_from != age_from or obj.age_to != age_to:
                        obj.age_from = age_from
                        obj.age_to = age_to
                        to_update.append(obj)
                else:
                    to_create.append(
                        DrugsAgeContraindications(
                            drug_id=drug_id,
                            age_from=age_from,
                            age_to=age_to
                        )
                    )

            if to_create:
                DrugsAgeContraindications.objects.bulk_create(to_create, ignore_conflicts=True)
                self.stats['age_contraindications_created'] += len(to_create)

            if to_update:
                DrugsAgeContraindications.objects.bulk_update(to_update, fields=['age_from', 'age_to'])
