# api.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from es_client import get_es
from typing import List, Optional
import uvicorn

app = FastAPI(title="News2Signals API")
es = get_es()
INDEX = "news_signals"


class SearchResponse(BaseModel):
    id: str
    url: str
    summary: Optional[str]
    tickers: List[str] = []
    companies: List[str] = []
    event_type: Optional[str]
    sentiment: Optional[str]


@app.get("/search", response_model=List[SearchResponse])
def search(q: str = Query(..., description="Full text query"),
           size: int = Query(10, ge=1, le=100)):
    """Full-text semantic search (match-based)."""
    body = {
        "query": {
            "multi_match": {
                "query": q,
                "fields": ["title^2", "summary", "full_text"]
            }
        },
        "size": size
    }
    res = es.search(index=INDEX, body=body)
    hits = []
    for h in res["hits"]["hits"]:
        src = h["_source"]
        hits.append({
            "id": h["_id"],
            "url": src.get("url"),
            "summary": src.get("summary"),
            "tickers": src.get("tickers", []),
            "companies": src.get("companies", []),
            "event_type": src.get("event_type"),
            "sentiment": src.get("sentiment")
        })
    return hits


@app.get("/filter", response_model=List[SearchResponse])
def filter_query(ticker: Optional[str] = None,
                 event_type: Optional[str] = None,
                 sentiment: Optional[str] = None,
                 size: int = Query(10, ge=1, le=100)):
    """Keyword filter endpoint (tickers/event_type/sentiment)."""
    must = []
    if ticker:
        must.append({"term": {"tickers": {"value": ticker}}})
    if event_type:
        must.append({"term": {"event_type": {"value": event_type}}})
    if sentiment:
        must.append({"term": {"sentiment": {"value": sentiment}}})

    if must:
        body = {"query": {"bool": {"must": must}}, "size": size}
    else:
        body = {"query": {"match_all": {}}, "size": size}

    res = es.search(index=INDEX, body=body)
    hits = []
    for h in res["hits"]["hits"]:
        src = h["_source"]
        hits.append({
            "id": h["_id"],
            "url": src.get("url"),
            "summary": src.get("summary"),
            "tickers": src.get("tickers", []),
            "companies": src.get("companies", []),
            "event_type": src.get("event_type"),
            "sentiment": src.get("sentiment")
        })
    return hits


@app.post("/scrape_now")
def scrape_now(limit: int = 5):
    """
    Trigger scraping + LLM processing pipeline on demand.
    Uses the existing scraper and LLM modules.
    Note: This is simple sync/blocking version. For production use an async job queue.
    """
    # delay import so API starts quickly even if scraper modules heavy
    from scraper.scraper import run_scrape
    from LLM.processor import analyze_article
    import json
    from datetime import datetime
    from es_client import get_es as get_es_local

    # 1) scrape -> writes data/sample_output.json
    run_scrape(limit=limit)

    # 2) load scraped and process each article and index
    with open("data/sample_output.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

    client = get_es_local()
    inserted = 0
    for article in articles:
        text = article["text"]
        url = article["url"]
        signals = analyze_article(text)
        doc = {
            "url": url,
            "full_text": text,
            "summary": signals.get("summary", ""),
            "tickers": signals.get("tickers", []),
            "companies": signals.get("companies", []),
            "event_type": signals.get("event_type", ""),
            "sentiment": signals.get("sentiment", ""),
            "timestamp": datetime.utcnow()
        }
        client.index(index=INDEX, document=doc)
        inserted += 1

    return {"inserted": inserted}
