# score 
import json
from utils import get_llm


def analyze_match(resume_text: str, jd_text: str) -> dict:
    llm = get_llm()

    prompt = f"""
You are an expert resume screener. Compare this resume against this job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

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
        result = json.loads(raw_text)
        return result

    except json.JSONDecodeError:
        print ("LLm did not return valid JSON. Raw response:")
        print(raw_text)
        return {"score": 0, "matched_skills": [], "summary": "Could not parse response"}

    except Exception as e:
        print(f"Error in analyze_match : {e}")
        return {"score" : 0, "matched_skills" : [], "summary": "An error occured."}



# test block

if __name__ == "__main__":
    sample_resume = "python developer with 3 years of experience. Built REST APIs and worked with SQL."
    sample_jd = "Looking for Python developer with REST API Experience and SQL skills."
    result = analyze_match(sample_resume, sample_jd)
    print(result)

