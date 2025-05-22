from django.apps import AppConfig


class DrugsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'drugs'

    def ready(self):
        import drugs.signals
