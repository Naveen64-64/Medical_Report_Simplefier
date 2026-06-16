import httpx
from openai import OpenAI
from config import Config
from utils.constants import SIMPLIFICATION_PROMPT

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
        print(f"Failed to initialize OpenAI client at module load: {e}")

def simplify_report(report_text):
    """
    Calls the OpenAI API to simplify complex medical jargon into easy-to-understand terms.
    If the OPENAI_API_KEY is not configured, returns a mock simplification for demonstration.
    """
    global client
    params = Config.get_openai_params()
    if not params['api_key'] or params['api_key'] == "your_openai_api_key_here":
        return get_mock_simplification(report_text)
        
    try:
        if client is None:
            client = OpenAI(
                api_key=params['api_key'],
                base_url=params['base_url'],
                http_client=httpx.Client()
            )
            
        prompt = SIMPLIFICATION_PROMPT.format(report_text=report_text)
        response = client.chat.completions.create(
            model=params['model'],
            messages=[
                {"role": "system", "content": "You are a helpful, professional medical report translator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        # Return helpful error or fallback representation
        return (
            "### Error in AI Generation\n\n"
            f"Unable to process report using OpenAI API: {str(e)}\n\n"
            "Here is the original text parsed:\n"
            f"```\n{report_text}\n```"
        )

def get_mock_simplification(report_text):
    """Returns a placeholder simplified report structure for demonstration."""
    return f"""## 🩺 Easy-to-Understand Health Report Summary

### Overall Result
Most of your test results are **good and normal** in this demonstration run. 👍 However, the system is running in offline mock mode, so you need to configure your OpenAI API key in the `.env` file for real AI analyses.

---

## ✅ Good News

### 1. Document Extraction: Successful
Your uploaded document was parsed successfully.

**What this means:**
The system successfully extracted {len(report_text)} characters of text from your report and it is ready to be simplified.

### 2. System Status: Healthy
The Flask server, database connection, and translation triggers are working normally.

---

## ⚠️ Things That Need Attention

### 1. API Configuration Required
The OpenAI API key was not detected in your configuration.

**What this means:**
The AI model cannot simplify medical terminology automatically until you configure `OPENAI_API_KEY` in your `.env` file.

---

## 🍎 Health Recommendations

### Drink Plenty of Water
* Drink 2–3 liters of clean water daily.
* Stay hydrated to support general body function.

### Eat Healthy and Light Food
* Eat freshly cooked meals.
* Choose light food items like rice, khichdi, and vegetables.
* Avoid street food, excessively spicy or oily meals.

### Take Proper Rest
* Get 7-8 hours of sleep.
* Avoid heavy physical strain if you feel fatigued.

### Maintain Good Hygiene
* Wash your hands thoroughly before eating.
* Maintain clean kitchen habits.

---

## 🚨 Consult a Doctor Immediately If You Have
* High fever
* Severe weakness
* Stomach pain
* Vomiting
* Yellow eyes or skin

---

## 📋 Final Conclusion
✅ Document Extraction: Normal
⚠️ API Connection: Config Required

### Simple Final Message
**Your report parsing is successful. The main task now is to configure your OpenAI API key in the `.env` file to unlock dynamic AI simplifications. Drink water, eat healthy food, rest, and consult your doctor for any actual health concerns.** 💙
"""
