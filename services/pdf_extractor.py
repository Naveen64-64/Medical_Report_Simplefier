import pdfplumber

def extract_text_from_pdf(file_path):
    """
    Extracts text from a PDF document using pdfplumber.
    Returns the extracted text, or an empty string if no text is found or on error.
    """
    extracted_text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {e}")
    
    return extracted_text.strip()
