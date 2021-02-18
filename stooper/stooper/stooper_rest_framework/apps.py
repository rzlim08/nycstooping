from django.apps import AppConfig


class StooperRestFrameworkConfig(AppConfig):
    name = "stooper.stooper_rest_framework"

    def ready(self):
        from stooper.pull_metadata.PullAndParse import PullAndParse
        pap = PullAndParse()
        pap.start()
        pap.schedule(240)

