import spacy
import sys


class LocationData:
    def __init__(self, text):
        self.text = text
        self.nlp = spacy.load("models")

    def run_spacy(self):
        doc = self.nlp(self.text)
        return doc.ents


if __name__ == "__main__":
    ttl = LocationData(sys.argv[1])
