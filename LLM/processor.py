import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

MODEL = "gemini-2.0-flash"

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

    raw = response.text.strip()

    # Remove ```json ... ``` fences if present
    raw = re.sub(r"^```json", "", raw)
    raw = re.sub(r"^```", "", raw)
    raw = raw.replace("```", "").strip()

    try:
        return json.loads(raw)
    except Exception:
        return {
            "error": "Failed to parse JSON",
            "raw_response": raw
        }
