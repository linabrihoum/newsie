# 📰 Newsie - A Daily News Digest

An automated Python script that collects news from trustworthy sources, summarizes & neutralizes articles using Google Gemini, performs  fact-checking, analyzes government bills, and sends a formatted HTML email digest daily.

## 🚀 Features

- **📰 News Collection**: Fetches articles from reliable sources (Reuters, Bloomberg, BBC, WSJ, etc.)
- **🤖 AI Summarization**: Uses Google Gemini to create neutral, factual summaries
- **🔍 Fact Checking**: Basic verification and consistency checking
- **🏛️ Bill Analysis**: Tracks government bills and their impact on sectors/companies
- **📧 HTML Email**: Beautiful, categorized email digest
- **⏰ Automation**: Runs daily via GitHub Actions at 9:00 AM Eastern Time

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
   - `GMAIL_CREDENTIALS`: Base64 encoded credentials.json
   
   **Optional Secret:**
   - `GMAIL_TOKEN`: Base64 encoded token.json (will be created automatically)

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
├── news_collector.py             # STEP 1: News collection
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

### News Sources
Edit `TRUSTED_KEYWORDS` in `news_collector.py` to modify news sources.

### Categories
Edit `CATEGORIES` in `news_collector.py` to modify article categorization.

### Email Schedule
Edit the cron expression in `.github/workflows/daily_news_digest.yml`:
- Current: `0 14 * * *` (9:00 AM Eastern Time)
- Format: `minute hour day month day-of-week`

## 📊 Email Format

The daily digest includes:
- 📰 **Technology** articles
- 🧬 **Health** news
- 🏛️ **Government/Policy** updates
- 📊 **Economy** reports
- 💵 **Finance** market news
- 📜 **Government Bill Summary** (if applicable)
- 📈 **Companies to Watch** (if applicable)

Each article includes:
- Headline with source link
- 2-3 sentence neutral summary
- Fact-check status (🔍 Verified / ⚠️ Unverified)

## ❤️ Acknowledgments

- [NewsAPI](https://newsapi.org/) for news data
- [Google Gemini](https://ai.google.dev/) for AI summarization
- [Gmail API](https://developers.google.com/gmail/api) for email sending
- [GitHub Actions](https://github.com/features/actions) for automation

---

**Happy news digesting! 📰✨** 