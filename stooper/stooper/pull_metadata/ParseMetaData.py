import json
import sys
from datetime import datetime
from LocationData import LocationData
import requests


class MetaDataParser:
    """Parse MetaData file from instagram scraper"""

    def __init__(self, jsonfile):
        self.jsonfile = jsonfile
        self.json = None
        self.image_meta = None
        self.boundaries = "bbox=-74.26,40.501,-73.74,40.88"
        self.proximity = "proximity=-73.9373,40.7643"
        self.access = "access_token=pk.eyJ1IjoibGltcjEwIiwiYSI6ImNra3Qzc3d4NzB0dnQybnJ0OGpwNGx1Y3MifQ.DVO1tkloVpo9UrAGvokQ0w"
        self.read_json()
        self.location_coordinates = []
        self.google_maps_key = "AIzaSyAk0MzAhyw0_RiDOC7rYYkSUYs7zG_qMfY"
        self.google_maps_coords = "40.501,-74.26|40.88,-73.74"

    def read_json(self):
        with open(self.jsonfile) as f:
            self.json = json.load(f)

    def extract_relevant_info(self):
        images = []
        for image_json in self.json["GraphImages"]:
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
            images.append(subdict)
        self.image_meta = images

    def timestamp_to_date(self):
        for image_json in self.image_meta:
            image_json["datetime"] = datetime.fromtimestamp(
                image_json["taken_at_timestamp"]
            )

    def get_location(self):
        for image_json in self.image_meta:
            ld = LocationData(image_json["caption"])
            loc = ld.run_spacy()
            if len(loc) > 0:
                response_dict = self.call_mapbox(loc)
                if (len(response_dict["features"]) == 0) or (
                    response_dict["features"][0]["relevance"] <= 0.5
                ):
                    gmaps_response_dict = self.call_google_maps(loc)
                    if len(gmaps_response_dict["results"]) == 0:
                        print("Failed: ", image_json["caption"], loc[-1])
                        continue
                    best_res = gmaps_response_dict["results"][0]
                    self.location_coordinates.append(
                        LocationCoordinates(
                            image_json["caption"],
                            best_res["geometry"]["location"],
                            best_res["formatted_address"],
                        )
                    )
                    print(
                        "Success! ",
                        image_json["caption"],
                        best_res["geometry"]["location"],
                        best_res["formatted_address"],
                    )
                elif response_dict["features"][0]["relevance"] > 0.5:
                    correct = response_dict["features"][0]
                    self.location_coordinates.append(
                        LocationCoordinates(
                            image_json["caption"],
                            correct["center"],
                            correct["place_name"],
                        )
                    )
                    print(
                        image_json["caption"], correct["center"], correct["place_name"]
                    )
        pass

    def call_google_maps(self, loc):
        response = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json?address={text}"
            "&{bounding}&key={key}".format(
                text=loc[0], bounding=self.google_maps_coords, key=self.google_maps_key
            )
        )
        return response.json()

    def call_mapbox(self, loc):
        response = requests.get(
            "https://api.mapbox.com/geocoding/v5/mapbox.places/{text}.json?"
            "types=address&{boundary}&{proximity}&{access}".format(
                text=str(loc[0]),
                boundary=self.boundaries,
                proximity=self.proximity,
                access=self.access,
            )
        )
        response_dict = response.json()
        return response_dict

    def __call__(self):
        self.extract_relevant_info()
        self.timestamp_to_date()
        self.get_location()


class LocationCoordinates:
    def __init__(self, text, coords, place_name):
        self.text = text
        self.coordinates = coords
        self.place_name = place_name


if __name__ == "__main__":
    jsonfile = sys.argv[1]
    mdp = MetaDataParser(jsonfile)
    mdp()
