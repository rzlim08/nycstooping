from django.apps import AppConfig


class StooperRestFrameworkConfig(AppConfig):
    name = 'stooper.stooper_rest_framework'

    def ready(self):
        from stooper.stooper_rest_framework.models import PostLocation
        PostLocation.objects.create(
            id="new_id",
            long="-1.0",
            lat="-1.0"
        )
