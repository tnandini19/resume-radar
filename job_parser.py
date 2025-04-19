# job_parser.py

import re

def extract_job_description(jd_text):
    """
    Function to extract job description text.
    You can customize this function based on your job description format.
    """
    # Sample implementation: Extract keywords (simple version)
    keywords = re.findall(r'\b[A-Za-z]+\b', jd_text)
    return keywords
