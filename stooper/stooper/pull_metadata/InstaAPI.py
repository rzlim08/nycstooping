import requests
import re
from stooper.pull_metadata.ParseMetaData import MetaDataParser
from stooper.secrets import return_rapid_api_key


class APIParser(MetaDataParser):
    def __init__(self, username):
        super().__init__("")
        self.username = username
        self.image_meta = []
        self.json = None

    def read_json(self):
        posts = self.call_api()
        for post in posts:
            caption = post["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"]
            post["node"]["tags"] = re.findall(r"#\w+", caption)
            post["node"]["username"] = self.username
        self.json = {"GraphImages": [post["node"] for post in posts]}

    def call_api(self):
        url = "https://instagram40.p.rapidapi.com/account-feed"
        querystring = {"username": self.username}
        headers = {
            'x-rapidapi-key': return_rapid_api_key(),
            'x-rapidapi-host': "instagram40.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        return response.json()

