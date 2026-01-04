from django.apps import AppConfig


class HousesConfig(AppConfig):
    name = "apps.houses"

    def ready(self):
        import apps.houses.signals
