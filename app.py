import streamlit as st
import pandas as pd
import spacy
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from resume_parser import extract_text_from_pdf, extract_resume_keywords
from job_parser import extract_job_description
from match_engine import calculate_match_score
from fpdf import FPDF
import base64
import fitz
import os

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Set page config
st.set_page_config(page_title="ResumeRadar", layout="wide")

# Detect current theme
current_theme = st.get_option("theme.base")
background_color = "#FFFFFF" if current_theme == "light" else "#0E1117"
text_color = "#000000" if current_theme == "light" else "#FFFFFF"

# Custom styling
st.markdown(f"""
    <style>
    .main {{
        background-color: {background_color};
        color: {text_color};
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {text_color};
    }}
    .reportview-container .markdown-text-container {{
        font-family: 'Segoe UI', sans-serif;
    }}
    </style>
""", unsafe_allow_html=True)

# Title Section
st.markdown(f"<h1 style='text-align: center;'>📄 ResumeRadar</h1>", unsafe_allow_html=True)

# Uploaders
st.markdown("### Upload Files")
col1, col2 = st.columns(2)

with col1:
    cv_pdf = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="cv")
with col2:
    jd_txt = st.file_uploader("Upload Job Description (PDF/TXT)", type=["pdf", "txt"], key="jd")

# File processing
if cv_pdf and jd_txt:
    with st.spinner("Processing documents and calculating match score..."):

        # Extract text
        cv_text = extract_text_from_pdf(cv_pdf)
        jd_text = extract_text_from_pdf(jd_txt) if jd_txt.name.endswith(".pdf") else jd_txt.read().decode("utf-8")

        # Extracted keywords
        cv_keywords = extract_resume_keywords(cv_text)
        jd_keywords = extract_resume_keywords(jd_text)

        # Match Score Calculation
        score, matched_keywords = calculate_match_score(cv_keywords, jd_keywords)

        # Show Score
        st.success(f"✅ Match Score: {score}%")

        # Matched keywords
        st.markdown("#### ✅ Matched Keywords")
        st.write(", ".join(matched_keywords))

        # WordCloud
        st.markdown("#### ☁️ Resume Keyword WordCloud")
        wordcloud = WordCloud(width=800, height=400, background_color=background_color, colormap='Set2').generate(cv_text)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

        # PDF Preview (optional)
        with st.expander("🔍 Preview Uploaded Resume"):
            with open("temp_resume.pdf", "wb") as f:
                f.write(cv_pdf.getbuffer())
            with fitz.open("temp_resume.pdf") as doc:
                for page in doc:
                    pix = page.get_pixmap()
                    st.image(pix.tobytes("png"))

        # Downloadable Report
        st.markdown("### 📥 Download Match Report")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="ResumeRadar - Match Report", ln=True, align='C')
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt=f"Match Score: {score}%")
        pdf.ln(5)
        pdf.multi_cell(0, 10, txt="Matched Keywords: " + ", ".join(matched_keywords))

        report_path = "match_report.pdf"
        pdf.output(report_path)

        with open(report_path, "rb") as file:
            btn = st.download_button(
                label="📄 Download PDF Report",
                data=file,
                file_name="ResumeRadar_Report.pdf",
                mime="application/pdf"
            )

        # Clean up
        os.remove("temp_resume.pdf")
        os.remove(report_path)
else:
    st.info("⬆️ Please upload both a resume and a job description to proceed.")
