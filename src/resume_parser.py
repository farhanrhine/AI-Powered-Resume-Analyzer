# extract text from resume and clean
import pdfplumber
from utils import clean_text


def parser_resume(pdf_file) -> str:
    """
    Extract all text from pdf and return a clean string

    Args : a pdf file

    return : a full resume text, cleaned.
    """

    all_text = []
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()

                if text:
                    all_text.append(text)
    
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

    full_text = "\n".join(all_text)
    return clean_text(full_text)



if __name__ == "__main__":
    with open("docs/FARHAN.pdf", "rb") as f:
        result = parser_resume(f)
        print(result)