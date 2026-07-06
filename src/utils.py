import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_llm():

    """
    call this function whenever need to talk to llm
    """
    api_key = os.getenv("GEMINI_API_KEY")

    return ChatGoogleGenerativeAI(
        model = "gemini-3.5-flash",
        temperature = 0.5,
        google_api_key = api_key 

    )


def clean_text(text : str) -> str:
    """
    remove white space from string
    """
    if not text:
        return ""
    
    cleaned_lines = []

    lines = text.splitlines()

    for line in lines:
        stripped = line.strip()
        if stripped:
            words = stripped.split()
            cleaned_line = " ".join(words)
            cleaned_lines.append(cleaned_line)

    return "\n".join(cleaned_lines)


if __name__ == "__main__":
    llm = get_llm()
    print(type(llm))

    result = clean_text("      helo  \n\n world \n  ")
    print(repr(result))

