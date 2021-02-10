from stooper import secrets
from stooper.pull_metadata.ParseMetaData import MetaDataParser
import subprocess


class PullAndParse:
    def __init__(self):
        # self.accounts = ['nycfreeatthecurb','stoopingnyc', 'stoopingupperwestside','curbalertnyc', 'curbalertqueens']
        self.accounts = ["curbalertnyc"]

    def scrape(self):
        for account in self.accounts:
            cmd = (
                "instagram-scraper {account} -u a_pro_stooper -p {password} --include-location "
                "--cookiejar cookies_aps --media-types none"
                " --latest -m1 --retry-forever -d stooper/pull_metadata".format(
                    account=account, password=secrets.return_pass()
                )
            )
            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            print(output, error)

    def parse(self):
        for account in self.accounts:
            json_file = "stooper/pull_metadata/{}.json".format(account)
            mdp = MetaDataParser(json_file)
            mdp()
            for m in mdp.image_meta:
                print(m.location, m.location_text)

