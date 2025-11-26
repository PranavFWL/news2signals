import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

MODEL = "gemini-1.5-flash"

def analyze_article(text: str) -> dict:
    """
    Sends article text to Gemini and returns structured signals.
    """
    prompt = f"""
    You are a financial news extraction model.

    Extract the following from the article text:

    - ticker symbols involved (NSE/BSE)
    - company names mentioned
    - event type (earnings, bonus issue, management change, macro event, etc.)
    - market sentiment (positive, negative, neutral)
    - short summary (2–3 sentences)
    - confidence score (0 to 1)

    Return ONLY a valid JSON object with the following format:

    {{
        "tickers": [],
        "companies": [],
        "event_type": "",
        "sentiment": "",
        "summary": "",
        "confidence": 0.0
    }}

    Article text:
    {text[:6000]}  # limit to avoid token overflow
    """

    response = genai.GenerativeModel(MODEL).generate_content(prompt)

    try:
        # extract JSON part
        return json.loads(response.text.strip())
    except Exception:
        return {"error": "Malformed JSON", "raw": response.text}
