import streamlit as st
import spacy
import fitz  # PyMuPDF
from fpdf import FPDF
import base64
from jd_extractor import extract_keywords as extract_jd_keywords, keyword_match_score
from resume_parser import extract_text_from_pdf, extract_resume_keywords

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# --- Keyword Extractor --- (JD)
def extract_keywords(text):
    doc = nlp(text)
    keywords = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and token.is_alpha:
            keywords.append(token.text.lower())
    return list(set(keywords))

# --- PDF Text Extractor --- (from Resume)
def extract_resume_from_file(uploaded_file):
    """Helper function to save the uploaded file temporarily and extract text."""
    with open("temp_resume.pdf", "wb") as f:
        f.write(uploaded_file.read())
    return extract_text_from_pdf("temp_resume.pdf")

# --- PDF Report Generator ---
def generate_pdf_report(jd_keywords, cv_keywords, score):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

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
st.set_page_config(page_title="ResumeRadar", page_icon="📄")
st.title("📄 ResumeRadar: JD ↔️ CV Matcher")
st.markdown("""
Welcome to **ResumeRadar** – Your AI-powered job-fit analyzer.  
Upload your **Resume** and the **Job Description (JD)** below to get a match score, smart insights, and shortlist recommendations. 🚀
""")

# Theme toggle (Light/Dark Mode)
theme = st.radio("Choose Theme", ("Light", "Dark"))
if theme == "Dark":
    st.markdown("""
        <style>
            body {
                background-color: #181818;
                color: white;
            }
            .stButton>button {
                background-color: #4CAF50;
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            body {
                background-color: white;
                color: black;
            }
        </style>
    """, unsafe_allow_html=True)

# Text Area Input
jd_input = st.text_area("📝 Paste Job Description:", height=200)
cv_input = st.text_area("👤 Paste Resume:", height=200)

# PDF Upload Option
st.markdown("### 📄 Or Upload PDFs (Optional)")
jd_pdf = st.file_uploader("Upload JD (PDF)", type=["pdf"], key="jd")
cv_pdf = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="cv")

# Use PDF content if available
if jd_pdf:
    jd_input = extract_text_from_pdf(jd_pdf)
if cv_pdf:
    cv_input = extract_resume_from_file(cv_pdf)

# Match Button
if st.button("🔍 Analyze & Match"):
    if jd_input and cv_input:
        with st.spinner("🔍 Analyzing and calculating match score..."):
            # Extract JD keywords using custom JD extractor
            jd_keywords = extract_jd_keywords(jd_input)

            # Extract resume keywords
            cv_keywords = extract_keywords(cv_input)

            # Calculate match score using the match scoring function
            score, matched_keywords = keyword_match_score(jd_keywords, cv_keywords)

        # Results
        st.markdown(f"### ✅ Match Score: `{score}%`")
        st.markdown("**JD Keywords:**")
        st.write(jd_keywords)
        st.markdown("**Resume Keywords:**")
        st.write(cv_keywords)

        # Display result message based on match score
        if score >= 60:
            st.success("🎯 Candidate SHORTLISTED for interview!")
        else:
            st.warning("❌ Candidate NOT shortlisted. Needs closer alignment with JD.")

        # Highlight missing keywords
        missing_keywords = list(set(jd_keywords) - set(cv_keywords))
        if missing_keywords:
            st.markdown("### ❌ Missing Keywords:")
            st.write(missing_keywords)

        # PDF Report Download
        pdf_file = generate_pdf_report(jd_keywords, cv_keywords, score)
        st.markdown(get_pdf_download_link(pdf_file), unsafe_allow_html=True)
    else:
        st.error("Please paste or upload both Job Description and Resume.")
