# Medical Report Simplifier

A web application designed to help patients understand complex medical jargon. Users can upload medical reports (PDF or images), get an AI-powered layperson-friendly simplified summary, translate it into different languages, and chat interactively with a medical assistant based on their report.

## Features
- **File Upload**: Supports PDF documents and image files (PNG, JPG, JPEG).
- **OCR Integration**: Extracts text from scanned documents using Tesseract OCR.
- **AI Simplifier**: Leverages Google Gemini AI to translate cryptic medical terms into simple, easy-to-understand explanations.
- **Multi-language Support**: Translate the simplified summary into multiple languages.
- **Interactive Chatbot**: Ask questions directly about the report findings.
- **Modern UI**: A premium dark-themed/glassmorphic responsive dashboard.

## File Structure
- `app.py`: Flask entry point.
- `config.py`: Application config.
- `routes/`: Blueprint routes for uploads, reports, and chatbot.
- `services/`: Core logic for text extraction, OCR, Gemini API, and translator.
- `database/`: Database connectivity and schemas.
- `models/`: Access layers for User, Report, and ChatHistory.
- `static/`: Frontend CSS & JS.
- `templates/`: HTML markup templates.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher.
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed on your system (required only for image files).

### Installation
1. Clone or copy the project files to your directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your environment variables:
   - Copy the `.env.example` file to a new file named `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and fill in your details:
     - Insert your OpenAI or OpenRouter API key in `OPENAI_API_KEY`.
     - Customize the `OPENAI_MODEL` if desired (defaults to `google/gemini-2.5-flash`).
   - (Windows OCR only) If Tesseract is not in your system PATH, add the absolute path to your `tesseract.exe` in the `TESSERACT_CMD` environment variable in `.env`. E.g., `TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe`.


5. Initialize the database:
   The database initializes automatically when running `app.py` for the first time.

6. Run the application:
   ```bash
   python app.py
   ```
7. Open `http://127.0.0.1:5000` in your web browser.
