import spacy
from match_agent import calculate_match_score

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Extractor functions
def extract_keywords(text):
    doc = nlp(text)
    keywords = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and token.is_alpha:
            keywords.append(token.text.lower())
    return list(set(keywords))

# Sample JD and Resume
job_description = """
We are hiring a backend Python developer with strong knowledge of Flask, APIs, and Machine Learning.
"""

resume = """
Skilled Python developer with hands-on experience in Django, Flask, machine learning, NLP, and API integration.
"""

# Run Extractors
jd_keywords = extract_keywords(job_description)
cv_keywords = extract_keywords(resume)

print("JD Keywords:", jd_keywords)
print("CV Keywords:", cv_keywords)

# Match Score
score = calculate_match_score(jd_keywords, cv_keywords)
print(f"\nMatch Score: {score}%")

# Shortlisting Logic
if score >= 60:
    print("\n✅ Candidate SHORTLISTED for interview!")
    print("📩 Sending interview invite to candidate@example.com...")
else:
    print("\n❌ Candidate NOT shortlisted. Needs closer alignment with JD.")
