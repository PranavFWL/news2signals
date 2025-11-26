from LLM.processor import analyze_article
import json

# Load one scraped article to test the LLM
with open("data/sample_output.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# Pick the first article's text
first_article = articles[0]["text"]

# Run it through the Gemini processor
result = analyze_article(first_article)

# Print the structured output
print(json.dumps(result, indent=2))
