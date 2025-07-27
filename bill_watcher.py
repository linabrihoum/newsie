import pandas as pd
import re
from typing import Dict, List, Optional, Tuple

# --- BILL DETECTION CONFIGURATION ---
# Keywords that indicate bill-related news
BILL_KEYWORDS = [
    'bill', 'legislation', 'law', 'act', 'resolution', 'amendment',
    'passed', 'approved', 'voted', 'house', 'senate', 'congress',
    'legislative', 'legislature', 'federal', 'government'
]

# Keywords that indicate which branch passed it
BRANCH_KEYWORDS = {
    'house': ['house of representatives', 'house passed', 'house approved', 'house voted'],
    'senate': ['senate passed', 'senate approved', 'senate voted', 'senators'],
    'both': ['congress passed', 'congress approved', 'both chambers', 'house and senate']
}

# --- SECTOR MAPPING ---
SECTOR_KEYWORDS = {
    'AI/Technology': [
        'artificial intelligence', 'AI', 'machine learning', 'automation', 'robotics',
        'semiconductor', 'chip', 'computing', 'software', 'digital', 'cyber'
    ],
    'Renewable Energy': [
        'renewable energy', 'solar', 'wind', 'clean energy', 'green energy',
        'electric vehicle', 'EV', 'battery', 'sustainability', 'climate'
    ],
    'Healthcare': [
        'healthcare', 'medical', 'pharmaceutical', 'drug', 'treatment',
        'insurance', 'medicare', 'medicaid', 'hospital', 'doctor'
    ],
    'Infrastructure': [
        'infrastructure', 'construction', 'roads', 'bridges', 'transportation',
        'highway', 'railway', 'airport', 'port', 'building'
    ],
    'Finance': [
        'banking', 'finance', 'financial', 'regulation', 'SEC', 'federal reserve',
        'tax', 'revenue', 'budget', 'spending', 'deficit'
    ],
    'Defense': [
        'defense', 'military', 'weapons', 'national security', 'veterans',
        'armed forces', 'defense spending', 'military budget'
    ],
    'Education': [
        'education', 'school', 'university', 'college', 'student loan',
        'federal aid', 'scholarship', 'research funding'
    ]
}

# --- COMPANY MAPPING BY SECTOR ---
COMPANIES_BY_SECTOR = {
    'AI/Technology': [
        'NVDA', 'MSFT', 'GOOGL', 'META', 'AAPL', 'AMD', 'INTC', 'TSM',
        'ORCL', 'CRM', 'ADBE', 'NFLX', 'AMZN', 'TSLA'
    ],
    'Renewable Energy': [
        'TSLA', 'ENPH', 'PLUG', 'SEDG', 'RUN', 'SPWR', 'FSLR', 'NEE',
        'GE', 'GEVO', 'BLDP', 'BE', 'NIO', 'XPEV', 'LI'
    ],
    'Healthcare': [
        'JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR',
        'LLY', 'BMY', 'AMGN', 'GILD', 'CVS', 'ANTM'
    ],
    'Infrastructure': [
        'CAT', 'DE', 'CEMEX', 'VMC', 'MLM', 'URI', 'TEX', 'FLR',
        'J', 'ACM', 'PWR', 'EME', 'MTZ'
    ],
    'Finance': [
        'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC',
        'TFC', 'COF', 'AXP', 'BLK', 'SCHW', 'SPGI'
    ],
    'Defense': [
        'LMT', 'RTX', 'BA', 'GD', 'NOC', 'LHX', 'TDG', 'AJRD',
        'KTOS', 'AIR', 'TDG', 'HII', 'LDOS'
    ],
    'Education': [
        'APEI', 'LOPE', 'STRA', 'ZVO', 'LAUR', 'EDU', 'TAL', 'GHC'
    ]
}

# --- BILL EXTRACTION ---
def extract_bill_info(article_text: str) -> Optional[Dict]:
    """
    Extract bill information from article text.
    Returns dict with bill details or None if no bill found.
    """
    if not article_text:
        return None
    
    text_lower = article_text.lower()
    
    # Check if article contains bill-related keywords
    if not any(keyword in text_lower for keyword in BILL_KEYWORDS):
        return None
    
    bill_info = {
        'bill_name': None,
        'bill_number': None,
        'branch_passed': None,
        'explanation': None,
        'sectors_affected': []
    }
    
    # Extract bill name (look for patterns, ex: "H.R. 1234" or "S. 5678")
    bill_patterns = [
        r'([A-Z]\.R\.\s+\d+)',  # H.R. 1234
        r'([A-Z]\.\s+\d+)',     # S. 5678
        r'([A-Z][A-Z]\d+)',     # HR1234, S5678
        r'([A-Z][a-z]+\.?\s+\d+)'  # House 1234, Senate 5678
    ]
    
    for pattern in bill_patterns:
        matches = re.findall(pattern, article_text, re.IGNORECASE)
        if matches:
            bill_info['bill_number'] = matches[0]
            break
    
    # Determine which branch passed it
    for branch, keywords in BRANCH_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            bill_info['branch_passed'] = branch
            break
    
    # Extract bill name (look for quoted text or capitalized phrases)
    name_patterns = [
        r'"([^"]+)"',  # Quoted text
        r'([A-Z][A-Za-z\s]+Act)',  # Something Act
        r'([A-Z][A-Za-z\s]+Bill)',  # Something Bill
        r'([A-Z][A-Za-z\s]+Law)'   # Something Law
    ]
    
    for pattern in name_patterns:
        matches = re.findall(pattern, article_text)
        if matches:
            bill_info['bill_name'] = matches[0]
            break
    
    # Generate explanation if we have bill info
    if bill_info['bill_number'] or bill_info['bill_name']:
        bill_info['explanation'] = generate_bill_explanation(article_text)
        bill_info['sectors_affected'] = identify_affected_sectors(article_text)
    
    return bill_info if (bill_info['bill_number'] or bill_info['bill_name']) else None

def generate_bill_explanation(article_text: str) -> str:
    """
    Generate a brief, neutral explanation of what the bill does.
    """
    # Extract key phrases that explain the bill's purpose
    explanation_keywords = [
        'funds', 'funding', 'allocates', 'provides', 'establishes',
        'regulates', 'regulations', 'requires', 'mandates', 'authorizes',
        'creates', 'expands', 'reduces', 'increases', 'decreases'
    ]
    
    sentences = article_text.split('.')
    relevant_sentences = []
    
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in explanation_keywords):
            relevant_sentences.append(sentence.strip())
    
    if relevant_sentences:
        return relevant_sentences[0][:200] + "..."
    else:
        return "Bill details and funding information available from official sources."

def identify_affected_sectors(article_text: str) -> List[str]:
    """
    Identify which sectors are affected by the bill.
    """
    text_lower = article_text.lower()
    affected_sectors = []
    
    for sector, keywords in SECTOR_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            affected_sectors.append(sector)
    
    return affected_sectors

# --- COMPANY IDENTIFICATION ---
def get_affected_companies(sectors: List[str], max_companies: int = 10) -> List[str]:
    """
    Get list of companies that might be affected by the bill.
    """
    companies = []
    
    for sector in sectors:
        if sector in COMPANIES_BY_SECTOR:
            companies.extend(COMPANIES_BY_SECTOR[sector])
    
    # Remove duplicates and limit to max_companies
    unique_companies = list(set(companies))
    return unique_companies[:max_companies]

# --- MAIN BILL ANALYSIS ---
def analyze_bill_impact(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
    """
    Analyze Government/Policy articles for bill information and impact.
    Returns updated DataFrame and list of bill impacts.
    """
    print("🏛️  Analyzing government bills and policy impact...")
    
    if df.empty:
        return df, []
    
    # Filter for Government/Policy articles
    gov_articles = df[df['category'] == 'Government/Policy'].copy()
    
    if gov_articles.empty:
        print("📝 No Government/Policy articles found for bill analysis.")
        return df, []
    
    bill_impacts = []
    
    for idx, row in gov_articles.iterrows():
        article_text = str(row.get('headline', '')) + ' ' + str(row.get('content', ''))
        bill_info = extract_bill_info(article_text)
        
        if bill_info:
            # Get affected companies
            affected_companies = get_affected_companies(bill_info['sectors_affected'])
            
            bill_impact = {
                'article_index': idx,
                'headline': row.get('headline'),
                'bill_name': bill_info['bill_name'],
                'bill_number': bill_info['bill_number'],
                'branch_passed': bill_info['branch_passed'],
                'explanation': bill_info['explanation'],
                'sectors_affected': bill_info['sectors_affected'],
                'companies_affected': affected_companies
            }
            
            bill_impacts.append(bill_impact)
            print(f"📋 Bill found: {bill_info['bill_name'] or bill_info['bill_number']}")
            print(f"   Branch: {bill_info['branch_passed']}")
            print(f"   Sectors: {', '.join(bill_info['sectors_affected'])}")
            print(f"   Companies: {', '.join(affected_companies[:5])}...")
            print()
    
    # Add bill impact column to DataFrame
    df = df.copy()
    df['bill_impact'] = None
    
    for impact in bill_impacts:
        idx = impact['article_index']
        df.iloc[idx, df.columns.get_loc('bill_impact')] = '📋 Bill Impact'
    
    print(f"✅ Bill analysis complete: {len(bill_impacts)} bills found")
    return df, bill_impacts

if __name__ == "__main__":
    import news_collector
    import summarizer
    import fact_checker
    
    # Get articles and process
    df = news_collector.collect_all_news()
    df = summarizer.summarize_articles(df.head(10))
    df = fact_checker.fact_check_articles(df)
    
    # Analyze bill impact
    df, bill_impacts = analyze_bill_impact(df)
    
    # Show results
    print("\n📊 Bill Analysis Results:")
    for impact in bill_impacts:
        print(f"  📋 {impact['bill_name'] or impact['bill_number']}")
        print(f"     Branch: {impact['branch_passed']}")
        print(f"     Sectors: {', '.join(impact['sectors_affected'])}")
        print(f"     Companies: {', '.join(impact['companies_affected'][:5])}...")
        print() 