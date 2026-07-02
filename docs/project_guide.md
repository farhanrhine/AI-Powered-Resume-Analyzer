# 🚀 AI-Powered Resume Analyzer — Build It Yourself Guide
> **Philosophy**: Skeletons are provided. You fill in the body. Each `# TODO` is one thing you write yourself.

---

## 🗂️ Target Project Structure

```
AI-Powered-Resume-Analyzer/
│
├── app.py                      ← Streamlit UI (Phase 6)
├── .env                        ← GOOGLE_API_KEY=your_key_here
├── pyproject.toml              ← Already set up ✅
│
└── src/
    ├── __init__.py             ← Keep empty, just needs to exist
    ├── utils.py                ← Phase 7 (build first, used by all)
    ├── resume_parser.py        ← Phase 1
    ├── jd_parser.py            ← Phase 2
    ├── matching_engine.py      ← Phase 3
    ├── gap_analysis.py         ← Phase 4
    └── suggestion_generator.py ← Phase 5
```

---

## ✅ Recommended Build Order
```
utils.py → resume_parser.py → jd_parser.py → matching_engine.py → gap_analysis.py → suggestion_generator.py → app.py
```
> **Rule**: Test each file with a `print()` at the bottom before moving to the next phase.

---

---

# 📦 PHASE 0 — utils.py (Build This First!)

**Why first?** All other files will import the LLM from here. Build it once, use everywhere.

```python
# src/utils.py

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# TODO: Call load_dotenv() here so .env is loaded when this module is imported


def get_llm():
    """
    Returns a configured Gemini LLM instance.
    All other modules should call this instead of setting up the LLM themselves.
    """
    # TODO: Read GOOGLE_API_KEY from environment using os.getenv()
    api_key = ...

    # TODO: Return a ChatGoogleGenerativeAI instance
    # Hint: model="gemini-2.0-flash", temperature=0.3 is a good start
    return ChatGoogleGenerativeAI(
        model=...,
        google_api_key=...,
        temperature=...
    )


def clean_text(text: str) -> str:
    """
    Strips and normalizes a string.
    Removes extra blank lines, trims whitespace.
    """
    if not text:
        return ""
    
    # TODO: Split into lines, strip each line, remove empty ones, rejoin
    lines = text.splitlines()
    # Hint: use a list comprehension with .strip() and filter out empty strings
    cleaned_lines = ...
    
    return "\n".join(cleaned_lines)
```

### 🧪 Test it:
Add this at the bottom temporarily:
```python
if __name__ == "__main__":
    llm = get_llm()
    print(type(llm))  # Should print something like <class 'ChatGoogleGenerativeAI'>
    print(clean_text("  hello   \n\n  world  "))  # Should print: hello\nworld
```
Run with: `uv run python src/utils.py`

---

---

# 📦 PHASE 1 — resume_parser.py

```python
# src/resume_parser.py

import pdfplumber
from src.utils import clean_text


def parse_resume(pdf_file) -> str:
    """
    Extracts and returns all text from a PDF file.
    
    Args:
        pdf_file: A file-like object (from Streamlit's st.file_uploader or open())
    
    Returns:
        str: The full extracted text, cleaned and joined.
    """
    all_text = []

    try:
        # TODO: Open the pdf_file using pdfplumber.open()
        # Hint: use `with pdfplumber.open(pdf_file) as pdf:`
        with ...:
            # TODO: Loop through pdf.pages
            for page in ...:
                # TODO: Extract text from each page using page.extract_text()
                text = ...
                
                # TODO: Only append if text is not None and not empty
                if text:
                    all_text.append(text)

    except Exception as e:
        # TODO: Print a helpful error message and return an empty string
        print(f"Error reading PDF: {e}")
        return ""

    # TODO: Join all_text into one big string (use "\n" as separator)
    # Then pass it through clean_text() before returning
    full_text = ...
    return clean_text(full_text)
```

### 🧪 Test it:
```python
if __name__ == "__main__":
    # Replace with a real PDF path on your machine
    with open("sample_resume.pdf", "rb") as f:
        result = parse_resume(f)
        print(result[:500])  # Print first 500 chars to verify
```

---

---

# 📦 PHASE 2 — jd_parser.py

```python
# src/jd_parser.py

from src.utils import clean_text


def parse_jd(jd_text: str) -> str:
    """
    Cleans and normalizes job description text entered by the user.
    
    Args:
        jd_text: Raw string from a text area input.
    
    Returns:
        str: Cleaned job description text.
    """
    # TODO: Check if jd_text is empty or None, return "" early if so
    if not jd_text or ...:
        return ""

    # TODO: Run it through clean_text() from utils
    cleaned = ...

    # Optional: Check word count and warn if too short
    word_count = len(cleaned.split())
    if word_count < 30:
        print("Warning: Job description seems very short.")

    return cleaned
```

### 🧪 Test it:
```python
if __name__ == "__main__":
    sample = "   \n\nSoftware Engineer \n\n Must know Python   and SQL.  \n"
    print(parse_jd(sample))
```

---

---

# 📦 PHASE 3 — matching_engine.py

> **This is the core of your app.** Take your time with the prompt.

```python
# src/matching_engine.py

import json
from src.utils import get_llm


def analyze_match(resume_text: str, jd_text: str) -> dict:
    """
    Uses Gemini to compare a resume against a job description.
    Returns a match score, matched skills, and a summary.
    
    Returns:
        dict with keys: 'score' (int), 'matched_skills' (list), 'summary' (str)
    """
    llm = get_llm()

    # TODO: Write a prompt that instructs Gemini to:
    # 1. Compare the resume and JD
    # 2. Give a match score from 0 to 100
    # 3. List skills/keywords found in BOTH
    # 4. Write a short 2-3 sentence summary
    # 5. IMPORTANT: Tell it to respond with ONLY valid JSON, no extra text
    #
    # Hint: Use an f-string so you can insert resume_text and jd_text
    prompt = f"""
    You are a resume screening expert. Compare the following resume and job description.
    
    RESUME:
    {resume_text}
    
    JOB DESCRIPTION:
    {jd_text}
    
    # TODO: Complete the instruction part of this prompt.
    # Ask for a JSON response with exactly these keys:
    # - "score": integer 0-100
    # - "matched_skills": list of strings
    # - "summary": string
    # Tell it: respond with ONLY the JSON object, no markdown, no explanation.
    """

    try:
        # TODO: Call llm.invoke(prompt) to get the response
        response = ...
        
        # TODO: The response object has a .content attribute (it's a string)
        raw_text = response.content
        
        # TODO: Parse the JSON string into a Python dict using json.loads()
        result = json.loads(raw_text)
        
        return result

    except json.JSONDecodeError:
        # The LLM didn't return valid JSON — return a safe fallback
        print("Warning: LLM did not return valid JSON")
        return {"score": 0, "matched_skills": [], "summary": "Could not parse response."}
    
    except Exception as e:
        print(f"Error in analyze_match: {e}")
        return {"score": 0, "matched_skills": [], "summary": "An error occurred."}
```

### 🧪 Test it:
```python
if __name__ == "__main__":
    sample_resume = "Python developer with 3 years experience in REST APIs and SQL databases."
    sample_jd = "We need a Python developer with REST API experience and SQL knowledge."
    
    result = analyze_match(sample_resume, sample_jd)
    print(result)
    # Expected: {'score': 85, 'matched_skills': ['Python', 'REST API', 'SQL'], 'summary': '...'}
```

---

---

# 📦 PHASE 4 — gap_analysis.py

```python
# src/gap_analysis.py

import json
from src.utils import get_llm


def find_gaps(resume_text: str, jd_text: str) -> list:
    """
    Identifies skills and requirements in the JD that are missing from the resume.
    
    Returns:
        list of strings, each describing a specific gap.
    """
    llm = get_llm()

    # TODO: Write a prompt that asks Gemini to:
    # 1. Look at what the JD requires
    # 2. Check what is NOT present in the resume
    # 3. Return a JSON array (list) of gap descriptions
    # Example output: ["No mention of Docker", "Missing AWS experience", ...]
    # Again: tell it to return ONLY valid JSON, nothing else.
    prompt = f"""
    # TODO: Write your prompt here.
    # Resume: {resume_text}
    # Job Description: {jd_text}
    """

    try:
        response = llm.invoke(prompt)
        raw_text = response.content
        
        # TODO: Parse the response as a JSON list
        gaps = json.loads(raw_text)
        
        # Make sure it's actually a list
        if not isinstance(gaps, list):
            return []
        
        return gaps

    except Exception as e:
        print(f"Error in find_gaps: {e}")
        return []
```

---

---

# 📦 PHASE 5 — suggestion_generator.py

```python
# src/suggestion_generator.py

import json
from src.utils import get_llm


def generate_suggestions(gaps: list, resume_text: str) -> list:
    """
    Given a list of skill gaps and the resume context, generates
    specific, actionable suggestions to improve the resume.
    
    Returns:
        list of suggestion strings.
    """
    if not gaps:
        return ["Your resume looks well-aligned! No major gaps found."]

    llm = get_llm()

    # Convert gaps list to a readable string for the prompt
    gaps_str = "\n".join(f"- {gap}" for gap in gaps)

    # TODO: Write a prompt that:
    # 1. Shows the gaps
    # 2. Shows the resume (for context)
    # 3. Asks for specific, actionable suggestions for each gap
    # 4. Returns a JSON array of suggestion strings
    # Good suggestion example: "Add a section listing Docker projects you've worked on"
    # Bad suggestion example: "Learn Docker" (too vague)
    prompt = f"""
    # TODO: Write your prompt here.
    # Gaps: {gaps_str}
    # Resume context: {resume_text}
    """

    try:
        response = llm.invoke(prompt)
        raw_text = response.content
        
        # TODO: Parse JSON list from response
        suggestions = json.loads(raw_text)
        
        if not isinstance(suggestions, list):
            return []
        
        return suggestions

    except Exception as e:
        print(f"Error in generate_suggestions: {e}")
        return []
```

---

---

# 📦 PHASE 6 — app.py (The Final Assembly)

```python
# app.py

import streamlit as st

# TODO: Import your 5 functions from src/
from src.resume_parser import parse_resume
from src.jd_parser import parse_jd
from src.matching_engine import analyze_match
from src.gap_analysis import find_gaps
from src.suggestion_generator import generate_suggestions


# ── Page Config ──────────────────────────────────────────
# TODO: Set page title, icon, and layout using st.set_page_config()
st.set_page_config(
    page_title=...,
    page_icon=...,
    layout="wide"
)

# ── Header ───────────────────────────────────────────────
st.title("🎯 AI-Powered Resume Analyzer")
st.markdown("Upload your resume and paste a job description to get your match score and improvement tips.")

st.divider()

# ── Input Section ─────────────────────────────────────────
# TODO: Create two columns using st.columns([1, 1])
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📄 Your Resume")
    # TODO: Add a file uploader that only accepts PDF files
    uploaded_file = st.file_uploader(..., type=["pdf"])

with col2:
    st.subheader("📋 Job Description")
    # TODO: Add a text area for the JD. Give it a height of about 300
    jd_input = st.text_area(..., height=300)

st.divider()

# ── Analyze Button ────────────────────────────────────────
# TODO: Add a centered button labeled "Analyze My Resume"
analyze_btn = st.button("🔍 Analyze My Resume", use_container_width=True)

# ── Results Section ───────────────────────────────────────
if analyze_btn:
    # Validate inputs before proceeding
    if not uploaded_file:
        st.error("Please upload a PDF resume first.")
    elif not jd_input.strip():
        st.error("Please paste a job description.")
    else:
        # TODO: Use st.spinner() to show a loading message while processing
        with st.spinner("Analyzing your resume... this may take a few seconds ⏳"):
            
            # Step 1: Parse inputs
            resume_text = parse_resume(uploaded_file)
            jd_text = parse_jd(jd_input)
            
            # Step 2: Run analysis
            match_result = analyze_match(resume_text, jd_text)
            gaps = find_gaps(resume_text, jd_text)
            suggestions = generate_suggestions(gaps, resume_text)

        # ── Display Results ───────────────────────────────
        st.success("Analysis complete!")
        st.divider()

        # TODO: Show match score using st.metric()
        # Hint: st.metric(label="Match Score", value=f"{score}%")
        score = match_result.get("score", 0)
        matched_skills = match_result.get("matched_skills", [])
        summary = match_result.get("summary", "")

        r1, r2 = st.columns([1, 2])
        with r1:
            st.metric(label="🎯 Match Score", value=f"{score}%")
        with r2:
            st.markdown("**📝 Summary**")
            st.write(summary)

        st.divider()

        # TODO: Show matched skills using st.success() or a loop with st.badge / st.write
        st.subheader("✅ Matched Skills")
        if matched_skills:
            # Hint: You can display them as a comma-separated string or loop through them
            st.write(", ".join(matched_skills))
        else:
            st.write("No matching skills found.")

        st.divider()

        # TODO: Show gaps list using st.warning() for each item
        st.subheader("⚠️ Skill Gaps")
        if gaps:
            for gap in gaps:
                st.warning(gap)
        else:
            st.success("No major gaps detected!")

        st.divider()

        # TODO: Show suggestions using st.info() for each item, numbered
        st.subheader("💡 How to Improve Your Resume")
        for i, suggestion in enumerate(suggestions, start=1):
            st.info(f"**{i}.** {suggestion}")

        # Optional: Show raw resume text in a collapsible section
        with st.expander("📄 View extracted resume text"):
            st.text(resume_text)
```

---

---

## 🚩 Common Gotchas

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: src` | Run from project root: `uv run streamlit run app.py` |
| LLM returns text with ```json ``` markers | Strip it: `raw_text.strip().strip("```json").strip("```")` before `json.loads()` |
| `None` from `page.extract_text()` | Always check `if text:` before appending |
| API key not found | Make sure `.env` has `GOOGLE_API_KEY=...` and you call `load_dotenv()` |
| Gemini response isn't JSON | Add `"Respond with ONLY valid JSON. No markdown. No explanation."` at end of prompt |

---

## 🧠 The Mental Model

```
PDF File ──► parse_resume() ──► resume_text (string)
JD Text  ──► parse_jd()     ──► jd_text     (string)
                                    │
                          ┌─────────┼─────────┐
                          ▼         ▼         ▼
                   analyze_match  find_gaps  (combined)
                          │         │
                          ▼         ▼
                      match_result  gaps ──► generate_suggestions()
                                                    │
                                                    ▼
                                             suggestions (list)
```

All of these feed into `app.py` to display results.

---

*You know more than you think. The skeleton is there — just fill in the blanks. 💪*
