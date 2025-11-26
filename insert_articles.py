from es_client import get_es
from LLM.processor import analyze_article
import json
from datetime import datetime

es = get_es()

INDEX = "news_signals"

# Load scraped raw articles
with open("data/sample_output.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

print(f"Loaded {len(articles)} articles.")

for i, article in enumerate(articles, start=1):
    url = article["url"]
    full_text = article["text"]

    print(f"[{i}] Processing:", url)

    # Pass through LLM for structured info
    signals = analyze_article(full_text)

    doc = {
        "url": url,
        "full_text": full_text,
        "summary": signals.get("summary", ""),
        "tickers": signals.get("tickers", []),
        "companies": signals.get("companies", []),
        "event_type": signals.get("event_type", ""),
        "sentiment": signals.get("sentiment", ""),
        "timestamp": datetime.utcnow()
    }

    # Insert into Elasticsearch
    res = es.index(index=INDEX, document=doc)
    print("   Inserted ID:", res["_id"])

print("All articles inserted successfully.")
