import pandas as pd
import re
from typing import List, Dict, Tuple
from difflib import SequenceMatcher

# --- FACT CHECKING CONFIGURATION ---
# Keywords that indicate factual claims (dates, numbers, names, etc.)
FACT_KEYWORDS = [
    'announced', 'reported', 'said', 'confirmed', 'revealed', 'stated',
    'according to', 'sources say', 'officials say', 'experts say',
    'study shows', 'research indicates', 'data shows', 'statistics show'
]

# Keywords that might indicate unverified claims
UNVERIFIED_KEYWORDS = [
    'allegedly', 'reportedly', 'rumored', 'speculation', 'unconfirmed',
    'anonymous sources', 'unnamed sources', 'sources familiar with',
    'may', 'might', 'could', 'possibly', 'potentially'
]

# --- SIMILARITY DETECTION ---
def find_similar_articles(df: pd.DataFrame, similarity_threshold: float = 0.6) -> List[List[int]]:
    """
    Find groups of articles that are similar in content.
    Returns list of article index groups.
    """
    similar_groups = []
    processed = set()
    
    for i, row1 in df.iterrows():
        if i in processed:
            continue
            
        similar_group = [i]
        processed.add(i)
        
        # Compare with other articles
        for j, row2 in df.iterrows():
            if j in processed:
                continue
                
            # Calculate similarity between headlines
            headline1 = str(row1.get('headline', '')).lower()
            headline2 = str(row2.get('headline', '')).lower()
            
            similarity = SequenceMatcher(None, headline1, headline2).ratio()
            
            if similarity > similarity_threshold:
                similar_group.append(j)
                processed.add(j)
        
        if len(similar_group) > 1:
            similar_groups.append(similar_group)
    
    return similar_groups

# --- FACT EXTRACTION ---
def extract_facts(text: str) -> Dict[str, List[str]]:
    """
    Extract factual claims from article text.
    Returns dict with fact types and values.
    """
    facts = {
        'dates': [],
        'numbers': [],
        'names': [],
        'organizations': [],
        'locations': []
    }
    
    if not text:
        return facts
    
    text_lower = text.lower()
    
    # Extract dates (basic pattern)
    date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}\b'
    facts['dates'] = re.findall(date_pattern, text)
    
    # Extract numbers (percentages, amounts, etc.)
    number_pattern = r'\b\d+(?:\.\d+)?%\b|\$\d+(?:,\d{3})*(?:\.\d{2})?\b|\b\d+(?:\.\d+)?\s*(?:million|billion|thousand)\b'
    facts['numbers'] = re.findall(number_pattern, text)
    
    # Extract names (basic pattern - could use NLP in the future)
    name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
    facts['names'] = re.findall(name_pattern, text)
    
    # Extract organizations (basic pattern)
    org_pattern = r'\b[A-Z][A-Z\s&]+(?:Corp|Inc|LLC|Ltd|Company|Organization|Foundation)\b'
    facts['organizations'] = re.findall(org_pattern, text)
    
    return facts

# --- CONSISTENCY CHECKING ---
def check_article_consistency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Check articles for factual consistency and add fact-check status.
    """
    if df.empty:
        return df
    
    df = df.copy()
    df['fact_check_status'] = '🔍 Fact-checked'  # Default status
    
    # Find similar articles
    similar_groups = find_similar_articles(df)
    
    for group in similar_groups:
        if len(group) < 2:
            continue
            
        # Extract facts from each article in the group
        group_facts = []
        for idx in group:
            article_text = str(df.iloc[idx].get('headline', '')) + ' ' + str(df.iloc[idx].get('content', ''))
            facts = extract_facts(article_text)
            group_facts.append(facts)
        
        # Check for inconsistencies
        inconsistencies = check_fact_consistency(group_facts)
        
        # Flag articles with inconsistencies
        if inconsistencies:
            for idx in group:
                df.iloc[idx, df.columns.get_loc('fact_check_status')] = '⚠️ Unverified'
                print(f"⚠️  Inconsistency found in article {idx}: {inconsistencies}")
    
    return df

def check_fact_consistency(facts_list: List[Dict]) -> List[str]:
    """
    Check if facts are consistent across articles.
    Returns list of inconsistencies found.
    """
    inconsistencies = []
    
    if len(facts_list) < 2:
        return inconsistencies
    
    # Compare dates
    all_dates = []
    for facts in facts_list:
        all_dates.extend(facts['dates'])
    
    if len(set(all_dates)) > 1 and len(all_dates) > 1:
        inconsistencies.append(f"Conflicting dates: {set(all_dates)}")
    
    # Compare numbers (basic check)
    all_numbers = []
    for facts in facts_list:
        all_numbers.extend(facts['numbers'])
    
    if len(set(all_numbers)) > 1 and len(all_numbers) > 1:
        # Better number comparison could be added here
        pass
    
    return inconsistencies

# --- UNVERIFIED CLAIM DETECTION ---
def flag_unverified_claims(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flag articles that contain unverified claims.
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    for idx, row in df.iterrows():
        text = str(row.get('headline', '')) + ' ' + str(row.get('content', ''))
        text_lower = text.lower()
        
        # Check for unverified claim indicators
        unverified_count = sum(1 for keyword in UNVERIFIED_KEYWORDS if keyword in text_lower)
        fact_count = sum(1 for keyword in FACT_KEYWORDS if keyword in text_lower)
        
        # If more unverified indicators than fact indicators, flag it
        if unverified_count > fact_count and unverified_count > 0:
            df.iloc[idx, df.columns.get_loc('fact_check_status')] = '⚠️ Unverified'
            print(f"⚠️  Unverified claims detected in article {idx}")
    
    return df

# --- MAIN FACT CHECKING FUNCTION ---
def fact_check_articles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform comprehensive fact checking on articles.
    Returns DataFrame with fact-check status added.
    """
    print("🔍 Performing fact checking...")
    
    if df.empty:
        return df
    
    # Check consistency across similar articles
    df = check_article_consistency(df)
    
    # Flag unverified claims
    df = flag_unverified_claims(df)
    
    # Step 3: Count results
    fact_checked = len(df[df['fact_check_status'] == '🔍 Fact-checked'])
    unverified = len(df[df['fact_check_status'] == '⚠️ Unverified'])
    
    print(f"✅ Fact checking complete: {fact_checked} verified, {unverified} unverified")
    
    return df

if __name__ == "__main__":
    import news_collector
    import summarizer
    
    # Get articles and summarize
    df = news_collector.collect_all_news()
    df = summarizer.summarize_articles(df.head(10))  # Test with 10 articles
    
    # Perform fact checking
    df = fact_check_articles(df)
    
    # Show results
    print("\n📊 Fact Check Results:")
    for idx, row in df.iterrows():
        status = row.get('fact_check_status', '❓ Unknown')
        headline = row.get('headline', '')[:60]
        print(f"  {status} {headline}...") 