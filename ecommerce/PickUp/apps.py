from django.apps import AppConfig


class PickUpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'PickUp'

    def ready(self):
        from . import signals  # noqa: F401