# 📰 Newsie - A Daily News Digest

An automated Python script that collects news from trustworthy sources, prioritizes articles using an intelligent scoring system, categorizes them with AI, summarizes & neutralizes articles using Google Gemini, performs fact-checking, analyzes government bills, and sends a formatted HTML email digest daily.

## 🚀 Features

- **📰 Smart News Collection**: Fetches articles from reliable sources (Reuters, Bloomberg, BBC, WSJ, etc.)
- **🎯 Priority Scoring System**: Intelligently ranks articles by importance using multiple factors
- **🤖 AI-Powered Categorization**: Uses Google Gemini to categorize articles into relevant sections
- **🤖 AI Summarization**: Uses Google Gemini to create neutral, factual summaries
- **🔍 Fact Checking**: Basic verification and consistency checking
- **🏛️ Bill Analysis**: Tracks government bills and their impact on sectors/companies
- **📧 HTML Email**: Categorized email digest formatted with HTML to section out
- **⏰ Automation**: Runs daily with GitHub Actions at 9:00 AM Eastern Time

## 🎯 Priority Scoring System

The system uses a scoring algorithm to identify the most important articles from hundreds of daily news items. Only the top 25 highest-priority articles are selected for full AI processing.

### Scoring Factors (Total Possible Score: ~50+ points)

#### 🏆 **Source Credibility** (+10 points)
Trusted news sources get automatic priority:
- Reuters, Associated Press, Bloomberg, BBC, Wall Street Journal
- Financial Times, The Guardian, PBS NewsHour, Politico
- Al Jazeera, The Hill, Axios

#### 🚨 **Breaking News Indicators** (+8 points)
Articles with urgent keywords:
- "Breaking", "urgent", "just in", "developing", "live", "update"
- "crisis", "emergency", "deadline", "immediate", "critical"

#### 💼 **High-Impact Topics** (+6 points each)
Major political and business stories:
- **Politics**: President, Congress, Senate, House, White House, Administration
- **Government**: Federal Reserve, SEC, FDA, Supreme Court, Election
- **Major Companies**: Apple, Microsoft, Google, Amazon, Tesla, Nvidia, Meta
- **Financial Institutions**: JPMorgan, Goldman Sachs, Bank of America, Wells Fargo
- **Pharmaceuticals**: Pfizer, Moderna, Johnson & Johnson, AstraZeneca

#### 📈 **Market-Moving Events** (+5 points each)
Financial and economic news:
- Earnings, quarterly results, stock market, Dow Jones, NASDAQ, S&P
- Mergers, acquisitions, IPO, bankruptcy, layoffs, hiring
- Interest rates, inflation, GDP, jobs report, unemployment

#### 🤖 **Technology & Innovation** (+4 points each)
Tech and innovation stories:
- Artificial intelligence, AI, machine learning, blockchain, crypto
- Cybersecurity, data breach, hack, software, startup, unicorn
- SpaceX, NASA, satellite, rocket, space exploration

#### 🏥 **Health & Safety** (+4 points each)
Medical and health-related news:
- COVID, pandemic, vaccine, FDA approval, clinical trial
- Cancer, treatment, hospital, medical, healthcare, insurance
- Genetics, medicine, CDC, WHO

#### 🌍 **International Significance** (+3 points each)
Global and diplomatic news:
- Russia, Ukraine, China, Iran, North Korea, Israel, Palestine
- NATO, United Nations, trade war, sanctions, embargo
- Refugee, migration, border, diplomatic, embassy

#### ⏰ **Recency Bonus** (+1-2 points)
Newer articles get slight priority:
- Very recent (<6 hours): +2 points
- Recent (<12 hours): +1 point

#### 📝 **Content Quality** (+0.5-1 point)
More detailed articles:
- Long content (>500 chars): +1 point
- Medium content (>200 chars): +0.5 points

## 🤖 AI-Powered Categorization

The system uses Google Gemini to intelligently categorize articles into 7 main categories:

### Categories & AI Prompts

The AI analyzes article content and assigns one of these categories:

1. **🧠 Technology**: Tech companies, software, AI, digital innovation, startups
2. **🧬 Health**: Medical, healthcare, pharmaceuticals, wellness, hospitals
3. **🏛️ Government/Policy**: Politics, laws, regulations, government agencies, elections
4. **📊 Economy**: Economic indicators, jobs, GDP, inflation, business trends
5. **💵 Finance**: Stock markets, banking, investments, financial markets, trading
6. **🌍 World**: International news, foreign countries, global events, diplomacy
7. **🚀 Space**: NASA, space exploration, astronauts, satellites, space agencies

### AI Categorization Process

1. **Batch Processing**: Multiple articles are sent to Gemini in a single API call
2. **Content Analysis**: AI analyzes headline, description, and content
3. **Context Understanding**: AI understands nuances and context better than keyword matching
4. **Category Assignment**: AI assigns the most appropriate category from our predefined list
5. **Fallback System**: If AI fails, falls back to keyword-based categorization

## 📋 Prerequisites

- Python 3.11+
- Google Cloud Project with Gmail API enabled
- NewsAPI account
- Google Gemini API access

## 🛠️ Setup Instructions

### 1. Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd newsie
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file**:
   ```env
   NEWSAPI_KEY=your_newsapi_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   EMAIL_SENDER=your_email@gmail.com
   EMAIL_RECIPIENTS=recipient_email@gmail.com
   ```

4. **Set up Gmail API credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download credentials as `credentials.json`
   - Place `credentials.json` in the project root

5. **Test locally**:
   ```bash
   python main.py
   ```

### 2. GitHub Actions Setup

1. **Add GitHub Secrets** (Settings → Secrets and variables → Actions):
   
   **Required Secrets:**
   - `NEWSAPI_KEY`: Your NewsAPI key
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `EMAIL_SENDER`: Your Gmail address
   - `EMAIL_RECIPIENTS`: Recipient email address(es)
   - `CREDENTIALS_JSON_B64`: Base64 encoded credentials.json
   
   **Optional Secret:**
   - `TOKEN_JSON_B64`: Base64 encoded token.json (will be created automatically)

2. **Encode your credentials for GitHub**:
   ```bash
   # On Windows PowerShell:
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("credentials.json"))
   
   # On Linux/Mac:
   base64 -i credentials.json
   ```

3. **Test the workflow**:
   - Go to Actions tab in your GitHub repo
   - Click "Daily News Digest"
   - Click "Run workflow" to test manually

## 📁 Project Structure

```
newsie/
├── .github/workflows/
│   └── daily_news_digest.yml    # GitHub Actions workflow
├── news_collector.py             # STEP 1: News collection & priority scoring
├── summarizer.py                 # STEP 2: AI summarization
├── fact_checker.py               # STEP 3: Fact checking
├── bill_watcher.py               # STEP 4: Bill analysis
├── email_composer.py             # STEP 5: Email composition
├── email_sender.py               # STEP 6: Email sending
├── main.py                       # Main orchestration script
├── requirements.txt              # Python dependencies
├── credentials.json              # Gmail API credentials
├── token.json                    # Gmail API token (auto-generated)
├── .env                         # Environment variables
└── README.md                    # This file
```

## 🔧 Configuration

### Priority Scoring
Edit the scoring functions in `news_collector.py`:
- `calculate_article_priority()`: Modify scoring weights and keywords
- `select_high_priority_articles()`: Change the number of articles selected (default: 25)

### AI Categorization
Edit the AI prompts in `news_collector.py`:
- `categorize_articles_batch()`: Modify category definitions and AI prompts
- `CATEGORIES`: Add or modify keyword-based fallback categories

### News Sources
Edit `TRUSTED_KEYWORDS` in `news_collector.py` to modify news sources.

### Email Schedule
Edit the cron expression in `.github/workflows/daily_news_digest.yml`:
- Current: `0 14 * * *` (9:00 AM Eastern Time)
- Format: `minute hour day month day-of-week`

## 📊 Email Format

The daily digest includes:
- 🧠 **Technology** articles
- 🧬 **Health** news
- 🏛️ **Government/Policy** updates
- 📊 **Economy** reports
- 💵 **Finance** market news
- 🌍 **World** international news
- 🚀 **Space** exploration news
- 📜 **Government Bill Summary** (if applicable)
- 📈 **Companies to Watch** (if applicable)

Each article includes:
- Headline with source link
- 2-3 sentence neutral summary
- Fact-check status (🔍 Verified / ⚠️ Unverified)

## 📈 Performance Metrics

### Typical Daily Results
- **Articles Collected**: ~90-100 articles
- **Duplicates Removed**: ~5-10 articles
- **Priority Articles Selected**: 25 articles
- **AI Categorization Success Rate**: >95%
- **AI Summarization Success Rate**: >90%
- **Email Delivery Success Rate**: >99%

### Processing Pipeline
1. **Collection**: Fetch ~100 articles from NewsAPI
2. **Deduplication**: Remove ~5-10 duplicate articles
3. **Priority Scoring**: Rank all articles by importance
4. **Selection**: Choose top 25 priority articles
5. **AI Categorization**: Categorize with Google Gemini
6. **AI Summarization**: Summarize with Google Gemini
7. **Fact Checking**: Verify article consistency
8. **Bill Analysis**: Analyze government policy impact
9. **Email Composition**: Create HTML digest
10. **Email Delivery**: Send via Gmail API

## ❤️ Acknowledgments

- [NewsAPI](https://newsapi.org/) for news data
- [Google Gemini](https://ai.google.dev/) for AI categorization and summarization
- [Gmail API](https://developers.google.com/gmail/api) for email sending
- [GitHub Actions](https://github.com/features/actions) for automation

---

**Happy news digesting! 📰✨** 