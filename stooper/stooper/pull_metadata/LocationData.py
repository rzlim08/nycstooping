import spacy


class LocationData:
    def __init__(self, location_model, text):
        self.text = text
        self.nlp = spacy.load(location_model)

    def run_spacy(self):
        doc = self.nlp(self.text)
        return doc.ents


