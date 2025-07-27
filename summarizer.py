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
    """Summarize articles in batch to avoid rate limits"""
    if df.empty:
        return df
    
    # Prepare batch prompt
    articles_text = ""
    for i, (_, article) in enumerate(df.iterrows(), 1):
        headline = article.get('headline', '')
        content = article.get('content', '')
        
        # Combine headline and content
        full_text = f"{headline}\n{content}".strip()
        articles_text += f"\n{i}. {full_text}\n"
    
    batch_prompt = SUMMARY_PROMPT.format(text=articles_text)
    
    try:
        print(f"🤖 Sending batch request for {len(df)} articles...")
        response = requests.post(
            GEMINI_API_URL,
            headers={'Content-Type': 'application/json'},
            params={'key': GEMINI_API_KEY},
            json={
                'contents': [{
                    'parts': [{'text': batch_prompt}]
                }]
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and data['candidates']:
                batch_summary = data['candidates'][0]['content']['parts'][0]['text']
                summaries = parse_batch_summaries(batch_summary, len(df))
                
                # Add summaries to DataFrame
                df_with_summaries = df.copy()
                df_with_summaries['summary'] = None  # Initialize summary column
                for i, summary in enumerate(summaries):
                    if i < len(df_with_summaries) and summary:
                        df_with_summaries.iloc[i, df_with_summaries.columns.get_loc('summary')] = summary
                
                print(f"✅ Successfully summarized {len(df)} articles in one batch!")
                return df_with_summaries
            else:
                raise Exception("No response content from Gemini API")
        else:
            print(f"❌ Gemini API request failed with status {response.status_code}")
            if response.status_code == 429:
                print("⏰ Rate limit exceeded - falling back to individual summarization")
            elif response.status_code == 400:
                print("🔧 Bad request - check prompt format")
            raise Exception(f"Gemini API error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Batch summarization failed: {e}")
        raise

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
        text = row.get('content') or row.get('headline', '')
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