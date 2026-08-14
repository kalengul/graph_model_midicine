"""
Сервисный слой модуля risk_assessments.

Порядок работы:
  1. Резолвим названия препаратов -> Drug ID
  2. Резолвим названия противопоказаний -> Contraindication ID
  3. Запускаем существующий расчёт совместимости через FortranCalculator
"""
import logging
from typing import Optional
import re

from drugs.models import Drug
from contraindications.models import Contraindication

from ranker.utils.check_banned import DrugPairChecker
from ranker.utils.fortran_calculator import FortranCalculator
from ranker.constants import IDX_2_RANK_NAME

from risk_assessments.utils import normalize_drug_name

logger = logging.getLogger("risk_assessments.service")


class DrugNotFoundError(Exception):
    """Один или несколько препаратов не найдены в БД."""
    def __init__(self, missing: list[str]):
        self.missing = missing


class ContraindicationNotFoundError(Exception):
    """Одно или несколько противопоказаний не найдены в БД."""
    def __init__(self, missing: list[str]):
        self.missing = missing


# Маппинг значений compatibility_fortran из калькулятора в наш API-enum.
# Калькулятор возвращает нижний регистр; наш API — верхний.
_FORTRAN_STATUS_MAP = {
    "compatible":   "COMPATIBLE",
    "caution":      "CAUTION",
    "incompatible": "INCOMPATIBLE",
}


def resolve_drug_ids(drug_names: list[str]) -> dict[int, str]:
    """
    Принимает нормализованные названия препаратов.
    Возвращает {drug_id: drug_name} для всех найденных.
    Бросает DrugNotFoundError, если хоть одно название не найдено.
    """
    found: dict[int, str] = {}
    missing: list[str] = []

    for name in drug_names:
        drug = Drug.objects.filter(drug_name__iexact=name).first()
        if drug is None:
            missing.append(name)
        else:
            found[drug.id] = drug.drug_name

    if missing:
        raise DrugNotFoundError(missing)

    return found


def resolve_contraindication_ids(contra_names: list[str]) -> list[int]:
    """
    Принимает названия противопоказаний (нормализация внутри).
    Возвращает список ID найденных противопоказаний.
    Бросает ContraindicationNotFoundError, если хоть одно не найдено.
    """
    if not contra_names:
        return []

    found_ids: list[int] = []
    missing: list[str] = []

    for name in contra_names:
        normalized = re.sub(r"\s+", " ", name.lower()).strip()
        contra = Contraindication.objects.filter(name__iexact=normalized).first()
        if contra is None:
            missing.append(name)  # возвращаем исходное имя в ошибке — понятнее пользователю
        else:
            found_ids.append(contra.id)

    if missing:
        raise ContraindicationNotFoundError(missing)

    return found_ids


def assess_drug_risks(
    drug_names: list[str],
    patient_profile: Optional[dict] = None,
) -> dict:
    """
    Главная функция оценки рисков.

    Args:
        drug_names: нормализованные названия препаратов (уже прошли через сериализатор)
        patient_profile: провалидированный dict из PatientProfileSerializer или None

    Returns:
        dict согласно схеме DrugRiskAssessmentResponse

    Raises:
        DrugNotFoundError
        ContraindicationNotFoundError
    """
    # 1. Резолвим препараты
    drugs_map = resolve_drug_ids(drug_names)   # {id: drug_name}
    drug_ids = list(drugs_map.keys())

    # 2. Резолвим противопоказания пациента
    cont_ids: list[int] = []
    if patient_profile:
        raw_cont_list = patient_profile.get("contList") or []
        cont_ids = resolve_contraindication_ids(raw_cont_list)

    # 3. Проверка запрещённых пар
    banned_pairs = DrugPairChecker().check_banned(drug_ids)
    if banned_pairs:
        return _build_response(
            drugs_map=drugs_map,
            status="BANNED",
            banned_pairs=banned_pairs,
        )

    # 4. Проверка противопоказаний пациента
    if cont_ids or (patient_profile and patient_profile.get("age") is not None):
        contra_result = _check_contraindications(
            drug_ids,
            cont_ids=cont_ids,
            age=patient_profile.get("age") if patient_profile else None,
        )
        if contra_result:
            return _build_response(
                drugs_map=drugs_map,
                status="BANNED_CONTRAINDICATIONS",
                banned_pairs_cont=contra_result,
            )

    # 5. Основной расчёт совместимости
    gender = patient_profile.get("gender") if patient_profile else None
    context = FortranCalculator(
        normalize=True,
        cuttoff_not_life_threats_side_e=True,
    ).calculate(
        rank_name=IDX_2_RANK_NAME[0],
        n_drug=drug_ids,
        gender=gender,
    )

    return _build_response(
        drugs_map=drugs_map,
        status=_map_fortran_status(context["compatibility_fortran"]),
        # Ключ в калькуляторе написан с опечаткой — оставляем как есть
        rank=context.get("rank_iteractions"),
        side_effects=_map_side_effects(context.get("side_effects", [])),
        combinations=_map_combinations(context.get("combinations", [])),
        se_from_drug=_map_se_from_drug(context.get("SEFromDrug", [])),
    )


# ---------------------------------------------------------------------------
# Маппинг данных из FortranCalculator в формат API
# ---------------------------------------------------------------------------

def _map_fortran_status(raw_status: str) -> str:
    """
    Переводит статус калькулятора (нижний регистр) в API-enum (верхний регистр).
    Калькулятор возвращает: "compatible" | "caution" | "incompatible"
    """
    mapped = _FORTRAN_STATUS_MAP.get(raw_status)
    if mapped is None:
        logger.warning("Неизвестный статус калькулятора: %s, используем CAUTION", raw_status)
        return "CAUTION"
    return mapped


def _map_side_effects(raw: list[dict]) -> list[dict]:
    """
    Калькулятор возвращает:
      [
        {"compatibility": "compatible", "effects": [{"se_name": "...", "rank": 0.1}, ...]},
        {"compatibility": "caution",    "effects": [...]},
        {"compatibility": "incompatible","effects": [...]},
      ]

    API ожидает:
      [
        {"compatibility": "compatible", "effects": [{"seName": "...", "rank": 0.1}, ...]},
        ...
      ]
    """
    result = []
    for group in raw:
        mapped_effects = [
            {"seName": e["se_name"], "rank": e["rank"]}
            for e in group.get("effects", [])
        ]
        result.append({
            "compatibility": group["compatibility"],
            "effects": mapped_effects,
        })
    return result


def _map_combinations(raw: list[dict]) -> list[dict]:
    """
    Калькулятор возвращает:
      [
        {
          "compatibility": "caution",
          "drugs": [{"name": "...", "side_effects": [{"se_name": "...", "rank": 0.1}]}, ...]
        },
        {
          "compatibility": "incompatible",
          "drugs": [{"name": "...", "side_effects": [...]}, ...]
        },
      ]

    API ожидает:
      [
        {
          "compatibility": "caution",
          "drugs": [{"name": "...", "sideEffects": [{"seName": "...", "rank": 0.1}]}, ...]
        },
        ...
      ]
    """
    result = []
    for group in raw:
        mapped_drugs = []
        for drug in group.get("drugs", []):
            mapped_se = [
                {"seName": se["se_name"], "rank": se["rank"]}
                for se in drug.get("side_effects", [])
            ]
            mapped_drugs.append({"name": drug["name"], "sideEffects": mapped_se})
        result.append({
            "compatibility": group["compatibility"],
            "drugs": mapped_drugs,
        })
    return result


def _map_se_from_drug(raw: list[dict]) -> list[dict]:
    """
    Калькулятор возвращает:
      [
        {"d_name": "...", "effects": [{"se_name": "...", "rank": 0.1}, ...]},
        ...
      ]

    API ожидает (поле combinations по препаратам — для sideEffects блока):
      [
        {"name": "...", "sideEffects": [{"seName": "...", "rank": 0.1}, ...]},
        ...
      ]
    """
    result = []
    for item in raw:
        mapped_effects = [
            {"seName": e["se_name"], "rank": e["rank"]}
            for e in item.get("effects", [])
        ]
        result.append({"name": item["d_name"], "sideEffects": mapped_effects})
    return result


# ---------------------------------------------------------------------------
# Проверка противопоказаний
# ---------------------------------------------------------------------------

def _check_contraindications(
    drug_ids: list[int],
    cont_ids: list[int],
    age: Optional[int],
) -> list[dict]:
    """
    Проверяет явные противопоказания и возрастные ограничения.
    Возвращает список несовместимостей или пустой список.
    """
    result = []

    drugs_qs = Drug.objects.filter(id__in=drug_ids).prefetch_related("contraindications")
    if age is not None:
        drugs_qs = drugs_qs.prefetch_related("age_restrictions")

    for drug in drugs_qs:
        # Явные противопоказания
        if cont_ids:
            for contra in drug.contraindications.filter(id__in=cont_ids):
                result.append({
                    "drugId": drug.id,
                    "drugName": drug.drug_name,
                    "contraindicationId": contra.id,
                    "contraindicationName": contra.name,
                    "reason": None,
                })

        # Возрастные ограничения
        if age is not None:
            for restriction in drug.age_restrictions.all():  # type: ignore[attr-defined]
                violation: Optional[str] = None
                if restriction.age_from and age < restriction.age_from:
                    violation = f"возраст до {restriction.age_from} лет"
                elif restriction.age_to and age > restriction.age_to:
                    violation = f"возраст после {restriction.age_to} лет"

                if violation:
                    result.append({
                        "drugId": drug.id,
                        "drugName": drug.drug_name,
                        "contraindicationId": None,
                        "contraindicationName": violation,
                        "reason": None,
                    })

    return result


# ---------------------------------------------------------------------------
# Сборка финального ответа
# ---------------------------------------------------------------------------

def _build_response(
    drugs_map: dict[int, str],
    status: str,
    rank: Optional[float] = None,
    banned_pairs: Optional[list] = None,
    banned_pairs_cont: Optional[list] = None,
    side_effects: Optional[list] = None,
    combinations: Optional[list] = None,
    se_from_drug: Optional[list] = None,
) -> dict:
    return {
        "drugs": {str(k): v for k, v in drugs_map.items()},
        "compatibility": {
            "status": status,
            "rank": rank,
        },
        "bannedPairs": banned_pairs or [],
        "bannedPairsCont": banned_pairs_cont or [],
        "sideEffects": side_effects or [],
        "combinations": combinations or [],
        "seFromDrug": se_from_drug or [],
    }