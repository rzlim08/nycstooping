from stooper import secrets
from stooper.pull_metadata.ParseMetaData import MetaDataParser
from stooper.stooper_rest_framework.models import PostLocation
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
import schedule
import time


class PullAndParse:
    def __init__(self):
        # self.accounts = ['nycfreeatthecurb','stoopingnyc', 'stoopingupperwestside','curbalertnyc', 'curbalertqueens']
        self.accounts = ["curbalertnyc", "stoopingnyc"]

    def scrape(self):
        cmd = (
            "instagram-scraper {account} -u a_pro_stooper -p {password} --include-location "
            "--cookiejar cookies_ps2 --media-types none"
            " -m100 --retry-forever -d stooper/pull_metadata".format(
                account=",".join(self.accounts), password=secrets.return_pass()
            )
        )
        """
        cmd = (
            "instagram-scraper {account} --include-location "
            "--cookiejar cookies_aps --media-types none"
            " -m5 -d stooper/pull_metadata".format(
                account=",".join(self.accounts)
            )
        )
        
        """
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        print(output, error)

    def parse(self):
        posts = []
        for account in self.accounts:
            json_file = "stooper/pull_metadata/{}.json".format(account)
            mdp = MetaDataParser(json_file)
            mdp()
            posts.extend(mdp.image_meta)

        return posts

    def start(self):
        self.scrape()
        posts = self.parse()
        for post in posts:
            if post.location is None:
                PostLocation.objects.get_or_create(
                    id=post.get_meta("id"),
                    posted_at=str(post.datetime),
                    display_url=post.get_meta("display_url"),
                    insta_account=post.get_meta("username"),
                    caption=post.get_meta("caption"),
                    long=-1,
                    lat=-1,
                )
            else:
                PostLocation.objects.get_or_create(
                    id=post.get_meta("id"),
                    posted_at=str(post.datetime),
                    display_url=post.get_meta("display_url"),
                    insta_account=post.get_meta("username"),
                    caption=post.get_meta("caption"),
                    long=post.location.long,
                    lat=post.location.lat,
                )

    def schedule(self, timer=5):
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.start, 'interval', minutes=timer)
        scheduler.start()
