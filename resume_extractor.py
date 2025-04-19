import spacy

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract candidate data from resume
def extract_resume_info(resume_text):
    doc = nlp(resume_text)
    keywords = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and token.is_alpha:
            keywords.append(token.text.lower())
    return list(set(keywords))

# Sample Resume (can be replaced with actual user input)
resume = '''
Experienced Python developer skilled in data analysis, machine learning, and backend development using Flask and Django.
Worked on NLP projects using NLTK and SpaCy. Familiar with APIs, SQL, and Git.
'''

# Run the extractor
extracted = extract_resume_info(resume)
print("Extracted Resume Keywords:", extracted)
