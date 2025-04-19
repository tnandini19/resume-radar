# Match Score Agent

def calculate_match_score(jd_keywords, resume_keywords):
    jd_set = set(jd_keywords)
    resume_set = set(resume_keywords)

    if not jd_set:
        return 0.0

    matched_keywords = jd_set.intersection(resume_set)
    match_score = len(matched_keywords) / len(jd_set) * 100

    print("Matched Keywords:", matched_keywords)
    return round(match_score, 2)

# Sample lists (replace with real output from extractor)
jd_keywords = ['python', 'developer', 'flask', 'nlp', 'machine', 'learning']
resume_keywords = ['python', 'django', 'nlp', 'developer', 'api']

# Run the matcher
score = calculate_match_score(jd_keywords, resume_keywords)
print(f"Match Score: {score}%")
