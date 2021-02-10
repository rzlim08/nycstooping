from django.apps import AppConfig


class StooperRestFrameworkConfig(AppConfig):
    name = "stooper.stooper_rest_framework"

    def ready(self):
        from stooper.stooper_rest_framework.models import PostLocation
        from stooper.pull_metadata.PullAndParse import PullAndParse

        pap = PullAndParse()
        pap.scrape()
        posts = pap.parse()
        for post in posts:
            PostLocation.objects.get_or_create(
                id=post.get_meta("id"),
                posted_at=post.datetime,
                display_url=post.get_meta("display_url"),
                insta_account=post.get_meta("username"),
                caption= post.get_meta("caption"),
                long= post.loc.long,
                lat= post.loc.lat,
            )
