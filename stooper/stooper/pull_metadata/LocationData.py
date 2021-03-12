import spacy
import sys
import re

class LocationData:
    def __init__(self, location_model, text):
        self.text = text
        self.nlp = spacy.load(location_model)

    def run_spacy(self):
        doc = self.nlp(self.text)
        ents = []
        for ent in doc.ents:
            if ent.label_ == "TRIANGULATION":
                caption = ent.text.lower()
                caption = re.sub('between|btwn|btw|bw', 'and', caption)
                ents.append(caption)
            else:
                ents.append(ent.text)
        return ents


if __name__ == "__main__":
    model_path = sys.argv[1]
    text = sys.argv[2]
    LocationData(model_path, text).run_spacy()
