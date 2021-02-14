import webscraping_ai
from stooper import secrets
from stooper.pull_metadata.ParseMetaData import MetaDataParser, InstagramPost


class ParseWebScrapingAPI(MetaDataParser):
    def __init__(self, jsonfile):
        super().__init__(jsonfile)

    def extract_relevant_info(self):
        api_response = self.call_webscraper()
        response_dict = eval(api_response)
        post_list = response_dict["graphql"]["user"]["edge_owner_to_timeline_media"][
            "edges"
        ]
        images = []
        for post in post_list:
            post = post["node"]
            subdict = {
                k: v
                for k, v in post.items()
                if k
                in [
                    "__typename",
                    "accessibility_caption",
                    "display_url",
                    "edge_sidecar_to_children",
                    "id",
                    "location",
                    "owner",
                    "shortcode",
                    "tags",
                    "taken_at_timestamp",
                    "urls",
                    "username",
                ]
            }
            subdict["username"] = subdict["owner"]["username"]
            if len(post["edge_media_to_caption"]["edges"]) < 1:
                subdict["caption"] = None
            elif len(post["edge_media_to_caption"]["edges"]) == 1:
                subdict["caption"] = post["edge_media_to_caption"]["edges"][0]["node"][
                    "text"
                ]
            else:
                raise ValueError("more than one caption")
            post = InstagramPost(subdict)
            post.timestamp_to_date()
            images.append(post)

    def call_webscraper(self):
        config = webscraping_ai.Configuration(
            api_key={"api_key": secrets.return_ws_api_key()}
        )
        with webscraping_ai.ApiClient(config) as api_client:
            api_instance = webscraping_ai.HTMLApi(api_client)
            url = "https://www.instagram.com/stoopingnyc/?__a=1"
            timeout = 5000
            proxy = "residential"
            js = False
            headers = {}
            try:
                api_response = api_instance.get_html(
                    url, headers=headers, timeout=timeout, js=js, proxy=proxy
                )
                print(api_response)
            except webscraping_ai.ApiException as e:
                print("Exception when calling HTMLApi->get_html: %s\n" % e)
        return api_response


if __name__ == "__main__":
    ParseWebScrapingAPI().extract_relevant_info()
