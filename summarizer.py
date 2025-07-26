import os
import requests
import pandas as pd
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

# Gemini API key should be set as an environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent'

# --- PROMPT TEMPLATE ---
SUMMARY_PROMPT = (
    "Summarize this news article in 2–3 sentences. "
    "Remove political bias or emotionally charged language and keep it objective.\n"
    "Article: {text}"
)

# --- SUMMARIZATION FUNCTION ---
def summarize_and_neutralize(text: str) -> Optional[str]:
    """
    Summarize and neutralize a news article using Google Gemini API.
    Returns the summary string, or None if summarization fails.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    if not text or len(text.strip()) < 40:
        return None  # Skip very short or empty articles

    prompt = SUMMARY_PROMPT.format(text=text)
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        # Gemini returns summary in a nested structure
        summary = result['candidates'][0]['content']['parts'][0]['text']
        return summary.strip()
    except Exception as e:
        print(f"Gemini summarization error: {e}")
        return None

# --- BATCH SUMMARIZATION ---
def summarize_articles_batch(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize all articles in one batch request.
    Sends all articles in a single prompt to Gemini.
    """
    if df.empty:
        return df
    
    # Prepare all articles for processing
    articles_text = ""
    for idx, row in df.iterrows():
        headline = row.get('headline', '')
        content = row.get('content', '')
        source = row.get('source', '')
        
        article_text = f"Headline: {headline}\nContent: {content}\nSource: {source}\n\n"
        articles_text += article_text
    
    # Create prompt
    batch_prompt = (
        "Summarize each of the following news articles in 2-3 sentences. "
        "Remove political bias or emotionally charged language and keep it objective. "
        "Format your response as a numbered list matching the order of articles:\n\n"
        f"{articles_text}"
    )
    
    try:
        headers = {"Content-Type": "application/json"}
        params = {"key": GEMINI_API_KEY}
        data = {
            "contents": [{"parts": [{"text": batch_prompt}]}]
        }
        
        print(f"🤖 Sending batch request for {len(df)} articles...")
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        # Extract the batch response
        batch_summary = result['candidates'][0]['content']['parts'][0]['text']
        
        # Parse the numbered list response
        summaries = parse_batch_summaries(batch_summary, len(df))
        
        # Add summaries to DataFrame
        df = df.copy()
        df['summary'] = summaries
        print(f"✅ Successfully summarized {len(df)} articles in one batch!")
        
        return df
        
    except Exception as e:
        print(f"❌ Batch summarization error: {e}")
        # Fallback to individual summaries for first few articles
        return summarize_articles_individual(df.head(3))

def parse_batch_summaries(batch_response: str, expected_count: int) -> List[str]:
    """
    Parse the batch response from Gemini into individual summaries.
    """
    summaries = []
    lines = batch_response.split('\n')
    
    for line in lines:
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
            # Extract summary text (remove numbering)
            summary = line.split('.', 1)[-1].strip()
            if summary:
                summaries.append(summary)
    
    # Ensure we have the right number of summaries
    while len(summaries) < expected_count:
        summaries.append(None)
    
    return summaries[:expected_count]

def summarize_articles_individual(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fallback method: summarize articles individually (original method).
    """
    summaries = []
    for idx, row in df.iterrows():
        text = row.get('content') or row.get('headline')
        summary = summarize_and_neutralize(text)
        summaries.append(summary)
    df = df.copy()
    df['summary'] = summaries
    return df

# --- BULK SUMMARIZATION ---
def summarize_articles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize articles using batch processing to avoid rate limits.
    Falls back to individual processing if batch fails.
    """
    if df.empty:
        return df
    
    # Try batch summarization first
    try:
        return summarize_articles_batch(df)
    except Exception as e:
        print(f"⚠️  Batch summarization failed: {e}")
        print("🔄 Falling back to individual summarization...")
        return summarize_articles_individual(df.head(5))  # Limit to 5 for rate limits

if __name__ == "__main__":
    # Example usage: load articles and summarize
    import news_collector
    df = news_collector.collect_all_news()
    df = summarize_articles(df)
    print(df[['headline', 'summary']].head()) 