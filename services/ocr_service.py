# Compatibility patch for Python 3.14+ where pkgutil.find_loader was removed
import pkgutil
if not hasattr(pkgutil, 'find_loader'):
    import importlib.util
    def find_loader(name, path=None):
        try:
            spec = importlib.util.find_spec(name, path)
            return spec.loader if spec else None
        except Exception:
            return None
    pkgutil.find_loader = find_loader

import base64
import os
import httpx
from openai import OpenAI
import pytesseract
from PIL import Image
from config import Config

# Configure tesseract path if provided in config
if Config.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD

def extract_text_from_image(image_path):
    """
    Performs OCR on an image file to extract textual information.
    Falls back to OpenAI vision capabilities if Tesseract is not installed or configured,
    or if Tesseract returns insufficient text (which can indicate a rotated/upside-down image).
    """
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image).strip()
        if len(text) < 30:
            print(f"Tesseract returned insufficient text ({len(text)} chars). Falling back to OpenAI Vision...")
            return extract_text_from_image_via_openai(image_path)
        return text
    except Exception as e:
        # Check if the error is due to missing Tesseract, and print warning
        is_tesseract_error = isinstance(e, pytesseract.TesseractNotFoundError) or "tesseract" in str(e).lower()
        if is_tesseract_error:
            print("Tesseract OCR not found. Attempting fallback to OpenAI Vision API...")
            try:
                return extract_text_from_image_via_openai(image_path)
            except Exception as fallback_err:
                print(f"OpenAI Vision fallback failed: {fallback_err}")
                error_msg = (
                    "Tesseract OCR engine was not found, and OpenAI Vision fallback failed. "
                    "Please ensure Tesseract is installed or a valid OpenAI/OpenRouter API key is configured. "
                    f"Details: {str(fallback_err)}"
                )
                raise RuntimeError(error_msg)
        else:
            print(f"Error performing OCR on {image_path}: {e}. Attempting fallback to OpenAI Vision...")
            try:
                return extract_text_from_image_via_openai(image_path)
            except Exception as fallback_err:
                print(f"OpenAI Vision fallback failed after OCR exception: {fallback_err}")
                raise e

def extract_text_from_image_via_openai(image_path):
    """
    Uses OpenAI Vision capabilities (GPT-4o-mini) to extract text from a medical report image.
    """
    params = Config.get_openai_params()
    if not params['api_key'] or params['api_key'] == "your_openai_api_key_here":
        raise RuntimeError("OpenAI API key is not configured.")

    # Determine file mime type
    file_ext = image_path.rsplit('.', 1)[1].lower() if '.' in image_path else 'jpeg'
    mime_type = f"image/{file_ext}"
    if file_ext == 'jpg':
        mime_type = "image/jpeg"

    # Encode image to base64
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    # Initialize client with dynamic params (supporting OpenRouter base_url overrides)
    client = OpenAI(
        api_key=params['api_key'],
        base_url=params['base_url'],
        http_client=httpx.Client()
    )

    prompt = (
        "Please transcribe all readable text, values, and tables from this image. "
        "This is an automated text transcription task. Output the exact text and numbers found in the image. "
        "Do not summarize, do not simplify, and do not analyze the data. "
        "Keep the layout, lines, and columns as close to the original as possible. "
        "Note: If the image is rotated, sideways, or upside down, please read and transcribe it as if it were oriented correctly."
    )

    response = client.chat.completions.create(
        model=params['model'],
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        temperature=0.0,
        max_tokens=2000
    )
    
    extracted_text = response.choices[0].message.content.strip()
    if not extracted_text:
        raise RuntimeError("OpenAI vision model returned empty text.")
        
    return extracted_text
