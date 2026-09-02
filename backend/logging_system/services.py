# backend/logging_system/services.py
import os
from logging_system.config import get_logger, LOG_DIR
from drugs.models import Drug
from logging_system.models import SystemState

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
    def log_request(user, drug_ids=None, drug_names=None):
        """
        Логирует пользователя, список препаратов, версии файлов и хэш коммита.
        :param user: объект пользователя (или None)
        :param drug_ids: список ID препаратов (для старого сервиса)
        :param drug_names: список названий препаратов (для нового сервиса)
        """
        if not CalculationLoggingService.is_enabled():
            return

        # Определяем названия препаратов
        if drug_names is not None:
            drugs = drug_names
        elif drug_ids is not None:
            drugs = list(Drug.objects.filter(id__in=drug_ids).values_list('drug_name', flat=True))
        else:
            drugs = []

        user_str = user.username if user and user.is_authenticated else "Anonymous"
        state = SystemState.get_current_state()
        drugs_file = state.drugs_file_name or 'N/A'
        weights_file = state.weights_file_name or 'N/A'

        _logger.info(
            f"User: {user_str} | Drugs: {drugs} | "
            f"DrugsFile: {drugs_file} | WeightsFile: {weights_file}"
        )