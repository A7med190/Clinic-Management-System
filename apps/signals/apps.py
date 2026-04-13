from django.apps import AppConfig


class SignalsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.signals"

    def ready(self):
        import apps.signals.handlers  # noqa: F401
