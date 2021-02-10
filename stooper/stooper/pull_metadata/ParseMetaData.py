import json
import sys
from stooper.pull_metadata.LocationData import LocationData
from stooper.stooper_rest_framework.models import PostLocation
from stooper import secrets
import requests


class MetaDataParser:
    """Parse MetaData file from instagram scraper"""

    def __init__(self, jsonfile):
        self.jsonfile = jsonfile
        self.json = None
        self.image_meta = []
        self.read_json()

    def read_json(self):
        with open(self.jsonfile) as f:
            self.json = json.load(f)

    def extract_relevant_info(self):
        images = []
        for image_json in self.json["GraphImages"]:
            if PostLocation.object.filter(id=image_json["id"]).exists():
                continue
            subdict = {
                k: v
                for k, v in image_json.items()
                if k
                in [
                    "__typename",
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
            ld = LocationData("stooper/pull_metadata/models", insta_post.get_meta("caption"))
            loc = ld.run_spacy()
            if len(loc) > 0:
                insta_post.add_location_text(loc)
                location_data = insta_post.call_mapbox(loc)
                if location_data is None:
                    location_data = insta_post.call_google_maps(loc)

                insta_post.add_location(location_data)
            else:
                insta_post.add_location_text(None)

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

    def call_google_maps(self, loc):
        response = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json?address={text}"
            "&{bounding}&key={key}".format(
                text=loc[0],
                bounding=self.google_maps_coords,
                key=secrets.return_google_api_key(),
            )
        ).json()
        if len(response["results"]) == 0:
            return None
        else:
            best_res = response["results"][0]
            return LocationCoordinatesGoogle(
                best_res["geometry"]["location"], best_res["formatted_address"]
            )

    def call_mapbox(self, loc):
        get_string = "https://api.mapbox.com/geocoding/v5/mapbox.places/{text}.json?"\
            "types=address&{boundary}&{proximity}&{access}".format(
                text=str(loc[0]),
                boundary=self.boundaries,
                proximity=self.proximity,
                access=secrets.return_mapbox_key(),
            )
        response = requests.get(
            get_string
        ).json()
        if ("message" in response.keys()) and (response["message"] == "Not Found"):
            raise ValueError("mapbox not running")
        if (len(response["features"]) == 0) or (
            response["features"][0]["relevance"] <= 0.5
        ):
            return None
        else:
            correct = response["features"][0]
            return LocationCoordinatesMapbox(correct["center"], correct["place_name"])

    def add_location(self, loc):
        self.location = loc

    def timestamp_to_date(self):
        self.datetime = self.get_meta("taken_at_timestamp")

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
