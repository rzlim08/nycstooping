from django.apps import AppConfig


class StooperRestFrameworkConfig(AppConfig):
    name = 'stooper_rest_framework'
    def ready(self):
        from models import
