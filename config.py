import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-key-for-dev')
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.environ.get('DATABASE_PATH', 'database.db'))
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff'}
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
    TESSERACT_CMD = os.environ.get('TESSERACT_CMD', '')

    @classmethod
    def get_openai_params(cls):
        api_key = cls.OPENAI_API_KEY
        base_url = None
        model = cls.OPENAI_MODEL
        
        # Check if it is an OpenRouter key
        if api_key and api_key.startswith("sk-or-"):
            base_url = "https://openrouter.ai/api/v1"
            if "/" not in model:
                model = f"openai/{model}"
                
        return {
            "api_key": api_key,
            "base_url": base_url,
            "model": model
        }
