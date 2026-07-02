# 🚀 AI-Powered Resume Analyzer — Build It Yourself Guide

> **Goal**: Build a Streamlit app that takes a Resume (PDF) + Job Description (text), and returns a match score, skill gaps, and improvement suggestions using Google Gemini via LangChain.

---

## 🗂️ Project Structure (Target)

```
AI-Powered-Resume-Analyzer/
│
├── app.py                  ← Streamlit UI (entry point)
├── pyproject.toml          ← Dependencies (already done)
├── .env                    ← Your API key (already done)
│
└── src/
    ├── __init__.py
    ├── resume_parser.py        ← Phase 1
    ├── jd_parser.py            ← Phase 2
    ├── matching_engine.py      ← Phase 3
    ├── gap_analysis.py         ← Phase 4
    ├── suggestion_generator.py ← Phase 5
    └── utils.py                ← Helpers used across modules
```

---

## ⚙️ Setup (Already Done — Just Verify)

- `uv` is your package manager — use `uv run streamlit run app.py` to start
- `.env` has your `GOOGLE_API_KEY`
- `pyproject.toml` has all dependencies: `pdfplumber`, `langchain`, `langchain-google-genai`, `streamlit`, `python-dotenv`

---

---

# 📦 PHASE 1 — Resume Parser

**File**: `src/resume_parser.py`

**Goal**: Extract raw text from a PDF resume uploaded by the user.

### What to build:
- A function `parse_resume(pdf_file) -> str`
- Accept a file object (from Streamlit's `st.file_uploader`)
- Use `pdfplumber` to open and read all pages
- Loop through every page, extract text, join it all together
- Return the full resume text as a single string
- Handle edge cases: empty pages, unreadable PDFs (try/except)

### Key concepts to learn:
- `pdfplumber.open()` — works with file-like objects
- `page.extract_text()` — returns text or None
- Always strip and clean the extracted text

### How to test it:
- In `app.py`, add a file uploader, call your function, and `st.write()` the output
- Upload a real PDF resume and verify the text looks correct

---

---

# 📦 PHASE 2 — Job Description Parser

**File**: `src/jd_parser.py`

**Goal**: Extract and clean the Job Description text entered by the user.

### What to build:
- A function `parse_jd(jd_text: str) -> str`
- The input is plain text (from a `st.text_area`)
- Strip extra whitespace, remove blank lines, normalize the text
- Return clean JD text

### Key concepts to learn:
- String methods: `.strip()`, `.splitlines()`, `" ".join()`
- Why cleaning text matters before sending it to an LLM (less tokens = better)

### Optional enhancement:
- Detect if the JD is too short (< 50 words) and warn the user

### How to test it:
- Paste a sample job description into `st.text_area` and print the cleaned output

---

---

# 📦 PHASE 3 — Matching Engine (LLM Core)

**File**: `src/matching_engine.py`

**Goal**: Send both the resume text and JD text to Google Gemini and get a match score + analysis.

### What to build:
- A function `analyze_match(resume_text: str, jd_text: str) -> dict`
- Load your API key from `.env` using `python-dotenv`
- Initialize `ChatGoogleGenerativeAI` from `langchain-google-genai`
- Write a prompt that instructs Gemini to:
  - Score the match from 0–100
  - List matching skills/keywords found in both
  - Return structured output (JSON preferred)
- Parse the LLM response into a Python dictionary
- Return the dict with keys like: `score`, `matched_skills`, `summary`

### Key concepts to learn:
- `load_dotenv()` and `os.getenv("GOOGLE_API_KEY")`
- `ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=...)`
- LangChain's `invoke()` method
- Prompt engineering: be explicit about output format (ask for JSON)
- `json.loads()` to parse LLM's text response into a dict

### Prompt design tip:
Ask the model to respond ONLY with valid JSON, no extra text. Example structure to ask for:
```json
{
  "score": 78,
  "matched_skills": ["Python", "REST API", "SQL"],
  "summary": "Your resume strongly aligns with..."
}
```

### How to test it:
- Hardcode a sample resume and JD, call the function, print the result

---

---

# 📦 PHASE 4 — Gap Analysis

**File**: `src/gap_analysis.py`

**Goal**: Identify skills/requirements in the JD that are MISSING from the resume.

### What to build:
- A function `find_gaps(resume_text: str, jd_text: str) -> list`
- Ask Gemini to compare both texts and identify:
  - Skills mentioned in JD but not found in resume
  - Experience/qualifications the candidate is missing
- Return a list of gap items (strings)

### Key concepts to learn:
- You can reuse your LLM setup from Phase 3 (put it in `utils.py` to avoid repeating)
- This is a separate LLM call with a different prompt focus
- Parse the response as a JSON array: `["gap 1", "gap 2", ...]`

### How to test it:
- Use the same sample resume + JD from Phase 3
- Print the list of gaps and verify they make sense

---

---

# 📦 PHASE 5 — Suggestion Generator

**File**: `src/suggestion_generator.py`

**Goal**: Generate actionable, personalized suggestions for the user to improve their resume.

### What to build:
- A function `generate_suggestions(gaps: list, resume_text: str) -> list`
- Pass the gaps list and resume context to Gemini
- Ask it to give concrete, actionable improvement tips
- Example outputs:
  - "Add a project where you used Docker to your experience section"
  - "Include your AWS certifications under a Skills or Certifications section"
- Return a list of suggestion strings

### Key concepts to learn:
- Chaining information: use the output of Phase 4 as input to Phase 5
- Prompt engineering: ask for numbered, specific, actionable suggestions
- Keep suggestions realistic to what the resume already shows

---

---

# 📦 PHASE 6 — Streamlit UI

**File**: `app.py`

**Goal**: Wire everything together into a clean, usable web interface.

### What to build (step by step):

**Step 1 — Layout**
- Set page title and icon using `st.set_page_config()`
- Add a header / intro text
- Use `st.columns()` to split the layout (left: upload, right: JD input)

**Step 2 — Inputs**
- File uploader for PDF resume: `st.file_uploader()`
- Text area for Job Description: `st.text_area()`
- "Analyze" button: `st.button()`

**Step 3 — Processing**
- When the button is clicked:
  1. Call `parse_resume()` → get resume text
  2. Call `parse_jd()` → get clean JD text
  3. Call `analyze_match()` → get score + matched skills
  4. Call `find_gaps()` → get gap list
  5. Call `generate_suggestions()` → get suggestions

**Step 4 — Output / Results Display**
- Show the match score as a big metric: `st.metric()`
- Show matched skills as `st.success()` chips or a list
- Show gaps with `st.warning()` or a colored list
- Show suggestions with `st.info()` or numbered list
- Use `st.spinner("Analyzing...")` while the LLM is working
- Use `st.expander()` to show/hide the raw extracted resume text

**Step 5 — Error handling**
- Show friendly messages if no file is uploaded, if the LLM fails, etc.

### Key concepts to learn:
- `st.session_state` — preserve results between reruns
- `st.spinner()` — show loading state
- `st.columns()` — side-by-side layouts
- `st.expander()` — collapsible sections

---

---

# 📦 PHASE 7 — Polish & Utils

**File**: `src/utils.py`

**Goal**: Centralize shared code to avoid duplication.

### What to put here:
- LLM initialization function: `get_llm() -> ChatGoogleGenerativeAI`
  - Loads `.env`, reads API key, returns a configured LLM instance
  - All other modules import and call this instead of repeating setup
- `clean_text(text: str) -> str` — shared text cleaning logic
- Any constants: model name, temperature, etc.

---

---

## 🧪 Testing Strategy

| Phase | How to test |
|-------|------------|
| 1 | Upload a PDF, verify text is extracted correctly |
| 2 | Paste JD text, verify cleaning works |
| 3 | Hardcode inputs, verify JSON output from LLM |
| 4 | Verify gaps make sense for a sample resume vs. JD |
| 5 | Verify suggestions are specific and actionable |
| 6 | End-to-end test with a real resume + real JD |

---

## ⚡ Recommended Build Order

```
Phase 1 → Phase 2 → utils.py → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Polish
```

Start simple. Get each module working with print() statements before wiring into Streamlit.

---

## 🧠 Key Libraries Quick Reference

| Library | What it does |
|---------|-------------|
| `pdfplumber` | Extract text from PDFs |
| `python-dotenv` | Load API keys from `.env` |
| `langchain-google-genai` | Connect to Gemini LLM |
| `streamlit` | Build the web UI |
| `json` | Parse LLM's JSON responses |
| `os` | Read environment variables |

---

## 🚩 Common Pitfalls to Avoid

1. **Don't call the LLM in a loop** — 1 well-crafted prompt is better than 5 small ones
2. **Always handle LLM response parsing with try/except** — it won't always return perfect JSON
3. **Don't hardcode your API key** — always use `.env` + `load_dotenv()`
4. **Test each module independently** before connecting them all in `app.py`
5. **PDF text extraction can fail** on scanned/image-based PDFs — always check for None

---

*Good luck! You've got this. Build phase by phase, test as you go.*
