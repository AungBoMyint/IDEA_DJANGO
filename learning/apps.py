from django.apps import AppConfig


class LearningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'learning'

    def ready(self) -> None:
        import learning.signals.signals
