# search_examples.py
from es_client import get_es
import json

es = get_es()
INDEX = "news_signals"


def search_by_ticker(ticker: str, size: int = 10):
    """Return documents where `tickers` keyword array contains ticker."""
    q = {
        "query": {
            "term": {"tickers": {"value": ticker}}
        },
        "size": size
    }
    return es.search(index=INDEX, body=q)


def search_fulltext(query: str, size: int = 10):
    """Full text search against title + full_text + summary using match (analyzed)."""
    q = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^2", "summary", "full_text"]
            }
        },
        "size": size
    }
    return es.search(index=INDEX, body=q)


def filter_by_event_and_sentiment(event_type: str = None, sentiment: str = None, size: int = 10):
    """Keyword filters combining event_type and sentiment."""
    must = []
    if event_type:
        must.append({"term": {"event_type": event_type}})
    if sentiment:
        must.append({"term": {"sentiment": sentiment}})

    q = {"query": {"bool": {"must": must}} if must else {"match_all": {}} , "size": size}
    return es.search(index=INDEX, body=q)


if __name__ == "__main__":
    print("Fulltext search for 'bonus issue':")
    res = search_fulltext("bonus issue")
    print(json.dumps(res["hits"]["hits"], indent=2)[:1000])  # printed truncated for readability

    print("\nSearch by ticker NSE (example):")
    res = search_by_ticker("NSE")
    print(json.dumps(res["hits"]["hits"], indent=2))

    print("\nFilter by event_type=bonus issue and sentiment=positive:")
    res = filter_by_event_and_sentiment(event_type="bonus issue", sentiment="positive")
    print(json.dumps(res["hits"]["hits"], indent=2))
