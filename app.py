import streamlit as st
import re
import math
from collections import Counter
from pypdf import PdfReader

st.set_page_config(page_title="AI Resume Analyzer", page_icon="🤖", layout="wide")

if "users" not in st.session_state:
    st.session_state.users = {"admin": "1234", "student": "pass123"}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""

JOBS_DB = [
    {"title": "Data Scientist", "company": "TCS", "skills": ["python", "machine learning", "sql", "pandas", "statistics", "deep learning"], "desc": "Looking for a Data Scientist skilled in Python, ML algorithms, and SQL data analysis."},
    {"title": "Frontend Developer", "company": "Infosys", "skills": ["html", "css", "javascript", "react", "git", "ui/ux"], "desc": "Seeking a Frontend Developer with strong React, JavaScript, and responsive CSS skills."},
    {"title": "Python Backend Developer", "company": "Wipro", "skills": ["python", "django", "flask", "rest api", "sql", "docker"], "desc": "Backend engineer needed to build scalable REST APIs using Python, Flask, Django, and SQL."},
    {"title": "AI / ML Engineer", "company": "Accenture", "skills": ["python", "nlp", "tensorflow", "pytorch", "spacy", "ai"], "desc": "AI Engineer to build NLP pipelines, resume parsers, and deep learning models."},
    {"title": "Data Analyst", "company": "Deloitte", "skills": ["excel", "sql", "power bi", "tableau", "python", "data analysis"], "desc": "Data Analyst to create dashboards in Power BI and query data using SQL."}
]

SKILLS_DB = ["python", "java", "c++", "html", "css", "javascript", "react", "angular", "sql", "mysql", "mongodb", "machine learning", "deep learning", "nlp", "ai", "data analysis", "pandas", "numpy", "tensorflow", "pytorch", "flask", "django", "git", "docker", "aws", "excel", "power bi", "tableau", "rest api"]

def extract_skills(text):
    text_lower = text.lower()
    return list(set([s for s in SKILLS_DB if re.search(r'\b' + re.escape(s) + r'\b', text_lower)]))

def cosine_sim(text1, text2):
    w1, w2 = Counter(re.findall(r'\w+', text1.lower())), Counter(re.findall(r'\w+', text2.lower()))
    inter = set(w1.keys()) & set(w2.keys())
    num = sum([w1[x] * w2[x] for x in inter])
    den = math.sqrt(sum([w1[x]**2 for x in w1])) * math.sqrt(sum([w2[x]**2 for x in w2]))
    return round((num / den) * 100, 2) if den else 0.0

if not st.session_state.logged_in:
    st.title("🤖 AI Resume Analyzer & Job Portal")
    t1, t2 = st.tabs(["Login", "Sign Up"])
    with t1:
        u = st.text_input("Username (admin)")
        p = st.text_input("Password (1234)", type="password")
        if st.button("Login"):
            if u in st.session_state.users and st.session_state.users[u] == p:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials! Use admin / 1234")
    with t2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            if nu and np:
                st.session_state.users[nu] = np
                st.success("Account Created! Go to Login tab.")
else:
    st.sidebar.success(f"Logged in as: {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("📄 AI Resume Analysis & Job Recommendation")
    pdf_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
    manual_text = st.text_area("Or Paste Resume Text / Skills here:")

    resume_text = ""
    if pdf_file:
        reader = PdfReader(pdf_file)
        resume_text = " ".join([page.extract_text() or "" for page in reader.pages])
    elif manual_text:
        resume_text = manual_text

    if st.button("Analyze Resume") and resume_text:
        skills = extract_skills(resume_text)
        score = min(100, len(skills) * 12 + 20)
        
        c1, c2 = st.columns(2)
        c1.metric("ATS Score", f"{score} / 100")
        c1.progress(score / 100)
        c2.subheader("Extracted Skills")
        c2.info(", ".join([s.upper() for s in skills]) if skills else "No skills found")

        st.subheader("🎯 Recommended Jobs")
        res = []
        for j in JOBS_DB:
            s = cosine_sim(resume_text, j["desc"] + " " + " ".join(j["skills"]))
            miss = [x for x in j["skills"] if x not in skills]
            res.append((s, j, miss))
        res.sort(key=lambda x: x[0], reverse=True)

        for s, j, miss in res[:3]:
            with st.expander(f"🏢 {j['title']} at {j['company']} — Match: {s}%", expanded=True):
                st.write(f"**Description:** {j['desc']}")
                st.write(f"**Missing Skills:** {', '.join(miss).upper() if miss else 'None (Perfect Match!)'}")
                
