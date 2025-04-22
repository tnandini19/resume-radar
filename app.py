import streamlit as st
import spacy
import fitz  # PyMuPDF
from fpdf import FPDF
import base64
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from jd_extractor import extract_keywords as extract_jd_keywords, keyword_match_score
from resume_parser import extract_text_from_pdf, extract_resume_keywords

# --- Bias Detection ---
def detect_bias_terms(text):
    biased_terms = {
        "rockstar": "Use 'expert' or 'skilled professional'",
        "ninja": "Use 'developer' or 'engineer'",
        "guru": "Use 'specialist' or 'expert'",
        "he": "Use gender-neutral language",
        "she": "Use gender-neutral language",
        "dominant": "Use 'strong' or 'leading'",
        "aggressive": "Use 'assertive' or 'proactive'",
        "fearless": "Use 'confident'"
    }
    detected = {term: msg for term, msg in biased_terms.items() if term in text.lower()}
    return detected

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

# 💡 Theme Toggle Feature
theme = st.radio("🌓 Choose Theme", ("Light", "Dark"), horizontal=True)

if theme == "Dark":
    st.markdown(""" 
        <style> 
            html, body, .stApp { 
                background-color: #181818; 
                color: white; 
            } 
            .stTextInput > div > div > input, 
            .stTextArea > div > textarea, 
            .stFileUploader > div, 
            .stFileUploader label, 
            .stTextArea textarea { 
                background-color: #262730; 
                color: white; 
            } 
            .stButton > button { 
                background-color: #444; 
                color: white; 
                border: 1px solid #666; 
            } 
            .css-1cpxqw2, .css-1v3fvcr, .css-1kyxreq, .css-1aehpvj { 
                background-color: #262730 !important; 
                color: white !important; 
            } 
            .css-1cpxqw2:focus, .css-1v3fvcr:focus { 
                border-color: #888 !important; 
            } 
            .stRadio label { 
                color: white !important; 
            } 
            .stRadio input[type="radio"]:checked + label { 
                color: white !important; 
            } 
        </style> 
    """, unsafe_allow_html=True)
else:
    st.markdown(""" 
        <style> 
            html, body, .stApp { 
                background-color: white; 
                color: black; 
            } 
            .stTextInput > div > div > input, 
            .stTextArea > div > textarea, 
            .stFileUploader > div, 
            .stFileUploader label, 
            .stTextArea textarea { 
                background-color: #f5f5f5; 
                color: black; 
            } 
            .stButton > button { 
                background-color: #4CAF50; 
                color: white; 
                border: none; 
            } 
            .css-1cpxqw2, .css-1v3fvcr, .css-1kyxreq, .css-1aehpvj { 
                background-color: #f5f5f5 !important; 
                color: black !important; 
            } 
            .stRadio label { 
                color: black !important; 
            } 
            .stRadio input[type="radio"]:checked + label, 
            .stRadio input[type="radio"]:hover + label { 
                color: black !important; 
            } 
        </style> 
    """, unsafe_allow_html=True)


st.title("📄 ResumeRadar: JD ↔️ Resume Analyzer")
st.markdown("""
Welcome to **ResumeRadar** – Your AI-powered job-fit analyzer.  
Upload your **Resume** and the **Job Description (JD)** to get:
- ✅ Match score  
- 📌 Missing keywords  
- ☁️ Wordclouds  
- 🧾 Downloadable PDF report
""")

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
            
            bias_jd = detect_bias_terms(jd_input)
            bias_cv = detect_bias_terms(cv_input)

        if bias_jd or bias_cv:
            st.markdown("### ⚠️ Bias Alert")
            if bias_jd:
                st.warning("Bias detected in **Job Description**:")
                for term, suggestion in bias_jd.items():
                    st.write(f"- **{term}** → {suggestion}")
            if bias_cv:
                st.warning("Bias detected in **Resume**:")
                for term, suggestion in bias_cv.items():
                    st.write(f"- **{term}** → {suggestion}")
    
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
                # Generate PDF and show download link
        report_path = generate_pdf_report(jd_keywords, cv_keywords, score)
        st.markdown("### 📄 Download Match Report")
        st.markdown(get_pdf_download_link(report_path), unsafe_allow_html=True)
