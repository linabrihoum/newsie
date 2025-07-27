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

# --- TRUSTED SOURCES AND CATEGORIES ---
TRUSTED_KEYWORDS = [
    'reuters', 'bloomberg', 'bbc', 'wall street journal', 'npr', 'financial times', 
    'cnbc', 'politico', 'associated press', 'ap news'
]

# Enhanced keyword categories (content-based only)
CATEGORIES = {
    'Technology': [
        # Tech companies
        'microsoft', 'apple', 'google', 'amazon', 'meta', 'facebook', 'tesla', 'nvidia', 'amd', 'intel',
        'netflix', 'spotify', 'uber', 'lyft', 'airbnb', 'zoom', 'slack', 'salesforce', 'adobe',
        # Tech concepts
        'technology', 'tech', 'software', 'hardware', 'AI', 'artificial intelligence', 'machine learning',
        'blockchain', 'crypto', 'bitcoin', 'ethereum', 'algorithm', 'data', 'cloud', 'internet',
        'social media', 'smartphone', 'computer', 'laptop', 'robot', 'automation', 'startup',
        'venture capital', 'unicorn', 'coding', 'programming', 'developer', 'cybersecurity',
        'digital transformation', 'fintech', 'edtech', 'healthtech', 'biotech'
    ],
    'Health': [
        # Health concepts
        'health', 'medicine', 'medical', 'hospital', 'doctor', 'patient', 'treatment', 'drug',
        'pharmaceutical', 'fda', 'clinical trial', 'surgery', 'diagnosis', 'cancer', 'virus',
        'infection', 'therapy', 'medication', 'healthcare', 'insurance', 'mental health',
        'psychology', 'nutrition', 'fitness', 'exercise', 'diet', 'wellness',
        # Health companies
        'pfizer', 'moderna', 'johnson & johnson', 'j&j', 'astrazeneca', 'novartis', 'roche',
        'merck', 'gilead', 'biogen', 'amgen', 'regeneron', 'cdc', 'who', 'genetics'
    ],
    'Government/Policy': [
        # Government entities
        'government', 'white house', 'congress', 'senate', 'house', 'president', 'administration',
        'federal', 'state', 'supreme court', 'justice', 'attorney general', 'department', 'agency',
        'fbi', 'cia', 'nsa', 'department of defense', 'dod', 'department of state', 'dos',
        # Policy concepts
        'policy', 'law', 'bill', 'regulation', 'legislation', 'vote', 'election', 'campaign',
        'democrat', 'republican', 'politician', 'budget', 'tax', 'immigration', 'foreign policy',
        'diplomacy', 'executive order', 'veto', 'impeachment', 'confirmation', 'nomination'
    ],
    'Economy': [
        # Economic concepts
        'economy', 'economic', 'gdp', 'inflation', 'jobs', 'employment', 'recession', 'growth',
        'market', 'consumer', 'spending', 'retail', 'manufacturing', 'trade', 'import', 'export',
        'business', 'corporate', 'industry', 'sector', 'productivity', 'wages', 'salary', 'income',
        'poverty', 'wealth', 'middle class', 'economic growth', 'economic recovery', 'economic stimulus'
    ],
    'Finance': [
        # Financial concepts
        'finance', 'stock', 'market', 'earnings', 'analyst', 'M&A', 'sec', 'ipo', 'merger',
        'acquisition', 'investment', 'trading', 'portfolio', 'fund', 'bank', 'banking', 'credit',
        'loan', 'mortgage', 'interest rate', 'federal reserve', 'fed', 'dow', 'nasdaq', 's&p',
        'wall street', 'hedge fund', 'private equity', 'dividend', 'revenue', 'profit', 'loss',
        'quarterly', 'annual', 'shareholder', 'board', 'ceo', 'cfo', 'executive',
        # Financial companies
        'jpmorgan', 'bank of america', 'wells fargo', 'citigroup', 'goldman sachs', 'morgan stanley',
        'blackrock', 'vanguard', 'fidelity', 'charles schwab'
    ],
    'World': [
        # Countries and regions
        'world', 'global', 'international', 'foreign', 'diplomacy', 'embassy', 'ambassador',
        'united nations', 'nato', 'europe', 'asia', 'africa', 'latin america', 'middle east',
        'russia', 'china', 'japan', 'germany', 'france', 'uk', 'canada', 'mexico', 'thailand',
        'cambodia', 'iran', 'iranian', 'israel', 'palestine', 'ukraine', 'india', 'brazil',
        'australia', 'south korea', 'north korea', 'turkey', 'saudi arabia', 'egypt', 'nigeria',
        'south africa', 'kenya', 'ethiopia', 'morocco', 'algeria', 'tunisia', 'libya', 'sudan',
        # International events
        'war', 'conflict', 'peace', 'treaty', 'alliance', 'sanction', 'embargo', 'terrorism',
        'refugee', 'migration', 'border', 'immigration', 'diplomatic', 'foreign minister',
        'president', 'prime minister', 'king', 'queen', 'royal', 'monarchy', 'republic',
        'democracy', 'election', 'vote', 'protest', 'demonstration', 'riot', 'civil war',
        'coup', 'revolution', 'independence', 'sovereignty', 'territory', 'border dispute',
        'trade war', 'economic sanctions', 'humanitarian', 'aid', 'disaster', 'earthquake',
        'tsunami', 'hurricane', 'flood', 'drought', 'famine', 'pandemic', 'epidemic', 'outbreak'
    ],
    'Space': [
        # Space agencies and companies
        'space', 'nasa', 'spacex', 'blue origin', 'virgin galactic', 'boeing', 'lockheed martin',
        'northrop grumman', 'astronaut', 'satellite', 'rocket', 'spacecraft', 'space station',
        'iss', 'international space station',
        # Space objects and concepts
        'mars', 'moon', 'planet', 'galaxy', 'universe', 'orbit', 'launch', 'telescope', 'hubble',
        'james webb', 'rover', 'probe', 'mission', 'space exploration', 'cosmos', 'stellar',
        'interstellar', 'solar system', 'asteroid', 'meteor', 'comet', 'black hole', 'nebula',
        'star', 'constellation', 'astronomy', 'astrophysics', 'cosmology', 'gravity', 'zero gravity',
        'microgravity', 'space suit', 'spacewalk', 'space tourism', 'space mining', 'mars colony',
        'lunar base', 'space debris', 'space junk', 'space traffic', 'space law'
    ],
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

def remove_duplicates(articles: List[Dict]) -> List[Dict]:
    """
    Remove duplicate articles based on headline similarity and content overlap.
    Returns a list with duplicates removed.
    """
    if not articles:
        return articles
    
    # Create a list to store unique articles
    unique_articles = []
    seen_headlines = set()
    seen_urls = set()
    
    for article in articles:
        headline = article.get('headline', '').lower().strip()
        url = article.get('url', '').strip()
        
        # Skip if we've seen this exact headline or URL
        if headline in seen_headlines or url in seen_urls:
            continue
        
        # Check for similar headlines (fuzzy matching)
        is_duplicate = False
        for existing_article in unique_articles:
            existing_headline = existing_article.get('headline', '').lower().strip()
            
            # Calculate similarity
            if headline and existing_headline:
                # Simple similarity check (can be improved with more sophisticated algorithms)
                words1 = set(headline.split())
                words2 = set(existing_headline.split())
                
                # If more than 70% of words match, consider it a duplicate
                if len(words1.intersection(words2)) / max(len(words1), len(words2)) > 0.7:
                    is_duplicate = True
                    break
        
        if not is_duplicate:
            unique_articles.append(article)
            seen_headlines.add(headline)
            if url:
                seen_urls.add(url)
    
    print(f"🔄 Removed {len(articles) - len(unique_articles)} duplicate articles")
    return unique_articles

def categorize_articles_batch(articles: List[Dict]) -> List[str]:
    """
    Categorize multiple articles in a single batch to reduce API calls.
    """
    if not articles:
        return []
    
    # Define our categories for the AI
    categories = [
        'Technology', 'Health', 'Government/Policy', 'Economy', 'Finance', 'World', 'Space'
    ]
    
    # Prepare batch prompt
    articles_text = ""
    for i, article in enumerate(articles, 1):
        headline = article.get('headline', '')
        description = article.get('description', '')
        content = article.get('content', '')
        full_text = f"{headline} {description} {content}".strip()
        
        if full_text:
            articles_text += f"\n{i}. {full_text[:300]}\n"  # Limit each article to 300 chars
    
    # Create batch prompt for AI categorization
    prompt = f"""
    Categorize each of these news articles into exactly one of these categories:
    - Technology: Tech companies, software, AI, digital innovation, startups
    - Health: Medical, healthcare, pharmaceuticals, wellness, hospitals
    - Government/Policy: Politics, laws, regulations, government agencies, elections
    - Economy: Economic indicators, jobs, GDP, inflation, business trends
    - Finance: Stock markets, banking, investments, financial markets, trading
    - World: International news, foreign countries, global events, diplomacy
    - Space: NASA, space exploration, astronauts, satellites, space agencies

    Articles:
    {articles_text}

    Respond with only the category names in order, one per line (e.g., "Technology", "Finance", "World").
    """
    
    try:
        # Use Gemini API for batch categorization
        import requests
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent'
        
        if not GEMINI_API_KEY:
            print("⚠️ GEMINI_API_KEY not found, using fallback categorization")
            return [categorize_article_fallback(article) for article in articles]
        
        response = requests.post(
            GEMINI_API_URL,
            headers={'Content-Type': 'application/json'},
            params={'key': GEMINI_API_KEY},
            json={
                'contents': [{
                    'parts': [{'text': prompt}]
                }]
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and data['candidates']:
                ai_response = data['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Parse the response to extract categories
                lines = ai_response.split('\n')
                categories_result = []
                
                for line in lines:
                    line = line.strip().replace('"', '').replace("'", "")
                    if line:
                        # Check if the line contains a valid category
                        for category in categories:
                            if category.lower() in line.lower():
                                categories_result.append(category)
                                break
                        else:
                            # If no exact match, try to infer
                            if 'tech' in line.lower() or 'software' in line.lower():
                                categories_result.append('Technology')
                            elif 'health' in line.lower() or 'medical' in line.lower():
                                categories_result.append('Health')
                            elif 'government' in line.lower() or 'policy' in line.lower() or 'politics' in line.lower():
                                categories_result.append('Government/Policy')
                            elif 'economy' in line.lower() or 'economic' in line.lower():
                                categories_result.append('Economy')
                            elif 'finance' in line.lower() or 'stock' in line.lower() or 'market' in line.lower():
                                categories_result.append('Finance')
                            elif 'world' in line.lower() or 'international' in line.lower():
                                categories_result.append('World')
                            elif 'space' in line.lower() or 'nasa' in line.lower():
                                categories_result.append('Space')
                            else:
                                categories_result.append('Miscellaneous')
                
                # Ensure we have the right number of categories
                while len(categories_result) < len(articles):
                    categories_result.append('Miscellaneous')
                
                return categories_result[:len(articles)]
        
        # Fallback to individual categorization
        print("⚠️ Batch categorization failed, using individual fallback")
        return [categorize_article_fallback(article) for article in articles]
        
    except Exception as e:
        print(f"⚠️ AI batch categorization failed: {e}, using fallback")
        return [categorize_article_fallback(article) for article in articles]

def categorize_article_with_ai(article: Dict) -> str:
    """
    Individual AI categorization (fallback for single articles).
    """
    headline = article.get('headline', '')
    description = article.get('description', '')
    content = article.get('content', '')
    
    # Combine all text for analysis
    full_text = f"{headline} {description} {content}".strip()
    
    if not full_text:
        return 'Miscellaneous'
    
    # Define our categories for the AI
    categories = [
        'Technology', 'Health', 'Government/Policy', 'Economy', 'Finance', 'World', 'Space'
    ]
    
    # Create prompt for AI categorization
    prompt = f"""
    Categorize this news article into exactly one of these categories:
    - Technology: Tech companies, software, AI, digital innovation, startups
    - Health: Medical, healthcare, pharmaceuticals, wellness, hospitals
    - Government/Policy: Politics, laws, regulations, government agencies, elections
    - Economy: Economic indicators, jobs, GDP, inflation, business trends
    - Finance: Stock markets, banking, investments, financial markets, trading
    - World: International news, foreign countries, global events, diplomacy
    - Space: NASA, space exploration, astronauts, satellites, space agencies

    Article: {full_text[:500]}  # Limit to first 500 chars for efficiency

    Respond with only the category name (e.g., "Technology" or "Finance").
    """
    
    try:
        # Use Gemini API for categorization
        import requests
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent'
        
        if not GEMINI_API_KEY:
            print("⚠️ GEMINI_API_KEY not found, using fallback categorization")
            return categorize_article_fallback(article)
        
        response = requests.post(
            GEMINI_API_URL,
            headers={'Content-Type': 'application/json'},
            params={'key': GEMINI_API_KEY},
            json={
                'contents': [{
                    'parts': [{'text': prompt}]
                }]
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and data['candidates']:
                ai_response = data['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Clean up the response and find the category
                ai_response = ai_response.replace('"', '').replace("'", "").strip()
                
                # Check if the AI response matches one of our categories
                for category in categories:
                    if category.lower() in ai_response.lower():
                        return category
                
                # If no exact match, try to infer from the response
                if 'tech' in ai_response.lower() or 'software' in ai_response.lower():
                    return 'Technology'
                elif 'health' in ai_response.lower() or 'medical' in ai_response.lower():
                    return 'Health'
                elif 'government' in ai_response.lower() or 'policy' in ai_response.lower() or 'politics' in ai_response.lower():
                    return 'Government/Policy'
                elif 'economy' in ai_response.lower() or 'economic' in ai_response.lower():
                    return 'Economy'
                elif 'finance' in ai_response.lower() or 'stock' in ai_response.lower() or 'market' in ai_response.lower():
                    return 'Finance'
                elif 'world' in ai_response.lower() or 'international' in ai_response.lower():
                    return 'World'
                elif 'space' in ai_response.lower() or 'nasa' in ai_response.lower():
                    return 'Space'
        
        # Fallback to keyword-based categorization
        return categorize_article_fallback(article)
        
    except Exception as e:
        print(f"⚠️ AI categorization failed: {e}, using fallback")
        return categorize_article_fallback(article)

def categorize_article_fallback(article: Dict) -> str:
    """
    Fallback categorization using keyword matching when AI fails.
    """
    text = (article.get('headline', '') + ' ' + article.get('description', '')).lower()
    
    # Enhanced keyword-based categorization
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return category
    
    # Content analysis for specific patterns
    # Government/Policy patterns
    if any(pattern in text for pattern in ['white house', 'congress', 'senate', 'house of representatives', 'president', 'administration', 'federal government', 'executive order', 'supreme court']):
        return 'Government/Policy'
    
    # Technology patterns
    if any(pattern in text for pattern in ['microsoft', 'apple', 'google', 'amazon', 'tesla', 'nvidia', 'artificial intelligence', 'AI', 'software', 'tech company']):
        return 'Technology'
    
    # World patterns (specific countries and international events)
    if any(pattern in text for pattern in ['thailand', 'cambodia', 'iran', 'iranian', 'prince', 'defector', 'refugee', 'migration', 'border', 'diplomatic', 'foreign minister', 'embassy', 'ambassador']):
        return 'World'
    
    # Space patterns
    if any(pattern in text for pattern in ['nasa', 'spacex', 'astronaut', 'satellite', 'rocket', 'spacecraft', 'mars', 'moon', 'planet', 'galaxy', 'universe', 'orbit', 'launch', 'space station', 'iss']):
        return 'Space'
    
    # Finance patterns (market-specific terms)
    if any(pattern in text for pattern in ['stock market', 'earnings', 'trading', 'wall street', 'federal reserve', 'interest rate', 'dow jones', 'nasdaq', 's&p 500']):
        return 'Finance'
    
    # Health patterns (medical terms)
    if any(pattern in text for pattern in ['medical', 'hospital', 'doctor', 'patient', 'treatment', 'drug', 'pharmaceutical', 'fda', 'clinical trial', 'surgery', 'diagnosis', 'cancer', 'virus', 'infection', 'therapy', 'medication', 'cdc', 'who', 'genetics']):
        return 'Health'
    
    # Economy patterns (economic indicators)
    if any(pattern in text for pattern in ['gdp', 'inflation', 'jobs', 'employment', 'recession', 'economic growth', 'economic recovery', 'economic stimulus', 'consumer spending', 'retail sales', 'manufacturing']):
        return 'Economy'
    
    return 'Miscellaneous'

def categorize_article(article: Dict) -> str:
    """
    Main categorization function that uses AI first, then falls back to keywords.
    """
    return categorize_article_with_ai(article)

def calculate_article_priority(article: Dict) -> float:
    """
    Calculate priority score for an article based on multiple factors.
    Higher score = higher priority.
    """
    score = 0.0
    headline = article.get('headline', '').lower()
    description = article.get('description', '').lower()
    source = article.get('source', '').lower()
    
    # Source credibility (trusted sources get higher priority)
    trusted_sources = [
        'reuters', 'associated press', 'ap', 'bloomberg', 'bbc', 'wall street journal', 
        'wsj', 'financial times', 'ft', 'the guardian', 'pbs newshour', 'politico',
        'al jazeera', 'the hill', 'axios'
    ]
    
    for trusted_source in trusted_sources:
        if trusted_source in source:
            score += 10.0
            break
    
    # Breaking news indicators
    breaking_keywords = [
        'breaking', 'urgent', 'just in', 'developing', 'live', 'update', 'alert',
        'crisis', 'emergency', 'deadline', 'deadline', 'immediate', 'critical'
    ]
    
    for keyword in breaking_keywords:
        if keyword in headline or keyword in description:
            score += 8.0
            break
    
    # High-impact topics (politics, economy, major companies)
    high_impact_keywords = [
        'president', 'congress', 'senate', 'house', 'white house', 'administration',
        'federal reserve', 'fed', 'sec', 'fda', 'supreme court', 'election',
        'apple', 'microsoft', 'google', 'amazon', 'tesla', 'nvidia', 'meta',
        'jpmorgan', 'goldman sachs', 'bank of america', 'wells fargo',
        'pfizer', 'moderna', 'johnson & johnson', 'astrazeneca'
    ]
    
    for keyword in high_impact_keywords:
        if keyword in headline or keyword in description:
            score += 6.0
    
    # Market-moving events
    market_keywords = [
        'earnings', 'quarterly results', 'stock market', 'dow jones', 'nasdaq', 's&p',
        'merger', 'acquisition', 'ipo', 'bankruptcy', 'layoffs', 'hiring',
        'interest rate', 'inflation', 'gdp', 'jobs report', 'unemployment'
    ]
    
    for keyword in market_keywords:
        if keyword in headline or keyword in description:
            score += 5.0
    
    # Technology and innovation
    tech_keywords = [
        'artificial intelligence', 'ai', 'machine learning', 'blockchain', 'crypto',
        'cybersecurity', 'data breach', 'hack', 'software', 'startup', 'unicorn',
        'spacex', 'nasa', 'satellite', 'rocket', 'space exploration'
    ]
    
    for keyword in tech_keywords:
        if keyword in headline or keyword in description:
            score += 4.0
    
    # Health and safety
    health_keywords = [
        'covid', 'pandemic', 'vaccine', 'fda approval', 'clinical trial',
        'cancer', 'treatment', 'hospital', 'medical', 'healthcare', 'insurance',
        'genetics', 'medicine', 'cdc', 'who'
    ]
    
    for keyword in health_keywords:
        if keyword in headline or keyword in description:
            score += 4.0
    
    # International significance
    world_keywords = [
        'russia', 'ukraine', 'china', 'iran', 'north korea', 'israel', 'palestine',
        'nato', 'united nations', 'trade war', 'sanctions', 'embargo',
        'refugee', 'migration', 'border', 'diplomatic', 'embassy'
    ]
    
    for keyword in world_keywords:
        if keyword in headline or keyword in description:
            score += 3.0
    
    # Recency bonus (newer articles get slight priority)
    published_at = article.get('published_at', '')
    if published_at:
        try:
            from datetime import datetime, timezone
            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            hours_old = (now - pub_date).total_seconds() / 3600
            
            if hours_old < 6:  # Very recent
                score += 2.0
            elif hours_old < 12:  # Recent
                score += 1.0
        except:
            pass
    
    # Content length bonus (more detailed articles)
    content_length = len(article.get('content', ''))
    if content_length > 500:
        score += 1.0
    elif content_length > 200:
        score += 0.5
    
    return score

def select_high_priority_articles(articles: List[Dict], max_count: int = 20) -> List[Dict]:
    """
    Select the highest priority articles for processing.
    """
    if not articles:
        return []
    
    # Calculate priority scores for all articles
    scored_articles = []
    for article in articles:
        priority_score = calculate_article_priority(article)
        scored_articles.append((article, priority_score))
    
    # Sort by priority score (highest first)
    scored_articles.sort(key=lambda x: x[1], reverse=True)
    
    # Select top articles
    selected_articles = [article for article, score in scored_articles[:max_count]]
    
    # Print priority analysis
    print(f"📊 Priority Analysis:")
    print(f"   Total articles: {len(articles)}")
    print(f"   Selected top {len(selected_articles)} articles")
    
    # Show top 5 priorities
    print(f"   Top 5 priorities:")
    for i, (article, score) in enumerate(scored_articles[:5], 1):
        headline = article.get('headline', '')[:60] + "..." if len(article.get('headline', '')) > 60 else article.get('headline', '')
        source = article.get('source', 'Unknown')
        print(f"     {i}. Score {score:.1f}: {headline} ({source})")
    
    return selected_articles

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
    Fetch news from all sources, prioritize, categorize, and return as a DataFrame.
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
            all_articles.append(article)
    except Exception as e:
        print(f"Error fetching from NewsAPI: {e}")

    # TODO: Add more sources (GNews, Bing News, etc.)

    # Remove duplicates first
    unique_articles = remove_duplicates(all_articles)
    
    # Select high-priority articles for processing
    high_priority_articles = select_high_priority_articles(unique_articles, max_count=25)
    
    # Use batch AI categorization on high-priority articles only
    print("🤖 Using AI to categorize high-priority articles...")
    try:
        categories = categorize_articles_batch(high_priority_articles)
    except Exception as e:
        print(f"⚠️ AI categorization failed: {e}, using fallback")
        categories = [categorize_article_fallback(article) for article in high_priority_articles]
    
    # Add categories to high-priority articles
    for i, article in enumerate(high_priority_articles):
        if i < len(categories):
            article['category'] = categories[i]
        else:
            article['category'] = 'Miscellaneous'
    
    # Convert to DataFrame and sort by priority
    df = pd.DataFrame(high_priority_articles)
    df = sort_articles_by_priority(df)
    return df

if __name__ == "__main__":
    df = collect_all_news()
    print(df.head()) 