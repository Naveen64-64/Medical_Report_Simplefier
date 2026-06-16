import httpx
from openai import OpenAI
from config import Config
from utils.constants import CHATBOT_SYSTEM_PROMPT

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
        print(f"Failed to initialize chatbot OpenAI client at module load: {e}")

def get_chatbot_response(report_context, user_question, chat_history_list):
    """
    Queries OpenAI using the context of the medical report and the chat history.
    """
    global client
    params = Config.get_openai_params()
    if not params['api_key'] or params['api_key'] == "your_openai_api_key_here":
        return (
            f"Thank you for your question: '{user_question}'. I am currently operating in demo mode. "
            "To receive dynamic answers about your specific report, please configure your OpenAI API key."
        )

    try:
        if client is None:
            client = OpenAI(
                api_key=params['api_key'],
                base_url=params['base_url'],
                http_client=httpx.Client()
            )
            
        # Format the system instruction
        system_instruction = CHATBOT_SYSTEM_PROMPT.format(report_context=report_context)
        
        # Build messages structure
        messages = [
            {"role": "system", "content": system_instruction}
        ]
        
        # Add conversation history
        for msg in chat_history_list:
            role = "user" if msg['sender'] == 'user' else "assistant"
            messages.append({"role": role, "content": msg['message']})
            
        # Add current user question
        messages.append({"role": "user", "content": user_question})
        
        response = client.chat.completions.create(
            model=params['model'],
            messages=messages,
            temperature=0.5,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling chatbot service: {e}")
        return f"I'm sorry, I encountered an error while analyzing your question. Details: {str(e)}"
