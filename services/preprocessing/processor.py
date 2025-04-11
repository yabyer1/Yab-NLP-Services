import spacy

nlp = spacy.load("en_core_web_sm")

def preprocess_text(text: str) -> dict:
    doc = nlp(text)
    
    return {
        "tokens": [token.text for token in doc],
        "lemmas": [token.lemma_ for token in doc],
        "pos": [token.pos_ for token in doc],
        "ner": [(ent.text, ent.label_) for ent in doc.ents],
        "cleaned_tokens": [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    }
