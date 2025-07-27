import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API keys should be set as environment variables for security
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')

# List of reputable sources to filter
TRUSTED_SOURCES = [
    'reuters', 'associated-press', 'bloomberg', 'bbc-news', 'the-wall-street-journal',
    'npr', 'financial-times', 'cnbc', 'politico', 'ap-news'
]

# Alternative approach: Use keywords instead of specific sources for better coverage
TRUSTED_KEYWORDS = [
    'reuters', 'bloomberg', 'bbc', 'wall street journal', 'npr', 'financial times', 
    'cnbc', 'politico', 'associated press', 'ap news'
]

# Categories and associated keywords for basic categorization
CATEGORIES = {
    'Technology': ['technology', 'tech', 'software', 'hardware', 'AI', 'artificial intelligence', 'gadgets', 'silicon valley', 'startup', 'app', 'digital', 'cyber', 'blockchain', 'crypto', 'bitcoin', 'ethereum', 'nvidia', 'amd', 'intel', 'apple', 'google', 'microsoft', 'meta', 'facebook', 'amazon', 'tesla', 'chatgpt', 'openai', 'algorithm', 'data', 'cloud', 'internet', 'social media', 'smartphone', 'computer', 'laptop', 'robot', 'automation'],
    'Health': ['health', 'medicine', 'covid', 'disease', 'vaccine', 'wellness', 'medical', 'hospital', 'doctor', 'patient', 'treatment', 'drug', 'pharmaceutical', 'fda', 'clinical trial', 'surgery', 'diagnosis', 'cancer', 'virus', 'infection', 'therapy', 'medication', 'healthcare', 'insurance', 'mental health', 'psychology', 'nutrition', 'fitness', 'exercise', 'diet'],
    'Government/Policy': ['government', 'policy', 'congress', 'senate', 'house', 'law', 'bill', 'regulation', 'white house', 'president', 'administration', 'federal', 'state', 'legislation', 'vote', 'election', 'democrat', 'republican', 'politician', 'campaign', 'supreme court', 'justice', 'attorney general', 'department', 'agency', 'budget', 'tax', 'immigration', 'foreign policy', 'diplomacy'],
    'Economy': ['economy', 'economic', 'gdp', 'inflation', 'jobs', 'employment', 'recession', 'growth', 'market', 'consumer', 'spending', 'retail', 'manufacturing', 'trade', 'import', 'export', 'business', 'corporate', 'industry', 'sector', 'productivity', 'wages', 'salary', 'income', 'poverty', 'wealth', 'middle class'],
    'Finance': ['finance', 'stock', 'market', 'earnings', 'analyst', 'M&A', 'sec', 'ipo', 'merger', 'acquisition', 'investment', 'trading', 'portfolio', 'fund', 'bank', 'banking', 'credit', 'loan', 'mortgage', 'interest rate', 'federal reserve', 'fed', 'dow', 'nasdaq', 's&p', 'wall street', 'hedge fund', 'private equity', 'dividend', 'revenue', 'profit', 'loss', 'quarterly', 'annual', 'shareholder', 'board', 'ceo', 'cfo', 'executive'],
    'World': ['world', 'global', 'international', 'foreign', 'diplomacy', 'embassy', 'ambassador', 'united nations', 'nato', 'europe', 'asia', 'africa', 'latin america', 'middle east', 'russia', 'china', 'japan', 'germany', 'france', 'uk', 'canada', 'mexico', 'war', 'conflict', 'peace', 'treaty', 'alliance', 'sanction', 'embargo', 'terrorism', 'refugee', 'migration'],
}

# --- FETCH NEWS FROM NEWSAPI ---
def fetch_newsapi_articles() -> List[Dict]:
    """Fetch articles from NewsAPI"""
    url = 'https://newsapi.org/v2/everything'
    from_date = (datetime.utcnow() - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
    params = {
        'q': 'reuters OR bloomberg OR "wall street journal" OR bbc OR npr OR "financial times" OR cnbc OR politico OR "associated press"',
        'from': from_date,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 100,
        'apiKey': NEWSAPI_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"📅 Date range: {from_date} to now")
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            print(f"✅ Found {len(articles)} articles (total: {data.get('totalResults', 0)})")
            return articles
        else:
            print(f"❌ NewsAPI request failed with status {response.status_code}")
            if response.status_code == 401:
                print("🔑 Check your NewsAPI key - it may be invalid or expired")
            elif response.status_code == 429:
                print("⏰ Rate limit exceeded - try again later")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error fetching from NewsAPI: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error fetching from NewsAPI: {e}")
        return []

# --- CATEGORIZATION ---
def categorize_article(article: Dict) -> str:
    """
    Categorize an article based on its title/content using keyword matching.
    Returns the category name or 'Miscellaneous'.
    """
    text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
    source = article.get('source', {})
    source_name = source.get('name', '').lower() if isinstance(source, dict) else str(source).lower()
    
    # Check each category with more specific keywords
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return category
    
    # Additional source-based categorization
    if any(name in source_name for name in ['bloomberg', 'reuters', 'cnbc', 'financial times', 'wall street']):
        if any(word in text for word in ['stock', 'market', 'earnings', 'trading', 'investment', 'fund']):
            return 'Finance'
        elif any(word in text for word in ['economy', 'gdp', 'inflation', 'jobs', 'employment']):
            return 'Economy'
    
    # Technology sources
    if any(name in source_name for name in ['techcrunch', 'wired', 'ars technica', 'the verge']):
        return 'Technology'
    
    # Health sources
    if any(name in source_name for name in ['medical', 'health', 'fda', 'who']):
        return 'Health'
    
    # Government/Policy sources
    if any(name in source_name for name in ['politico', 'congress', 'white house', 'senate']):
        return 'Government/Policy'
    
    return 'Miscellaneous'

# --- PRIORITY SORTING ---
def sort_articles_by_priority(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sort articles by priority: categorized articles first, miscellaneous at bottom.
    Returns sorted DataFrame.
    """
    if df.empty:
        return df
    
    # Define priority order (higher priority first)
    priority_order = {
        'Finance': 1,      # High priority - market moving news
        'Technology': 2,    # High priority - tech news
        'Government/Policy': 3,  # High priority - policy impact
        'Economy': 4,      # Medium priority
        'Health': 5,       # Medium priority
        'World': 6,        # Medium priority
        'Miscellaneous': 7  # Low priority - at bottom
    }
    
    # Add priority column
    df = df.copy()
    df['priority'] = df['category'].map(priority_order).fillna(7)
    
    # Sort by priority, then by published date (newest first)
    df_sorted = df.sort_values(['priority', 'published_at'], ascending=[True, False])
    
    # Remove priority column (keep it clean)
    df_sorted = df_sorted.drop('priority', axis=1)
    
    return df_sorted

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

    # Convert to DataFrame and sort by priority
    df = pd.DataFrame(all_articles)
    df = sort_articles_by_priority(df)
    return df

if __name__ == "__main__":
    df = collect_all_news()
    print(df.head()) 