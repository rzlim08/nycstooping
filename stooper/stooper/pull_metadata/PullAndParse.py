from stooper import secrets
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
                " --latest -m100 --retry-forever -d stooper/pull_metadata".format(
                    account=account, password=secrets.return_pass()
                )
            )
            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            print(output, error)
