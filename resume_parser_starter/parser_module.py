import os, re
import pdfplumber
from docx import Document
import phonenumbers
from rapidfuzz import process, fuzz

SKILLS_FILE = os.path.join(os.path.dirname(__file__), "skills.csv")

def extract_text(path):
    ext = path.lower().split('.')[-1]
    if ext == "pdf":
        return extract_pdf_text(path)
    elif ext in ("docx", "doc"):
        return extract_docx_text(path)
    else:
        return ""

def extract_pdf_text(path):
    text_parts = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
    except Exception as e:
        print("pdfplumber error:", e)
    return "\n".join(text_parts)

def extract_docx_text(path):
    try:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        print("docx error:", e)
        return ""

EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,6}")
def extract_email(text):
    m = EMAIL_RE.search(text)
    return m.group(0) if m else None

def extract_phone(text, default_region=None):
    for match in phonenumbers.PhoneNumberMatcher(text, default_region):
        return phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
    return None

def load_skills():
    if not os.path.exists(SKILLS_FILE):
        return []
    with open(SKILLS_FILE, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

SKILLS = load_skills()

def match_skills(text, limit=50, score_cutoff=70):
    if not SKILLS:
        return []
    results = process.extract(text, SKILLS, scorer=fuzz.partial_ratio, limit=limit)
    picked = [r[0] for r in results if r[1] >= score_cutoff]
    seen = set()
    out = []
    for s in picked:
        if s.lower() not in seen:
            out.append(s)
            seen.add(s.lower())
    return out

def guess_name(text):
    for line in text.splitlines():
        line = line.strip()
        if line and len(line.split()) <= 5 and "@" not in line and not any(c.isdigit() for c in line):
            return line
    return None

def parse_resume(path):
    text = extract_text(path)
    parsed = {
        "text": text,
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": match_skills(text),
        "education": [],
        "experience": [],
        "name": guess_name(text)
    }
    return parsed
