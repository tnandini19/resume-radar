import spacy
import PyPDF2

# Load the SpaCy English model
nlp = spacy.load("en_core_web_sm")

# ---------------------------- #
# PDF Text Extractor          #
# ---------------------------- #

def extract_text_from_pdf(pdf_path):
    """Extract raw text from a PDF file."""
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

# ---------------------------- #
# Resume Keyword Extractor    #
# ---------------------------- #

def extract_resume_keywords(text):
    """Extracts NOUN and PROPER NOUN keywords from resume text."""
    doc = nlp(text)
    keywords = [
        token.text.lower()
        for token in doc
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and token.is_alpha
    ]
    return list(set(keywords))

# ---------------------------- #
# Test Code                   #
# ---------------------------- #

if __name__ == "__main__":
    # Change this path to your local resume PDF
    pdf_path = "sample_resume.pdf"

    resume_text = extract_text_from_pdf(pdf_path)
    resume_keywords = extract_resume_keywords(resume_text)

    print("👤 Resume Text:\n", resume_text[:300], "...\n")
    print("🔑 Resume Keywords:", resume_keywords)
