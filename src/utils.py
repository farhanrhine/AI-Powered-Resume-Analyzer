import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_llm():
    """
    Return a configuread Gemini LLm instance.
    All other modules should call this instead of setting up the LLM themselves.
    """

    return ChatGoogleGenerativeAI(
        model = "gemini-2.5-flash",
        temperature = 0.7,
    )


def clean_text(text: str)->str:
    """
    Remove blank & white space.
    """

    if not text:
        return ""


    lines = text.splitlines()
    cleaned_lines = []

    return "\n".join(cleaned_lines)



    if __name__ == "__main__":
        llm = get_llm()
        print(type(llm))
        print(clean_text("hola \n world"))



