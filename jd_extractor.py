import spacy

# Load the SpaCy English model
nlp = spacy.load("en_core_web_sm")

# ---------------------------- #
# Keyword Extraction Function #
# ---------------------------- #

def extract_keywords(text):
    """Extracts NOUN and PROPER NOUN keywords from text."""
    doc = nlp(text)
    keywords = [
        token.text.lower()
        for token in doc
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and token.is_alpha
    ]
    return list(set(keywords))

# ---------------------------- #
# Matching Logic Function     #
# ---------------------------- #

def keyword_match_score(jd_keywords, resume_keywords):
    """Calculates keyword match score and returns common keywords."""
    jd_set = set(jd_keywords)
    resume_set = set(resume_keywords)
    matched = jd_set.intersection(resume_set)
    score = (len(matched) / len(jd_set)) * 100 if jd_set else 0
    return round(score, 2), list(matched)

# ---------------------------- #
# Sample Inputs (For Testing) #
# ---------------------------- #

if __name__ == "__main__":
    job_description = """
    We are looking for a skilled Python developer with experience in machine learning, NLP, 
    data analysis, and web development using Flask or Django.
    """

    resume_text = """
    Experienced Python developer with a background in web development using Django,
    data analysis, and natural language processing.
    """

    jd_keywords = extract_keywords(job_description)
    resume_keywords = extract_keywords(resume_text)

    score, matched_keywords = keyword_match_score(jd_keywords, resume_keywords)

    print("📄 JD Keywords:", jd_keywords)
    print("👤 Resume Keywords:", resume_keywords)
    print(f"✅ Match Score: {score}%")
    print("🔁 Matched Keywords:", matched_keywords)
