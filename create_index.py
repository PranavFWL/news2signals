from es_client import get_es

es = get_es()

index_name = "news_signals"

mapping = {
    "mappings": {
        "properties": {
            "url": {"type": "keyword"},
            "title": {"type": "text"},
            "full_text": {"type": "text"},
            "summary": {"type": "text"},
            "tickers": {"type": "keyword"},
            "companies": {"type": "keyword"},
            "event_type": {"type": "keyword"},
            "sentiment": {"type": "keyword"},
            "timestamp": {"type": "date"}
        }
    }
}

if es.indices.exists(index=index_name):
    print("Index already exists.")
else:
    es.indices.create(index=index_name, body=mapping)
    print("Index created:", index_name)
