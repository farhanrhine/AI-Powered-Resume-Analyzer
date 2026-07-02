# 🚀 AI-Powered Resume Analyzer — Think First, Then Build

> **The rule**: Before writing ANY line of code, ask yourself: *"What problem does this line solve?"*
> If you can't answer it, stop and think — don't type yet.

---

## 🧠 The Big Picture — WHY does this app even exist?

**The problem**: A job seeker uploads their resume to a job portal. They get rejected. They don't know why.

**The root cause**: Their resume doesn't match the job description's keywords and requirements — and they have no way to know.

**What we're building**: A tool that reads BOTH the resume and the job description, compares them using AI, and tells the person:
1. How much does your resume match this job? (a score)
2. What skills does the job ask for that you're missing? (gaps)
3. What should you do about it? (suggestions)

**That's it. Keep this in your head at all times.**

---

## 🗺️ How the app flows (read this before anything else)

```
User uploads PDF resume
        │
        ▼
[resume_parser.py] ──── extracts the text from the PDF ────► resume_text (plain string)

User pastes Job Description text
        │
        ▼
[jd_parser.py] ──── cleans the raw text ────────────────────► jd_text (plain string)

Both strings go to the AI modules:
        │
        ├──► [matching_engine.py] ──── "How similar are these?" ────► score + matched skills
        │
        ├──► [gap_analysis.py] ──── "What's missing?" ─────────────► list of gaps
        │
        └──► [suggestion_generator.py] ── "What should I do?" ──────► list of suggestions

All results go to:
[app.py] ──── displays everything in a Streamlit web page
```

**Every file you create is one step in that chain. That's why you're writing each one.**

---

## 🗂️ Project Structure

```
AI-Powered-Resume-Analyzer/
│
├── app.py                      ← The face of the app (Phase 6)
├── .env                        ← Your secret API key (never share this)
├── pyproject.toml              ← Tells Python what libraries to install
│
└── src/
    ├── __init__.py             ← Tells Python "src is a package" (keep empty)
    ├── utils.py                ← Shared tools — build this FIRST
    ├── resume_parser.py        ← Phase 1
    ├── jd_parser.py            ← Phase 2
    ├── matching_engine.py      ← Phase 3
    ├── gap_analysis.py         ← Phase 4
    └── suggestion_generator.py ← Phase 5
```

---

---

# 📦 PHASE 0 — utils.py

## ❓ WHY are we building this first?

**The problem**: Every module (matching_engine, gap_analysis, suggestion_generator) needs to talk to Google Gemini. If every file sets up the LLM connection on its own, you'd repeat the same 5 lines of code 3 times. If the model name changes, you'd have to fix it in 3 places.

**The solution**: One file that sets up the connection. Everyone else just imports it.

**Think of it like this**: `utils.py` is the power socket on the wall. Every other module plugs into it. You don't install a new power socket in every room — you wire them all to one main panel.

---

## 🧠 Mental model for `get_llm()`

```
.env file (text file on disk)
    │
    │ load_dotenv() reads it and puts values into memory
    ▼
os environment (memory)
    │
    │ os.getenv("GOOGLE_API_KEY") reads from memory
    ▼
api_key variable
    │
    │ passed to ChatGoogleGenerativeAI(google_api_key=api_key)
    ▼
LLM object — a "phone" that can call Gemini
```

**WHY does this 3-step process exist?**
Because you never want to write your API key directly in code (it could end up on GitHub). So you store it in `.env`, tell Python to read that file, then pass it to the LLM safely.

---

## ✏️ Skeleton — fill in the `...`

```python
# src/utils.py

import os                              # WHY: lets you read from OS memory (where .env values go)
from dotenv import load_dotenv         # WHY: teaches Python to read .env files
from langchain_google_genai import ChatGoogleGenerativeAI  # WHY: the library that connects to Gemini

load_dotenv()                          # WHY: actually reads .env RIGHT NOW, at import time
                                       # Without this, os.getenv() returns None


def get_llm():
    """
    Creates and returns a Gemini LLM object.
    Call this function whenever you need to talk to Gemini.
    """
    # WHY: read the API key from memory (load_dotenv() put it there)
    api_key = os.getenv("GOOGLE_API_KEY")

    # WHY: create the LLM "phone" with your account credentials
    # model = which version of Gemini to use
    # temperature = how creative/random the responses are (0 = consistent, 1 = creative)
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=...,   # TODO: pass the api_key variable you read above
        temperature=0.3,
    )


def clean_text(text: str) -> str:
    """
    Removes extra whitespace and blank lines from a string.
    WHY: AI models charge per token (word). Sending 20 blank lines wastes money and confuses the model.
    """
    if not text:          # WHY: guard against None or empty string coming in
        return ""

    lines = text.splitlines()       # WHY: split the big string into individual lines (gives a list)

    cleaned_lines = []              # WHY: a bucket to collect the lines that are actually useful

    for line in lines:
        stripped = line.strip()     # WHY: remove leading/trailing spaces from this specific line
        # TODO: only add `stripped` to cleaned_lines if it is NOT an empty string
        ...

    # WHY: join the surviving lines back into one string, separated by newlines
    return "\n".join(cleaned_lines)


# ── Test block ──────────────────────────────────────────────────────────────
# WHY: This block only runs if you run THIS file directly (python src/utils.py)
# It does NOT run when other files import utils.py — that's what __name__ controls
if __name__ == "__main__":
    llm = get_llm()
    print(type(llm))  # Should show: <class '...ChatGoogleGenerativeAI'>

    result = clean_text("  hello   \n\n   world  \n  ")
    print(repr(result))  # Should show: 'hello\nworld'
```

### 🧪 Run it:
```
uv run python src/utils.py
```
**You should see the class name and `'hello\nworld'`. If you do, Phase 0 is done.**

---

---

# 📦 PHASE 1 — resume_parser.py

## ❓ WHY are we building this?

**The problem**: The user uploads a PDF. But PDFs are not text files — they are a binary format. Python cannot just `open()` a PDF and read words from it like a `.txt` file.

**The solution**: We use `pdfplumber`, a library that knows how to decode PDFs and extract the text layer from each page.

**WHY return a plain string?** Because the AI (Gemini) only understands text. It cannot read a PDF. Our job in this file is to be the **translator** — PDF in, clean text out.

---

## 🧠 Mental model

```
PDF file (binary — Python can't read this directly)
        │
        │  pdfplumber.open() decodes it
        ▼
pdf object (has a .pages list)
        │
        │  loop through each page
        ▼
page object
        │
        │  page.extract_text() pulls out the words
        ▼
text string (or None, if the page has no text layer)
        │
        │  collect all pages, join together, clean
        ▼
one big resume_text string ← this is what we return
```

**WHY might `extract_text()` return `None`?** PDFs can be purely image-based (scanned documents). There's no text layer to extract. We must always check for this.

---

## ✏️ Skeleton — fill in the `...`

```python
# src/resume_parser.py

import pdfplumber                 # WHY: the library that can read PDF files
from src.utils import clean_text  # WHY: reuse our shared cleaning function, don't repeat it


def parse_resume(pdf_file) -> str:
    """
    Extracts all text from a PDF file and returns it as a clean string.

    Args:
        pdf_file: A file-like object (from st.file_uploader or open())

    Returns:
        str: Full resume text, cleaned.
    """
    all_text = []   # WHY: a bucket to collect text from each page

    try:
        # WHY: 'with' ensures the PDF is closed properly even if an error occurs
        with pdfplumber.open(pdf_file) as pdf:

            # WHY: loop because a resume has multiple pages
            for page in pdf.pages:

                # WHY: extract_text() decodes this page's text. Returns None for image pages.
                text = page.extract_text()

                # TODO: check if text is not None AND not empty, then append to all_text
                if ...:
                    all_text.append(text)

    except Exception as e:
        # WHY: if the PDF is corrupted or unreadable, we don't want the app to crash
        print(f"Error reading PDF: {e}")
        return ""

    # WHY: all_text is currently a list of strings (one per page)
    # We join them into one big string with newlines between pages
    full_text = "\n".join(all_text)

    # WHY: clean it before returning — remove extra whitespace that pdfplumber sometimes adds
    return clean_text(full_text)


# ── Test block ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # TODO: replace with a real PDF file path on your computer to test
    with open("your_resume.pdf", "rb") as f:   # WHY: "rb" = read binary (PDFs are binary)
        result = parse_resume(f)
        print(result[:500])   # Print first 500 chars to see if it worked
```

---

---

# 📦 PHASE 2 — jd_parser.py

## ❓ WHY are we building this?

**The problem**: The user pastes a Job Description into a text box. It's raw, messy text — extra spaces, empty lines, sometimes even copied HTML formatting.

**The solution**: Clean it before sending to the AI.

**WHY does cleaning matter?** Two reasons:
1. AI models charge by token (roughly per word). Extra blank lines = wasted money.
2. Cleaner input = cleaner output. Garbage in, garbage out.

**This module is simple on purpose.** JD text doesn't need a special library — it's already text. We just clean it.

---

## ✏️ Skeleton — fill in the `...`

```python
# src/jd_parser.py

from src.utils import clean_text   # WHY: reuse the same cleaning logic, don't duplicate it


def parse_jd(jd_text: str) -> str:
    """
    Cleans and normalizes job description text.

    Args:
        jd_text: Raw string from a text area input.

    Returns:
        str: Clean job description text.
    """
    # WHY: guard against empty input — if the user didn't type anything, return early
    if not jd_text or not jd_text.strip():
        return ""

    # TODO: pass jd_text through clean_text() and store the result
    cleaned = ...

    # WHY: warn if the JD is suspiciously short — might be a mistake
    word_count = len(cleaned.split())
    if word_count < 30:
        print(f"Warning: JD is only {word_count} words. It might be too short for a good analysis.")

    return cleaned


# ── Test block ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = "   \n\nSoftware Engineer \n\n Must know Python   and SQL.  \n"
    print(repr(parse_jd(sample)))
    # Expected: 'Software Engineer\nMust know Python   and SQL.'
```

---

---

# 📦 PHASE 3 — matching_engine.py

## ❓ WHY are we building this?

**The problem**: We have two strings — a resume and a job description. We need to know: *how similar are they?* And specifically: *what skills appear in both?*

**The solution**: Send both to Gemini and ask it to compare them. But AI models return free-form text. We need structured data (a score, a list, a summary). So we must tell the AI exactly what format to respond in.

**WHY JSON?** Because Python can't work with "Your resume scores about 78 out of 100 based on...". But it CAN work with `{"score": 78}`. We need machine-readable output.

**This is the heart of the whole app.**

---

## 🧠 Mental model for LLM calls

```
We write a prompt (a question + instructions)
        │
        │  llm.invoke(prompt)
        ▼
Gemini receives the prompt, generates a response
        │
        │  response.content  (this is a plain string)
        ▼
We get back a string like: '{"score": 78, "matched_skills": [...]}'
        │
        │  json.loads(response.content)
        ▼
Python dict: {"score": 78, "matched_skills": [...]}  ← NOW we can use it
```

**WHY `json.loads()`?** The LLM returns text, not a Python object. `json.loads()` converts the text `"{"score": 78}"` into an actual Python dictionary `{"score": 78}`.

---

## ✏️ Skeleton — fill in the `...`

```python
# src/matching_engine.py

import json                       # WHY: converts JSON string → Python dict
from src.utils import get_llm     # WHY: our shared LLM setup from utils


def analyze_match(resume_text: str, jd_text: str) -> dict:
    """
    Compares resume against job description using Gemini.
    Returns a score, matched skills, and a summary.
    """
    llm = get_llm()   # WHY: create the Gemini connection (uses our shared util)

    # WHY: we write a prompt with very specific instructions
    # The more precise the instructions, the better the output
    # KEY RULE: always tell the AI to return ONLY JSON — no extra explanation
    prompt = f"""
You are an expert resume screener. Compare this resume against this job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

TODO: Write 3-4 lines here telling Gemini:
1. Give a score from 0 to 100 for how well the resume matches the JD
2. List the skills/keywords found in BOTH resume and JD
3. Write a 2-3 sentence summary of the match
4. CRITICAL: respond with ONLY a valid JSON object in this exact format:
{{
    "score": <integer 0-100>,
    "matched_skills": [<list of strings>],
    "summary": "<string>"
}}
No markdown. No explanation. Just the JSON.
    """

    try:
        # WHY: send the prompt to Gemini and wait for the response
        response = llm.invoke(prompt)

        # WHY: .content is where the actual text response lives
        raw_text = response.content

        # WHY: convert the JSON string into a Python dict so we can use .get() etc.
        result = json.loads(raw_text)

        return result

    except json.JSONDecodeError:
        # WHY: LLMs sometimes add ```json ``` around the response — that breaks json.loads()
        # If this error happens, print raw_text and look at what Gemini actually returned
        print("LLM did not return valid JSON. Raw response:")
        print(raw_text)
        return {"score": 0, "matched_skills": [], "summary": "Could not parse response."}

    except Exception as e:
        print(f"Error in analyze_match: {e}")
        return {"score": 0, "matched_skills": [], "summary": "An error occurred."}


# ── Test block ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # WHY: hardcode simple examples to test without running the full app
    sample_resume = "Python developer with 3 years of experience. Built REST APIs and worked with SQL."
    sample_jd = "Looking for a Python developer with REST API experience and SQL skills."

    result = analyze_match(sample_resume, sample_jd)
    print(result)
    # Expected: something like {'score': 85, 'matched_skills': ['Python', 'REST API', 'SQL'], ...}
```

---

---

# 📦 PHASE 4 — gap_analysis.py

## ❓ WHY are we building this?

**The problem**: We know the score. But the user needs to know specifically *what* they're missing. "You scored 60%" tells them nothing actionable. "You're missing Docker and AWS experience" tells them exactly where to focus.

**The solution**: Ask Gemini to look at the JD requirements and flag anything that's NOT in the resume.

**WHY a separate module from matching_engine?** Because it's a *different question*. `matching_engine` asks "what matches?" — `gap_analysis` asks "what's missing?". Keeping them separate makes each one simpler and easier to debug.

---

## ✏️ Skeleton — fill in the `...`

```python
# src/gap_analysis.py

import json
from src.utils import get_llm


def find_gaps(resume_text: str, jd_text: str) -> list:
    """
    Identifies requirements in the JD that are NOT present in the resume.
    Returns a list of gap descriptions.
    """
    llm = get_llm()

    # TODO: Write a prompt that instructs Gemini to:
    # 1. Look at what skills/experience/qualifications the JD requires
    # 2. Check which ones are NOT mentioned in the resume
    # 3. Return ONLY a JSON array (list) of gap descriptions
    # Example output Gemini should give: ["No mention of Docker", "Missing team lead experience"]
    prompt = f"""
TODO: Write your full prompt here.

Resume: {resume_text}
Job Description: {jd_text}
    """

    try:
        response = llm.invoke(prompt)
        raw_text = response.content

        # TODO: parse raw_text as a JSON list using json.loads()
        gaps = ...

        # WHY: make sure the result is actually a list before returning
        if not isinstance(gaps, list):
            return []

        return gaps

    except Exception as e:
        print(f"Error in find_gaps: {e}")
        return []


# ── Test block ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample_resume = "Python developer. Built REST APIs. Used MySQL."
    sample_jd = "Need Python dev with Docker, Kubernetes, REST API, and team lead experience."

    gaps = find_gaps(sample_resume, sample_jd)
    print(gaps)
    # Expected: something like ["No Docker experience", "No Kubernetes", "No team lead experience"]
```

---

---

# 📦 PHASE 5 — suggestion_generator.py

## ❓ WHY are we building this?

**The problem**: We have a list of gaps. But "you're missing Docker" is still not fully helpful. The user needs to know: *what exactly should I add to my resume?*

**The solution**: Take each gap and generate a specific, actionable suggestion tailored to what's already in the resume.

**WHY use the resume as context too?** Because good suggestions are personal. "Add a Docker project to your experience section" is more useful than just "learn Docker". We can only say "add it to your experience section" if we know they have an experience section.

---

## ✏️ Skeleton — fill in the `...`

```python
# src/suggestion_generator.py

import json
from src.utils import get_llm


def generate_suggestions(gaps: list, resume_text: str) -> list:
    """
    Generates specific, actionable suggestions for improving the resume.

    Args:
        gaps: List of skill/experience gaps (output from find_gaps)
        resume_text: The original resume text (for context)

    Returns:
        list of suggestion strings
    """
    # WHY: if there are no gaps, there's nothing to improve — return a congratulations message
    if not gaps:
        return ["Great news! Your resume looks well-aligned with the job description."]

    llm = get_llm()

    # WHY: convert the gaps list into a formatted string for the prompt
    # A list like ["gap1", "gap2"] becomes "- gap1\n- gap2"
    gaps_str = "\n".join(f"- {gap}" for gap in gaps)

    # TODO: Write a prompt that:
    # 1. Shows Gemini the identified gaps
    # 2. Shows Gemini the resume (so it knows what sections already exist)
    # 3. Asks for a SPECIFIC suggestion for how to fix each gap in the resume
    # 4. Bad suggestion: "Learn Docker" (too vague)
    # 5. Good suggestion: "Add a bullet point in your Projects section describing a deployment you did with Docker"
    # 6. Return ONLY a JSON array of suggestion strings
    prompt = f"""
TODO: Write your full prompt here.

Gaps identified:
{gaps_str}

Resume (for context):
{resume_text}
    """

    try:
        response = llm.invoke(prompt)
        raw_text = response.content

        # TODO: parse the JSON list from raw_text
        suggestions = ...

        if not isinstance(suggestions, list):
            return []

        return suggestions

    except Exception as e:
        print(f"Error in generate_suggestions: {e}")
        return []


# ── Test block ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample_gaps = ["No Docker experience mentioned", "Missing team leadership"]
    sample_resume = "Python developer. 3 years experience. Built e-commerce APIs. Led a small team."

    suggestions = generate_suggestions(sample_gaps, sample_resume)
    for s in suggestions:
        print("-", s)
```

---

---

# 📦 PHASE 6 — app.py

## ❓ WHY are we building this last?

**The problem**: Everything you built so far is just Python functions. There's no interface. A normal user can't run `python src/matching_engine.py` — they need a web page with buttons.

**The solution**: Streamlit. It turns Python code into a web app with almost no HTML/CSS needed.

**WHY Streamlit and not Flask/React?** Because we're building a tool, not a product. Streamlit lets you wire up a UI in 50 lines. The point of this project is the AI logic — not the web framework.

---

## 🧠 Mental model for Streamlit

```
Every time the user clicks a button or changes an input,
Streamlit reruns your ENTIRE app.py from top to bottom.

This means:
- Code at the top always runs
- Code inside `if st.button(...)` only runs when clicked
- Use st.session_state to remember things between reruns
```

---

## ✏️ Skeleton — fill in the `...`

```python
# app.py

import streamlit as st

# WHY: import the functions we built — this is where it all comes together
from src.resume_parser import parse_resume
from src.jd_parser import parse_jd
from src.matching_engine import analyze_match
from src.gap_analysis import find_gaps
from src.suggestion_generator import generate_suggestions


# ── Page config (must be the first Streamlit call) ──────────────────────────
# WHY: sets the browser tab title and page layout before anything renders
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🎯",
    layout="wide"
)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🎯 AI-Powered Resume Analyzer")
st.markdown("Upload your resume and paste a job description to see how well they match.")
st.divider()

# ── Inputs ───────────────────────────────────────────────────────────────────
# WHY: columns put two things side by side instead of stacked vertically
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📄 Your Resume")
    # WHY: file_uploader gives the user a drag-and-drop PDF upload widget
    # type=["pdf"] restricts to PDFs only
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

with col2:
    st.subheader("📋 Job Description")
    # TODO: add a st.text_area for the user to paste the job description
    # Give it a label and height=300
    jd_input = st.text_area(...)

st.divider()

# ── Analyze button ────────────────────────────────────────────────────────────
# WHY: use_container_width=True makes the button stretch the full width
analyze_btn = st.button("🔍 Analyze My Resume", use_container_width=True)

# ── Results ───────────────────────────────────────────────────────────────────
# WHY: this entire block only runs when the user clicks the button
if analyze_btn:

    # WHY: validate before sending to AI — don't waste API calls on empty inputs
    if not uploaded_file:
        st.error("⚠️ Please upload a PDF resume first.")
    elif not jd_input.strip():
        st.error("⚠️ Please paste a job description.")
    else:
        # WHY: spinner shows the user something is happening (LLM calls take 3-10 seconds)
        with st.spinner("Analyzing your resume... ⏳"):

            # Step 1: Extract text from inputs
            resume_text = parse_resume(uploaded_file)
            jd_text = parse_jd(jd_input)

            # Step 2: Run AI analysis
            match_result = analyze_match(resume_text, jd_text)
            gaps = find_gaps(resume_text, jd_text)
            suggestions = generate_suggestions(gaps, resume_text)

        # WHY: show success AFTER the spinner ends
        st.success("✅ Analysis complete!")
        st.divider()

        # ── Score + Summary ──────────────────────────────────────────────────
        score = match_result.get("score", 0)
        matched_skills = match_result.get("matched_skills", [])
        summary = match_result.get("summary", "")

        r1, r2 = st.columns([1, 2])
        with r1:
            # WHY: st.metric is a built-in Streamlit widget for displaying key numbers
            st.metric(label="🎯 Match Score", value=f"{score}%")
        with r2:
            st.markdown("**📝 Summary**")
            st.write(summary)

        st.divider()

        # ── Matched Skills ────────────────────────────────────────────────────
        st.subheader("✅ Matched Skills")
        if matched_skills:
            # TODO: display the matched_skills list — join them or loop through them
            ...
        else:
            st.write("No matching skills found.")

        st.divider()

        # ── Gaps ──────────────────────────────────────────────────────────────
        st.subheader("⚠️ Skill Gaps")
        if gaps:
            # TODO: loop through gaps and show each one using st.warning()
            for gap in gaps:
                ...
        else:
            st.success("No major gaps detected!")

        st.divider()

        # ── Suggestions ───────────────────────────────────────────────────────
        st.subheader("💡 How to Improve Your Resume")
        # TODO: loop through suggestions, number them, show each with st.info()
        for i, suggestion in enumerate(suggestions, start=1):
            ...

        # WHY: expander hides verbose content by default — keeps the page clean
        with st.expander("📄 View extracted resume text"):
            st.text(resume_text)
```

---

---

## 🚩 Common Gotchas

| Error you'll see | What it means | Fix |
|---|---|---|
| `ModuleNotFoundError: src` | Python can't find your src folder | Run from project root: `uv run streamlit run app.py` |
| `json.JSONDecodeError` | LLM wrapped response in ```json ``` | Strip it: `raw.strip().strip("```json").strip("```")` before `json.loads()` |
| `extract_text()` returns `None` | PDF is image-based, no text layer | Add `if text:` check before appending |
| `GOOGLE_API_KEY` is None | `.env` wasn't loaded or key is missing | Check `.env` has the key, check `load_dotenv()` is called |

---

## ✅ Definition of Done for Each Phase

Before moving to the next phase, your test block at the bottom must print a correct result.

| Phase | You know it works when... |
|---|---|
| utils.py | `type(llm)` prints and `clean_text()` removes blanks |
| resume_parser.py | Real PDF text appears in terminal |
| jd_parser.py | Cleaned JD text prints correctly |
| matching_engine.py | A dict with `score`, `matched_skills`, `summary` prints |
| gap_analysis.py | A list of gap strings prints |
| suggestion_generator.py | A list of suggestion strings prints |
| app.py | Full end-to-end flow works in browser |

---

*You know more than you think. Read the WHY. Then write the code. One line at a time.*
