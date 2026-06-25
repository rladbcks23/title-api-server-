import sys

from django.apps import AppConfig
from django.conf import settings


class TitlesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "titles"

    def ready(self):
        management_commands = {
            "check",
            "makemigrations",
            "migrate",
            "shell",
            "test",
        }
        is_management_command = any(
            command in sys.argv
            for command in management_commands
        )
        if (
            settings.TITLE_MODEL_ENABLED
            and settings.TITLE_MODEL_EAGER_LOAD
            and not is_management_command
        ):
            from .model_service import title_model_service

            title_model_service.load()
