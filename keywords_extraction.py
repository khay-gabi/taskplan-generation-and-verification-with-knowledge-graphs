import spacy
from collections import Counter

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

class KeyWords:

    def advanced_keyword_extraction(self, text):
        # Process the text with spaCy
        doc = nlp(text)
        
        # Initialize a list to store keywords
        keywords = []
        
        # Extract named entities as keywords
        named_entities = [entity.text for entity in doc.ents]
        keywords.extend(named_entities)
        
        # Extract nouns and adjectives, excluding stop words, and apply lemmatization
        for token in doc:
            if token.pos_ in ['NOUN', 'ADJ'] and not token.is_stop:
                keywords.append(token.lemma_)
        
        # Use a Counter to aggregate and count keywords
        keyword_counts = Counter(keywords)
        
        return keyword_counts
