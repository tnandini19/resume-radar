import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from resume_parser import extract_text_from_pdf, extract_resume_keywords
from job_parser import extract_job_description
from match_agent import calculate_match_score
from fpdf import FPDF

# Function to check the current theme and adjust colors
def get_theme_colors():
    theme = st.get_option("theme.base")
    if theme == "light":
        bg_color = 'white'
        text_color = 'black'
    else:
        bg_color = 'black'
        text_color = 'white'
    return bg_color, text_color

# Set the theme-aware colors
bg_color, text_color = get_theme_colors()

# Streamlit Layout
st.set_page_config(page_title="ResumeRadar", page_icon=":guardsman:", layout="wide")
st.title("ResumeRadar: Job-Resume Matchmaker")

# Use theme-aware text colors for header
st.markdown(f"<h1 style='color:{text_color};'>Match Your Resume to Job Descriptions</h1>", unsafe_allow_html=True)

# Sidebar for file uploads
st.sidebar.header("Upload Files")
cv_pdf = st.sidebar.file_uploader("Upload Resume (PDF)", type=["pdf"], key="cv")
jd_pdf = st.sidebar.file_uploader("Upload Job Description (PDF)", type=["pdf"], key="jd")

if cv_pdf and jd_pdf:
    # Extract text from the PDFs
    cv_text = extract_text_from_pdf(cv_pdf)
    jd_text = extract_text_from_pdf(jd_pdf)

    # Extract keywords from the resume and job description
    cv_keywords = extract_resume_keywords(cv_text)
    jd_keywords = extract_job_description(jd_text)

    # Calculate the match score between resume and job description
    score, matched_keywords = calculate_match_score(jd_keywords, cv_keywords)

    # Display match score and matched keywords
    st.subheader(f"Match Score: {score}%")
    st.markdown(f"Matched Keywords: {', '.join(matched_keywords)}", unsafe_allow_html=True)

    # Display the WordCloud for keywords
    wordcloud = WordCloud(width=800, height=400, background_color=bg_color, colormap='Blues' if bg_color == 'light' else 'Oranges').generate(' '.join(cv_keywords + jd_keywords))

    st.subheader("WordCloud of Keywords")
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(plt)

    # Generate the match report as a PDF
    pdf_output = generate_pdf_report(jd_keywords, cv_keywords, score)
    with open(pdf_output, "rb") as f:
        st.download_button("Download Match Report", f, file_name="match_report.pdf", mime="application/pdf")

else:
    st.warning("Please upload both a Resume and a Job Description.")

# Function to generate PDF report
def generate_pdf_report(jd_keywords, cv_keywords, score):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="ResumeRadar Match Report", ln=True, align="C")
    pdf.ln(10)

    # Add match score
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Match Score: {score}%", ln=True)
    pdf.ln(5)

    # Add JD and Resume keywords
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Job Description Keywords:", ln=True)
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
