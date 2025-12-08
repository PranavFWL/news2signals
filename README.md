# news2signals

**news2signals** is a lightweight pipeline that collects news articles, indexes them, and exposes a simple search/query interface.  
It’s designed for anyone who wants to analyze news, build trading signals, run NLP experiments, or just maintain a clean searchable news archive.

This project started as a personal learning experiment around scraping, indexing, APIs, and search engines — but it evolved into a reusable mini-framework.

---

## 🚀 Features

- **Scrape news articles** from different sources  
- **Create searchable indexes** using a backend like ElasticSearch  
- **Insert & update articles** programmatically  
- **Expose an API** for querying news data  
- **Example scripts** to test search capabilities  
- **Docker support** for smooth setup and deployment  
- **LLM placeholder** folder for future enhancements  
- **Basic tests** to validate scraping and indexing

---

## 📂 Repository Structure

news2signals/
│
├── scraper/ # Scripts/modules for scraping news
├── data/ # Storage folder for downloaded articles (optional)
├── LLM/ # Space for LLM/semantic search experiments
│
├── api.py # API to query the indexed news
├── create_index.py # Creates or resets ElasticSearch index
├── es_client.py # Wrapper client for ES operations
├── insert_articles.py # Load scraped articles into index
├── search_es.py # Example search via ES
├── search_examples.py # Sample search queries
│
├── test_es.py # Tests for ElasticSearch functionality
├── test_selenium.py # Tests for scraping components
├── test_llm.py # Placeholder tests for LLM features
│
├── requirements.txt # Python dependencies
└── Dockerfile # Docker image setup


---

## ⚙️ Installation

### 1. Clone the repo

git clone https://github.com/PranavFWL/news2signals.git
cd news2signals

### 2. Install dependencies
pip install -r requirements.txt

### 3. Set up ElasticSearch
docker run -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.6.0

### 4. Create the index
python create_index.py
