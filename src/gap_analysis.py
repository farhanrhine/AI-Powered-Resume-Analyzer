# gap analysis
import json
from utils import get_llm

def find_gaps(resume_text: str, jd_text:str)->list:
    llm = get_llm()

    prompt = f"""
    You are an expert resume screener. Identify the gaps between the candidate's resume and the job description (skills/requirements in the Job Description that are missing or weak in the Resume).
    
    Resume: {resume_text}
    Job Description: {jd_text}

    Respond with ONLY a valid JSON list of strings (e.g. ["Docker", "Kubernetes"]). Do not include markdown, markdown code block backticks (like ```json), or any other text.
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
            
        gaps = json.loads(raw_text)

        if not isinstance(gaps, list):
            return []

        return gaps

    except Exception as e:
        print(f"Error in find_gaps: {e}")
        return []



if __name__ == "__main__":
    sample_resume = "Python developer. Built REST APIs. Used MySQL."
    sample_jd = "Need Python dev with Docker, Kubernetes, REST API, and team lead experience."

    gaps = find_gaps(sample_resume, sample_jd)
    print(gaps)