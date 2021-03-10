from stooper import secrets
from datetime import datetime
import requests


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
        get_string = self.format_get_request(
            "https://maps.googleapis.com/maps/api/geocode/json?address={text}"
            "&{bounding}&key={key}".format(
                text=loc[0],
                bounding=self.google_maps_coords,
                key=secrets.return_google_api_key(),
            )
        )
        response = requests.get(get_string).json()
        if len(response["results"]) == 0:
            print("Failed google results: ", response)
            return None
        else:
            best_res = response["results"][0]
            if (
                "NY" in best_res["formatted_address"].lower()
                or "new york" in best_res["formatted_address"]
                or recall
            ):
                return LocationCoordinatesGoogle(
                    best_res["geometry"]["location"], best_res["formatted_address"]
                )
            else:
                return self.call_google_maps([loc[0] + " nyc"], recall=1)

    def format_get_request(self, string):
        return string.replace("#", "%23")

    def call_mapbox(self, loc):
        get_string = self.format_get_request(
            "https://api.mapbox.com/geocoding/v5/mapbox.places/{text}.json?"
            "types=address&{boundary}&{proximity}&{access}".format(
                text=str(loc[0]),
                boundary=self.boundaries,
                proximity=self.proximity,
                access=secrets.return_mapbox_key(),
            )
        )

        response = requests.get(get_string).json()
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
    ip = InstagramPost({})
    ip.call_google_maps(["Dean and Smith"])
