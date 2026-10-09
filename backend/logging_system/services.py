# logging_system/services.py
import os
from typing import Optional
from collections import defaultdict

from drugs.models import Drug
from logging_system.config import get_logger
from logging_system.models import SystemState


class BaseLoggingService:
    logger = None
    enabled_field = 'logging_enabled'  # тумблер общий

    @classmethod
    def is_enabled(cls) -> bool:
        try:
            state = SystemState.get_current_state()
            return getattr(state, cls.enabled_field)
        except Exception:
            return True

    @classmethod
    def set_enabled(cls, enabled: bool):
        state = SystemState.get_current_state()
        if getattr(state, cls.enabled_field) != enabled:
            setattr(state, cls.enabled_field, enabled)
            state.save(update_fields=[cls.enabled_field])
            if cls.logger is not None:
                cls.logger.info(f"Логирование {'включено' if enabled else 'выключено'}")

    @staticmethod
    def _format_banned_pairs(pairs: Optional[list[dict]]) -> list:
        if not pairs:
            return []
        parts = []
        for p in pairs:
            names = p.get("names") or p.get("pair") or []
            if len(names) >= 2:
                parts.append([names[0], names[1]])
            elif names:
                parts.append(names[0])
        return parts

    @staticmethod
    def _format_banned_pairs_cont(items) -> list:
        """
        Канонический формат: [(drug_name, [contra, ...]), ...].
        По умолчанию возвращаем как есть — подклассы могут переопределить
        """
        if not items:
            return []
        return list(items)

    @classmethod
    def _middle_parts(cls, **kwargs) -> list[str]:
        """
        Точка расширения: подклассы могут вернуть дополнительные поля,
        которые будут вставлены между Rank и Drugs.
        По умолчанию — ничего.
        """
        return []

    @classmethod
    def _common_parts(
        cls,
        user,
        status,
        rank,
        all_drugs,
        banned_pairs,
        banned_pairs_cont,
        **extra,
    ):
        user_str = user.username if user and user.is_authenticated else "Anonymous"
        state = SystemState.get_current_state()
        drugs_file = state.drugs_file_name or "N/A"
        weights_file = state.weights_file_name or "N/A"

        parts = [
            f"User: {user_str}",
            f"Status: {status or 'None'}",
            f"Rank: {rank if rank is not None else 'None'}",
        ]
        parts.extend(cls._middle_parts(**extra))
        parts.extend([
            f"Drugs: {list(all_drugs or [])}",
            f"BannedPairs: {cls._format_banned_pairs(banned_pairs) or 'None'}",
            f"BannedPairsCont: {cls._format_banned_pairs_cont(banned_pairs_cont) or 'None'}",
            f"DrugsFile: {drugs_file}",
            f"WeightsFile: {weights_file}",
        ])
        return parts

class FortranCalcLoggingService(BaseLoggingService):
    logger = get_logger('fortran_calc', 'fortran_calc.log')

    @classmethod
    def log_request(
        cls,
        user,
        status: str,
        rank: Optional[float] = None,
        all_drugs: Optional[list[str]] = None,
        banned_pairs: Optional[list[dict]] = None,
        banned_pairs_cont: Optional[list[dict]] = None,
    ) -> None:
        if not cls.is_enabled():
            return

        parts = cls._common_parts(
            user=user,
            status=status,
            rank=rank,
            all_drugs=all_drugs,
            banned_pairs=banned_pairs,
            banned_pairs_cont=banned_pairs_cont,
        )
        cls.logger.info(" | ".join(parts))


class RiskAssessmentLoggingService(BaseLoggingService):
    logger = get_logger('risk_assessments', 'risk_assesments.log')

    @classmethod
    def _format_banned_pairs_cont(cls, items) -> list:
        """
        Приводит плоский risk-формат
        [{'drugName': ..., 'contraindicationName': ...}, ...]
        к каноническому [(drug_name, [contra, ...]), ...].
        """
        if not items:
            return []
        by_drug = defaultdict(list)
        for i in items:
            by_drug[i.get('drugName')].append(i.get('contraindicationName'))
        return list(by_drug.items())

    @classmethod
    def _middle_parts(cls, drug_ids=None, missing_drugs=None, **kwargs) -> list[str]:
        return [
            f"MissingDrugs: {list(missing_drugs or [])}",
        ]

    @classmethod
    def log_request(
        cls,
        user,
        status: str,
        rank: Optional[float] = None,
        drug_ids: Optional[list[int]] = None,
        missing_drugs: Optional[list[str]] = None,
        all_drugs: Optional[list[str]] = None,
        banned_pairs: Optional[list[dict]] = None,
        banned_pairs_cont: Optional[list[dict]] = None,
    ) -> None:
        if not cls.is_enabled():
            return

        parts = cls._common_parts(
            user=user,
            status=status,
            rank=rank,
            all_drugs=all_drugs,
            banned_pairs=banned_pairs,
            banned_pairs_cont=banned_pairs_cont,
            # extra-поля уезжают в _middle_parts
            missing_drugs=missing_drugs,
        )
        cls.logger.info(" | ".join(parts))

class LoggingToggleService(BaseLoggingService):
    """
    Управление общим тумблером логирования.
    Не привязан ни к fortran, ни к risk — пишет событие в отдельный файл.
    """
    logger = get_logger('logging_system', 'logging_system.log')