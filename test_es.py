from es_client import get_es

es = get_es()

info = es.info()
print("Connected to Elasticsearch:")
print(info)
