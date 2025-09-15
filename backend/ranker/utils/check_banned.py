"""Модуль запретов."""

from itertools import combinations
from abc import ABC, abstractmethod

from django.db.models import Q

from drugs.models import Drug, BannedDrugPair


class BannedChecker(ABC):
    """Класс проверки на запрет."""

    @abstractmethod
    def check_banned(self, *args, **kwargs):
        """Провекра на наличие запретов."""


class DrugPairChecker(BannedChecker):
    """Класс для проверки запрещённых пар ЛС."""

    def check_banned(self, drugs):
        """Проверка на наличие запрещённых пар ЛС."""
        drug_map = (
            {drug.id: drug for drug in Drug.objects.filter(id__in=drugs)})
        banned_pairs = []
        for id1, id2 in combinations(drugs, 2):
            name1 = drug_map[id1].drug_name
            name2 = drug_map[id2].drug_name

            pair = BannedDrugPair.objects.filter(
                Q(first_drug__iexact=name1, second_drug__iexact=name2) |
                Q(first_drug__iexact=name2, second_drug__iexact=name1)
            ).first()

            if pair:
                banned_pairs.append((name1, name2, pair.comment))
        return banned_pairs
