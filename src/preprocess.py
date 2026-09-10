import re
import spacy

# Load spaCy English model
nlp = spacy.load('en_core_web_sm')

def clean_text(text):
    # Lowercase
    text = text.lower()
    
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Remove extra whitespace
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    
    return text

def lemmatize(text):
    doc = nlp(text)
    # Keep all words except punctuation and spaces
    # We keep negations like "not", "never" on purpose
    tokens = [token.lemma_ for token in doc if not token.is_punct and not token.is_space]
    return ' '.join(tokens)

def preprocess(text):
    text = clean_text(text)
    text = lemmatize(text)
    return text