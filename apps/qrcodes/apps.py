from django.apps import AppConfig


class QrcodesConfig(AppConfig):
    name = "apps.qrcodes"

    def ready(self):
        # signal shu yerda ulanadi
        import apps.qrcodes.signals