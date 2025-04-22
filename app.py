import streamlit as st
import spacy
import fitz  # PyMuPDF
from fpdf import FPDF
import base64
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from jd_extractor import extract_keywords as extract_jd_keywords, keyword_match_score
from resume_parser import extract_text_from_pdf, extract_resume_keywords
from datetime import datetime
import hashlib
import os
import json

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

# --- User Authentication (Login/Signup) ---
def create_user_account(username, password):
    users_db = "users_db.json"
    if os.path.exists(users_db):
        with open(users_db, 'r') as f:
            users = json.load(f)
    else:
        users = {}
    
    if username in users:
        return False  # User already exists
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    users[username] = hashed_password

    with open(users_db, 'w') as f:
        json.dump(users, f)
    return True

def authenticate_user(username, password):
    users_db = "users_db.json"
    if os.path.exists(users_db):
        with open(users_db, 'r') as f:
            users = json.load(f)
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if username in users and users[username] == hashed_password:
            return True
    return False

# --- Saving and Retrieving Data ---
def save_user_data(username, data):
    data_file = f"{username}_data.json"
    with open(data_file, 'w') as f:
        json.dump(data, f)

def retrieve_user_data(username):
    data_file = f"{username}_data.json"
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            return json.load(f)
    return {}

# --- Streamlit UI ---
st.set_page_config(page_title="ResumeRadar", page_icon="📄", layout="wide")

# Check if user is logged in (using session_state)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 💡 Theme Toggle Feature
theme = st.radio("🌓 Choose Theme", ("Light", "Dark"), horizontal=True)

if theme == "Dark":
    st.markdown("""
        <style>
            html, body, .stApp {
                background-color: #181818;
                color: #FFFFFF;
            }
            h1, h2, h3, h4, h5, h6, p, div, span {
                color: #FFFFFF !important;
            }
            .stTextInput input,
            .stTextArea textarea,
            .stFileUploader,
            .stSelectbox div,
            .stButton>button {
                background-color: #2c2c2c !important;
                color: #FFFFFF !important;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            html, body, .stApp {
                background-color: #FFFFFF;
                color: #000000;
            }
            h1, h2, h3, h4, h5, h6, p, div, span {
                color: #000000 !important;
            }
            .stTextInput input,
            .stTextArea textarea,
            .stFileUploader,
            .stSelectbox div,
            .stButton>button {
                background-color: #f5f5f5 !important;
                color: #000000 !important;
            }
        </style>
    """, unsafe_allow_html=True)

# --- Authentication UI ---
if not st.session_state.logged_in:
    auth_option = st.radio("📑 Login or Signup", ("Login", "Signup"))

    if auth_option == "Signup":
        st.subheader("Create a new account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if password == confirm_password:
            if st.button("Create Account"):
                if create_user_account(username, password):
                    st.success("Account created successfully!")
                else:
                    st.warning("Username already taken.")
        else:
            st.warning("Passwords do not match.")
    else:
        st.subheader("Login to your account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate_user(username, password):
                st.success("Logged in successfully!")
                st.session_state.logged_in = True
                user_data = retrieve_user_data(username)
            else:
                st.error("Invalid credentials.")
else:
    # Display app features after login
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
