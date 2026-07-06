# extract text from jd and clean

from utils import clean_text

def parse_jd(jd_text:str) -> str:
    """
    cleans & normalizes job description text.

    Args:
        jd_text : Raw string from a text area input

    Return:
        str: Clean job description text.
    """


    if not jd_text or not jd_text.strip():
        return ""

    cleaned = clean_text(jd_text)

    word_count = len(cleaned.split())
    if word_count < 30:
        print(f"Warning : Jd is only {word_count} words. Its might be the too short for analysis.")

    return cleaned


if __name__ == "__main__":
    sample = "  \n\nAI Enginner \n\n Must know Python    and SQL.   \n"
    print(repr(parse_jd(sample)))


