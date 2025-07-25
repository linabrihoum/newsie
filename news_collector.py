import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict

NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')

# List of reputable sources to filter
TRUSTED_SOURCES = [
    'reuters', 'associated-press', 'bloomberg', 'bbc-news', 'the-wall-street-journal',
    'npr', 'financial-times', 'cnbc', 'politico', 'ap-news'
]

# Categories and associated keywords for basic categorization
CATEGORIES = {
    'Technology': ['technology', 'tech', 'software', 'hardware', 'AI', 'artificial intelligence', 'gadgets'],
    'Health': ['health', 'medicine', 'covid', 'disease', 'vaccine', 'wellness'],
    'Government/Policy': ['government', 'policy', 'congress', 'senate', 'house', 'law', 'bill', 'regulation'],
    'Economy': ['economy', 'economic', 'gdp', 'inflation', 'jobs', 'employment'],
    'Finance': ['finance', 'stock', 'market', 'earnings', 'analyst', 'M&A', 'sec', 'ipo', 'merger'],
    'World': ['world', 'global', 'international', 'foreign'],
}

# --- FETCH NEWS FROM NEWSAPI ---
def fetch_newsapi_articles() -> List[Dict]:
    """
    Fetch news articles from NewsAPI published in the last 24 hours from trusted sources.
    Returns a list of article dicts.
    """
    if not NEWSAPI_KEY:
        raise ValueError("NEWSAPI_KEY environment variable not set.")

    url = 'https://newsapi.org/v2/everything'
    from_date = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    params = {
        'sources': ','.join(TRUSTED_SOURCES),
        'from': from_date,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 100,  # max per request
        'apiKey': NEWSAPI_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    articles = data.get('articles', [])
    return articles

# --- CATEGORIZATION ---
def categorize_article(article: Dict) -> str:
    """
    Categorize an article based on its title/content using keyword matching.
    Returns the category name or 'Miscellaneous'.
    """
    text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
    for category, keywords in CATEGORIES.items():
        if any(keyword.lower() in text for keyword in keywords):
            return category
    return 'Miscellaneous'

# --- MAIN ORCHESTRATOR ---
def collect_all_news() -> pd.DataFrame:
    """
    Fetch news from all sources, categorize, and return as a DataFrame.
    """
    all_articles = []

    # Fetch from NewsAPI (add more sources as needed)
    try:
        newsapi_articles = fetch_newsapi_articles()
        for art in newsapi_articles:
            article = {
                'headline': art.get('title'),
                'content': art.get('content') or art.get('description'),
                'url': art.get('url'),
                'source': art.get('source', {}).get('name'),
                'published_at': art.get('publishedAt'),
            }
            article['category'] = categorize_article(article)
            all_articles.append(article)
    except Exception as e:
        print(f"Error fetching from NewsAPI: {e}")

    # TODO: Add more sources (GNews, Bing News, etc.)

    # Convert to DataFrame
    df = pd.DataFrame(all_articles)
    return df

if __name__ == "__main__":
    df = collect_all_news()
    print(df.head()) 