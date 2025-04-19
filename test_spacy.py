import spacy

# Load the English model
nlp = spacy.load("en_core_web_sm")

# Test with a simple text
doc = nlp("Hello, how are you doing today?")

# Print out the tokens
for token in doc:
    print(token.text, token.pos_)
