import streamlit as st
import spacy
import fitz  # PyMuPDF
from fpdf import FPDF
import base64
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from jd_extractor import extract_keywords as extract_jd_keywords, keyword_match_score
from resume_parser import extract_text_from_pdf, extract_resume_keywords

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# --- Keyword Extractor ---
def extract_keywords(text):
    doc = nlp(text)
    keywords = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and token.is_alpha:
            keywords.append(token.text.lower())
    return list(set(keywords))

# --- WordCloud Generator ---
def show_wordcloud(title, text):
    st.subheader(title)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(text))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

# --- PDF Resume Extractor ---
def extract_resume_from_file(uploaded_file):
    with open("temp_resume.pdf", "wb") as f:
        f.write(uploaded_file.read())
    return extract_text_from_pdf("temp_resume.pdf")

# --- PDF Report Generator ---
def generate_pdf_report(jd_keywords, cv_keywords, score):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="ResumeRadar Match Report", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Match Score: {score}%", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="JD Keywords:", ln=True)
    pdf.set_font("Arial", size=12)
    for word in jd_keywords:
        pdf.cell(200, 10, txt=f"- {word}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Resume Keywords:", ln=True)
    pdf.set_font("Arial", size=12)
    for word in cv_keywords:
        pdf.cell(200, 10, txt=f"- {word}", ln=True)

    pdf_output = "match_report.pdf"
    pdf.output(pdf_output)
    return pdf_output

def get_pdf_download_link(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    href = f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="match_report.pdf">📥 Download Match Report (PDF)</a>'
    return href

# --- Streamlit UI ---
st.set_page_config(page_title="ResumeRadar", page_icon="📄", layout="wide")
st.title("📄 ResumeRadar: JD ↔️ Resume Analyzer")
st.markdown("""
Welcome to **ResumeRadar** – Your AI-powered job-fit analyzer.  
Upload your **Resume** and the **Job Description (JD)** to get:
- ✅ Match score
- 📌 Missing keywords
- ☁️ Wordclouds
- 🧾 Downloadable PDF report
""")

# Streamlit built-in theme handling (this will automatically handle the theme based on user preference)
theme = st.get_option("theme.base")

# Layout split
col1, col2 = st.columns(2)

with col1:
    jd_input = st.text_area("📝 Paste Job Description:", height=250)
    jd_pdf = st.file_uploader("📄 Or Upload JD (PDF)", type=["pdf"], key="jd")
    if jd_pdf:
        jd_input = extract_text_from_pdf(jd_pdf)

with col2:
    cv_input = st.text_area("👤 Paste Resume:", height=250)
    cv_pdf = st.file_uploader("📄 Or Upload Resume (PDF)", type=["pdf"], key="cv")
    if cv_pdf:
        cv_input = extract_resume_from_file(cv_pdf)

if st.button("🔍 Analyze & Match"):
    if jd_input and cv_input:
        with st.spinner("Analyzing and matching... 🚀"):
            jd_keywords = extract_jd_keywords(jd_input)
            cv_keywords = extract_keywords(cv_input)
            score, matched_keywords = keyword_match_score(jd_keywords, cv_keywords)

        st.subheader(f"🎯 Match Score: {score}%")
        if score >= 60:
            st.success("Looks like a strong match! Shortlisted ✅")
        else:
            st.warning("Needs improvement. Consider adding missing keywords.")

        st.markdown("### 📌 JD Keywords")
        st.write(jd_keywords)

        st.markdown("### 📌 Resume Keywords")
        st.write(cv_keywords)

        missing = list(set(jd_keywords) - set(cv_keywords))
        if missing:
            st.markdown("### ❌ Missing Keywords")
            st.write(missing)

        # Wordclouds
        show_wordcloud("☁️ JD Wordcloud", jd_keywords)
        show_wordcloud("☁️ Resume Wordcloud", cv_keywords)

        # PDF Download
        report = generate_pdf_report(jd_keywords, cv_keywords, score)
        st.markdown(get_pdf_download_link(report), unsafe_allow_html=True)
    else:
        st.error("Please upload or paste both Job Description and Resume.")
