import json
import sys
from stooper.pull_metadata.LocationData import LocationData
from stooper.stooper_rest_framework.models import PostLocation
from stooper import secrets
from datetime import datetime
import requests


class MetaDataParser:
    """Parse MetaData file from instagram scraper"""

    def __init__(self, jsonfile):
        self.jsonfile = jsonfile
        self.json = None
        self.image_meta = []

    def read_json(self):
        with open(self.jsonfile) as f:
            self.json = json.load(f)

    def extract_relevant_info(self):
        self.read_json()
        images = []
        for image_json in self.json["GraphImages"]:
            if PostLocation.objects.filter(id=image_json["id"]).exists():
                continue
            if "stoopingsuccess" in image_json["tags"]:
                continue
            subdict = {
                k: v
                for k, v in image_json.items()
                if k
                in [
                    "__typename",
                    "accessibility_caption",
                    "display_url",
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
            if len(image_json["edge_media_to_caption"]["edges"]) < 1:
                subdict["caption"] = None
            elif len(image_json["edge_media_to_caption"]["edges"]) == 1:
                subdict["caption"] = image_json["edge_media_to_caption"]["edges"][0][
                    "node"
                ]["text"]

            else:
                raise ValueError("more than one caption")
            post = InstagramPost(subdict)
            post.timestamp_to_date()
            images.append(post)
        self.image_meta = images

    def get_locations(self):
        for insta_post in self.image_meta:
            ld = LocationData(
                "stooper/pull_metadata/models", insta_post.get_meta("caption")
            )
            loc = ld.run_spacy()
            if len(loc) > 0:
                insta_post.add_location_text(loc)
                location_data = insta_post.call_google_maps(loc)
                insta_post.add_location(location_data)
            else:
                insta_post.add_location_text("")
                insta_post.add_location(None)

    def __call__(self):
        self.extract_relevant_info()
        self.get_locations()


class InstagramPost:
    def __init__(self, subdict):
        self.subdict = subdict
        self.boundaries = "bbox=-74.26,40.501,-73.74,40.88"
        self.proximity = "proximity=-73.9373,40.7643"
        self.google_maps_coords = "39.501,-74.26|40.88,-73.74"
        self.datetime = None
        self.location_text = None
        self.location = None

    def get_meta(self, fieldname):
        return self.subdict[fieldname]

    def call_google_maps(self, loc, recall=0):
        loc = " ".join(loc)
        get_string = self.format_get_request(
            "https://maps.googleapis.com/maps/api/geocode/json?address={text}"
            "&{bounding}&key={key}".format(
                text=loc,
                bounding=self.google_maps_coords,
                key=secrets.return_google_api_key(),
            )
        )
        response = requests.get(get_string).json()
        response = self.filter_responses(response["results"])
        if len(response) == 0 and recall:
            print("Failed google results: ", response, loc)
            return None
        elif len(response) == 0:
            return self.call_google_maps([loc + " nyc"], recall=1)
        else:
            best_res = response[0]
            return LocationCoordinatesGoogle(
                best_res["geometry"]["location"], best_res["formatted_address"]
            )

    @staticmethod
    def filter_responses(responses):
        valid_responses = []
        for response in responses:
            loc = response["geometry"]["location"]
            lat = loc["lat"]
            lng = loc["lng"]
            if (
                (40.501 <= lat <= 40.89)
                and (-74.26 <= lng < -73.74)
                and (
                    "ny" in response["formatted_address"].lower()
                    or "new york" in response["formatted_address"].lower()
                )
            ):
                valid_responses.append(response)

        return valid_responses

    def format_get_request(self, string):
        return string.replace("#", "%23").replace(";", "%3b")

    def add_location(self, loc):
        self.location = loc

    def timestamp_to_date(self):
        self.datetime = datetime.fromtimestamp(self.get_meta("taken_at_timestamp"))

    def add_location_text(self, location_text):
        self.location_text = location_text


class LocationCoordinates:
    def __init__(self, place_name):
        self.place_name = place_name
        self.long = None
        self.lat = None

    def __repr__(self):
        return "{}: lat = {}, long = {}".format(self.place_name, self.lat, self.long)


class LocationCoordinatesMapbox(LocationCoordinates):
    def __init__(self, coords, place_name):
        super().__init__(place_name)
        self.long = coords[0]
        self.lat = coords[1]


class LocationCoordinatesGoogle(LocationCoordinates):
    def __init__(self, coords, place_name):
        super().__init__(place_name)
        self.long = coords["lng"]
        self.lat = coords["lat"]


if __name__ == "__main__":
    jsonfile = sys.argv[1]
    mdp = MetaDataParser(jsonfile)
    mdp()
