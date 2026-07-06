# suggestion
import json
from utils import get_llm

def generate_suggestions(gaps: list, resume_text: str) -> list:
    if not gaps:
        return ["Great news! Your resume looks well-aligned with the job description."]

    llm = get_llm()

    gaps_str = "\n".join(f"- {g}" for g in gaps)

    prompt = f"""
    You are an expert resume advisor. Based on the following gaps identified between the resume and the job description, generate actionable suggestions on how the candidate can improve their resume or bridge these gaps.
    
    Gaps identified:
    {gaps_str}
    
    Resume (for context):
    {resume_text}

    Respond with ONLY a valid JSON list of strings (e.g. ["Add a section describing your Docker projects...", "Mention any leadership or mentoring roles you had..."]). Do not include markdown, markdown code block backticks (like ```json), or any other text.
    """

    try:
        response = llm.invoke(prompt)
        raw_text = response.content
        if isinstance(raw_text, list):
            parts = []
            for part in raw_text:
                if isinstance(part, dict) and "text" in part:
                    parts.append(part["text"])
                elif isinstance(part, str):
                    parts.append(part)
            raw_text = "".join(parts)
            
        suggestions = json.loads(raw_text)

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

