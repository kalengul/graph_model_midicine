# backend/logging_system/services.py
import os
from logging_system.config import get_logger, LOG_DIR
from drugs.models import Drug
from logging_system.models import SystemState
from typing import Optional
from datetime import datetime

_logger = get_logger()
CONFIG_FILE = os.path.join(LOG_DIR, 'logging_enabled.txt')

class CalculationLoggingService:

    @staticmethod
    def is_enabled() -> bool:
        """Возвращает текущее состояние логирования (из БД)."""
        try:
            state = SystemState.get_current_state()
            return state.logging_enabled
        except Exception:
            return True  # fallback

    @staticmethod
    def set_enabled(enabled: bool):
        """Включает или выключает логирование."""
        state = SystemState.get_current_state()
        if state.logging_enabled != enabled:
            state.logging_enabled = enabled
            state.save(update_fields=['logging_enabled'])
            _logger.info(f"Логирование {'включено' if enabled else 'выключено'}")

    @staticmethod
    def log_request(
        user,
        status: str,
        rank: Optional[float] = None,
        drug_ids: Optional[list[int]] = None,
        missing_drugs: Optional[list[str]] = None,
        all_drugs: Optional[list[str]] = None,
        banned_pairs: Optional[list[dict]] = None,
        banned_pairs_cont: Optional[list[dict]] = None,
    ) -> None:
        """
        Логирует результат оценки рисков в одну строку, поля через ';':
        User;timestamp;status;rank;drug_ids;missing_drugs;all_drugs;
        banned_pairs;banned_pairs_cont;drugs_file;weights_file
        """
        if not CalculationLoggingService.is_enabled():
            return

        # Определяем названия препаратов
        if (drug_ids is not None) and (all_drugs is None):
            all_drugs = list(Drug.objects.filter(id__in=drug_ids).values_list('drug_name', flat=True))

        user_str = user.username if user and user.is_authenticated else "Anonymous"

        state = SystemState.get_current_state()
        drugs_file = state.drugs_file_name or "N/A"
        weights_file = state.weights_file_name or "N/A"

        parts = [
            f"User: {user_str}",
            f"Status: {status or 'None'}",
            f"Rank: {rank if rank is not None else 'None'}",
            f"DrugIds: {list(drug_ids or [])}",
            f"MissingDrugs: {list(missing_drugs or [])}",
            f"Drugs: {list(all_drugs or [])}",
            f"BannedPairs: {CalculationLoggingService._format_banned_pairs(banned_pairs) or 'None'}",
            f"BannedPairsCont: {CalculationLoggingService._format_banned_pairs_cont(banned_pairs_cont) or 'None'}",
            f"DrugsFile: {drugs_file}",
            f"WeightsFile: {weights_file}",
        ]

        line = " | ".join(parts)
        _logger.info(line)

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
    def _format_banned_pairs_cont(items: Optional[list[dict]]) -> str:
        if not items:
            return ""
        return [
            (i.get('drugName'), i.get('contraindicationName'))
            for i in items
        ]