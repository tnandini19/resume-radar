import streamlit as st
import spacy
import fitz  # PyMuPDF
from fpdf import FPDF
import base64
from match_agent import calculate_match_score

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

# --- PDF Text Extractor ---
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

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
    cv_input = extract_text_from_pdf(cv_pdf)

# Match Button
if st.button("🔍 Analyze & Match"):
    if jd_input and cv_input:
        with st.spinner("🔍 Analyzing and calculating match score..."):
            jd_keywords = extract_keywords(jd_input)
            cv_keywords = extract_keywords(cv_input)
            score = calculate_match_score(jd_keywords, cv_keywords)

        # Results
        st.markdown(f"### ✅ Match Score: `{score}%`")
        st.markdown("**JD Keywords:**")
        st.write(jd_keywords)
        st.markdown("**Resume Keywords:**")
        st.write(cv_keywords)

        if score >= 60:
            st.success("🎯 Candidate SHORTLISTED for interview!")
        else:
            st.warning("❌ Candidate NOT shortlisted. Needs closer alignment with JD.")

        # PDF Report Download
        pdf_file = generate_pdf_report(jd_keywords, cv_keywords, score)
        st.markdown(get_pdf_download_link(pdf_file), unsafe_allow_html=True)
    else:
        st.error("Please paste or upload both Job Description and Resume.")
