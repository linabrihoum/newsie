import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

# --- EMAIL COMPOSER CONFIGURATION ---
# Category names
CATEGORY_EMOJIS = {
    'Technology': '🧠',
    'Health': '🧬', 
    'Government/Policy': '🏛️',
    'Economy': '📊',
    'Finance': '💵',
    'World': '🌍',
    'Space': '🚀',
    'Miscellaneous': '📰'
}

# --- HTML EMAIL TEMPLATE ---
def get_email_css() -> str:
    """Get CSS styling for the email"""
    return """
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .email-container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                 color: white; padding: 30px; text-align: center; border-radius: 10px; }
        .header h1 { margin: 0; font-size: 28px; }
        .header .date { margin-top: 10px; opacity: 0.9; }
        .category-section { margin: 30px 0; }
        .category-header { background: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; 
                          margin-bottom: 20px; border-radius: 5px; }
        .category-title { font-size: 20px; font-weight: bold; margin: 0; }
        .article { background: white; padding: 20px; margin: 15px 0; border-radius: 8px; 
                  box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #e9ecef; }
        .article:hover { box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
        .headline { font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }
        .summary { color: #555; margin-bottom: 10px; line-height: 1.5; }
        .meta { font-size: 12px; color: #888; margin-bottom: 8px; }
        .fact-check { display: inline-block; padding: 4px 8px; border-radius: 12px; 
                     font-size: 11px; font-weight: bold; }
        .fact-checked { background: #d4edda; color: #155724; }
        .unverified { background: #f8d7da; color: #721c24; }
        .bill-section { background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; 
                       margin: 20px 0; border-radius: 8px; }
        .bill-header { font-size: 18px; font-weight: bold; color: #856404; margin-bottom: 15px; }
        .bill-item { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .bill-name { font-weight: bold; color: #2c3e50; }
        .bill-details { color: #666; font-size: 14px; margin: 5px 0; }
        .companies { background: #e8f5e8; padding: 10px; border-radius: 5px; margin-top: 10px; }
        .footer { text-align: center; margin-top: 30px; padding: 20px; 
                 background: #f8f9fa; border-radius: 8px; color: #666; }
        .stats { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
                     gap: 10px; }
        .stat-item { text-align: center; }
        .stat-number { font-size: 24px; font-weight: bold; color: #1976d2; }
        .stat-label { font-size: 12px; color: #666; }
    </style>
    """

def format_article_html(article: pd.Series) -> str:
    """Format a single article as HTML"""
    headline = article.get('headline', '')
    summary = article.get('summary', '')
    source = article.get('source', '')
    category = article.get('category', '')
    url = article.get('url', '')
    fact_check_status = article.get('fact_check_status', '🔍 Fact-checked')
    
    # Handle None or empty summaries
    if not summary or summary == 'None':
        summary = "Summary not available"
    
    # Determine fact-check styling
    if 'Unverified' in fact_check_status:
        fact_check_class = 'unverified'
    else:
        fact_check_class = 'fact-checked'
    
    # Create headline link if URL exists
    headline_html = f'<a href="{url}" style="color: #2c3e50; text-decoration: none;">{headline}</a>' if url else headline
    
    return f"""
    <div class="article">
        <div class="meta">
            <strong>{source}</strong> • {category}
            <span class="fact-check {fact_check_class}">{fact_check_status}</span>
        </div>
        <div class="headline">{headline_html}</div>
        <div class="summary">{summary}</div>
    </div>
    """

def format_bill_section(bill_impacts: List[Dict]) -> str:
    """Format the bill impact section as HTML"""
    if not bill_impacts:
        return ""
    
    html = """
    <div class="bill-section">
        <div class="bill-header">📜 Government Bill Summary & Impact</div>
    """
    
    for impact in bill_impacts:
        bill_name = impact.get('bill_name') or impact.get('bill_number', 'Unknown Bill')
        branch = impact.get('branch_passed', 'Unknown')
        explanation = impact.get('explanation', '')
        sectors = impact.get('sectors_affected', [])
        companies = impact.get('companies_affected', [])
        
        # Handle None values for branch
        branch_display = branch.title() if branch and branch != 'Unknown' else 'Unknown'
        
        html += f"""
        <div class="bill-item">
            <div class="bill-name">{bill_name}</div>
            <div class="bill-details">
                <strong>Branch:</strong> {branch_display}<br>
                <strong>Impact:</strong> {explanation}
            </div>
        """
        
        if sectors:
            html += f'<div class="bill-details"><strong>Sectors Affected:</strong> {", ".join(sectors)}</div>'
        
        if companies:
            html += f"""
            <div class="companies">
                <strong>Companies to Watch:</strong> {", ".join(companies)}
            </div>
            """
        
        html += "</div>"
    
    html += "</div>"
    return html

def create_stats_section(df: pd.DataFrame) -> str:
    """Create a statistics section for the email"""
    total_articles = len(df)
    fact_checked = len(df[df.get('fact_check_status', '').str.contains('Fact-checked', na=False)])
    unverified = len(df[df.get('fact_check_status', '').str.contains('Unverified', na=False)])
    
    # Category counts
    category_counts = df['category'].value_counts()
    top_category = category_counts.index[0] if not category_counts.empty else 'None'
    top_count = category_counts.iloc[0] if not category_counts.empty else 0
    
    return f"""
    <div class="stats">
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-number">{total_articles}</div>
                <div class="stat-label">Total Articles</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{fact_checked}</div>
                <div class="stat-label">Fact-Checked</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{unverified}</div>
                <div class="stat-label">Unverified</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{top_category}</div>
                <div class="stat-label">Top Category</div>
            </div>
        </div>
    </div>
    """

def create_html_email(df: pd.DataFrame, bill_impacts: List[Dict] = None) -> str:
    """
    Create a complete HTML email with all sections.
    Returns the complete HTML email string.
    """
    if bill_impacts is None:
        bill_impacts = []
    
    # Get today's date
    today = datetime.now().strftime("%B %d, %Y")
    
    # Start building the email
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily News Digest - {today}</title>
        {get_email_css()}
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>📰 Daily News Digest</h1>
                <div class="date">{today}</div>
            </div>
    """
    
    # Add statistics section
    html += create_stats_section(df)
    
    # Group articles by category (priority categories first)
    priority_categories = ['Technology', 'Health', 'Government/Policy', 'Economy', 'Finance', 'World', 'Space']
    
    for category in priority_categories:
        category_articles = df[df['category'] == category]
        if not category_articles.empty:
            emoji = CATEGORY_EMOJIS.get(category, '📰')
            html += f"""
            <div class="category-section">
                <div class="category-header">
                    <h2 class="category-title">{emoji} {category}</h2>
                </div>
            """
            
            # Show all articles in priority categories (up to 15 each)
            for _, article in category_articles.head(15).iterrows():
                html += format_article_html(article)
            
            html += "</div>"
    
    # Add bill impact section if there are bills
    if bill_impacts:
        html += format_bill_section(bill_impacts)
    
    # Add Miscellaneous section at the end (show more articles)
    misc_articles = df[df['category'] == 'Miscellaneous']
    if not misc_articles.empty:
        html += f"""
        <div class="category-section">
            <div class="category-header">
                <h2 class="category-title">📰 Miscellaneous</h2>
            </div>
        """
        
        # Show more miscellaneous articles (up to 20)
        for _, article in misc_articles.head(20).iterrows():
            html += format_article_html(article)
        
        html += "</div>"
    
    # Add footer
    html += f"""
            <div class="footer">
                <p>📰 Daily News Digest • Generated on {today}</p>
                <p>Powered by NewsAPI & Google Gemini</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def save_email_preview(html_content: str, filename: str = "email_preview.html") -> str:
    """Save the email HTML to a file for preview"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return filename

if __name__ == "__main__":
    import news_collector
    import summarizer
    import fact_checker
    import bill_watcher
    
    # Get articles and process
    df = news_collector.collect_all_news()
    df = summarizer.summarize_articles(df.head(10))
    df = fact_checker.fact_check_articles(df)
    df, bill_impacts = bill_watcher.analyze_bill_impact(df)
    
    # Create email
    html_email = create_html_email(df, bill_impacts)
    
    # Save preview
    filename = save_email_preview(html_email)
    print(f"✅ Email preview saved to: {filename}")
    print("📧 Email composition complete!") 