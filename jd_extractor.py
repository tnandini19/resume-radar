import spacy

# Load the SpaCy English model
nlp = spacy.load("en_core_web_sm")

# Function to extract keywords from job description
def extract_keywords(text):
    doc = nlp(text)
    keywords = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and token.is_alpha:
            keywords.append(token.text.lower())
    return list(set(keywords))

# Sample JD
job_description = """
We are looking for a skilled Python developer with experience in machine learning, NLP, 
data analysis, and web development using Flask or Django.
"""

# Run the extractor
extracted = extract_keywords(job_description)
print("Extracted JD Keywords:", extracted)
