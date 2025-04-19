import streamlit as st
import spacy
from match_agent import calculate_match_score

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Extractor function
def extract_keywords(text):
    doc = nlp(text)
    keywords = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and token.is_alpha:
            keywords.append(token.text.lower())
    return list(set(keywords))

# --- Streamlit UI ---
st.set_page_config(page_title="ResumeRadar", page_icon="📄")
st.title("📄 ResumeRadar: JD ↔️ CV Matcher")
st.write("Upload or paste a Job Description and Resume to calculate match score.")

jd_input = st.text_area("📝 Paste Job Description:", height=200)
cv_input = st.text_area("👤 Paste Resume:", height=200)

if st.button("🔍 Analyze & Match"):
    if jd_input and cv_input:
        jd_keywords = extract_keywords(jd_input)
        cv_keywords = extract_keywords(cv_input)

        score = calculate_match_score(jd_keywords, cv_keywords)

        st.markdown(f"### ✅ Match Score: `{score}%`")
        st.markdown("**JD Keywords:**")
        st.write(jd_keywords)
        st.markdown("**Resume Keywords:**")
        st.write(cv_keywords)

        if score >= 60:
            st.success("🎯 Candidate SHORTLISTED for interview!")
        else:
            st.warning("❌ Candidate NOT shortlisted. Needs closer alignment with JD.")
    else:
        st.error("Please paste both Job Description and Resume.")
