import httpx
from openai import OpenAI
from config import Config
from utils.constants import SUPPORTED_LANGUAGES

# Configure client on load if key is set
client = None
params = Config.get_openai_params()
if params['api_key'] and params['api_key'] != "your_openai_api_key_here":
    try:
        client = OpenAI(
            api_key=params['api_key'],
            base_url=params['base_url'],
            http_client=httpx.Client()
        )
    except Exception as e:
        print(f"Failed to initialize translator OpenAI client at module load: {e}")

def translate_text(text, target_lang_code):
    """
    Translates simplified markdown text into the target language using OpenAI.
    """
    global client
    target_language = SUPPORTED_LANGUAGES.get(target_lang_code, 'English')
    
    if target_lang_code == 'en':
        return text  # Already in English
        
    params = Config.get_openai_params()
    if not params['api_key'] or params['api_key'] == "your_openai_api_key_here":
        return f"[Translation to {target_language} (Mock Mode)]\n\n{text}"
        
    try:
        if client is None:
            client = OpenAI(
                api_key=params['api_key'],
                base_url=params['base_url'],
                http_client=httpx.Client()
            )
            
        prompt = (
            f"You are a medical translator. Translate the following markdown text into "
            f"{target_language}. Keep all markdown formatting (bolding, headers, bullet points, horizontal rules) "
            f"exactly intact as in the source text. Do not add any extra preambles, just output the translation.\n\n"
            f"Text to translate:\n{text}"
        )
        
        response = client.chat.completions.create(
            model=params['model'],
            messages=[
                {"role": "system", "content": "You are a professional translator specializing in medical terms."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during translation: {e}")
        return f"Translation failed: {str(e)}"
