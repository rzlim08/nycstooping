import spacy
import sys


class LocationData:
    def __init__(self, location_model, text):
        self.text = text
        self.nlp = spacy.load(location_model)

    def run_spacy(self):
        doc = self.nlp(self.text)
        ents = []
        for ent in doc.ents:
            if ent.label_ == "TRIANGULATION":
                intersections = ent.text.lower().split("between")
                first_rd = intersections[0]
        return doc.ents


if __name__ == "__main__":
    model_path = sys.argv[1]
    text = sys.argv[2]
    LocationData(model_path, text).run_spacy()
