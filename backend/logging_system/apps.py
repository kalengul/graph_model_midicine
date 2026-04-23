from django.apps import AppConfig

class LoggingSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logging_system'
    verbose_name = 'Система логирования'

    def ready(self):
        # Импортируем модель ТОЛЬКО внутри метода ready
        from .models import SystemState
        from .utils.get_current_commit_hash import get_current_commit_hash
        
        commit = get_current_commit_hash()
        if commit:
            state = SystemState.get_current_state()
            if state.commit_hash != commit:
                state.commit_hash = commit
                state.save(update_fields=['commit_hash'])