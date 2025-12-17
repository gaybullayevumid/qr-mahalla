from django.apps import AppConfig


class QrcodesConfig(AppConfig):
    name = "apps.qrcodes"

    def ready(self):
        import apps.qrcodes.signals