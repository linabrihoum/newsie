#!/usr/bin/env python3
"""
Daily News Digest
Demonstrates STEP 1 (News Collection) and STEP 2 (Summarization)
"""

import os
from dotenv import load_dotenv
import news_collector
import summarizer
import fact_checker
import bill_watcher
import email_composer
import email_sender

load_dotenv()

def main():
    print("📰 Daily News Digest Pipeline")
    print("=" * 50)
    
    # STEP 1: Collect News
    print("\n📰 News Collection: Collecting articles from trustworthy sources...")
    try:
        df = news_collector.collect_all_news()
        if df.empty:
            print("❌ No articles collected. Check NewsAPI key and internet connection.")
            return
        print(f"✅ News Collection complete! Found {len(df)} articles")
        print(f"📊 Articles by category:")
        category_counts = df['category'].value_counts()
        for category, count in category_counts.items():
            print(f"   {category}: {count}")
    except Exception as e:
        print(f"❌ News Collection failed: {e}")
        return
    
    # STEP 2: Summarize Articles
    print("\n🤖 AI Summarization: Generating neutral summaries using Google Gemini...")
    try:
        df_summarized = summarizer.summarize_articles(df)
        if df_summarized.empty:
            print("❌ No articles summarized. Check Gemini API key and rate limits.")
            return
        print(f"✅ AI Summarization complete! Summarized {len(df_summarized)} articles")
        
        # Show sample summaries
        print("\n📝 Sample Summaries:")
        for i, (_, article) in enumerate(df_summarized.head().iterrows(), 1):
            headline = article['headline'][:50] + "..." if len(article['headline']) > 50 else article['headline']
            summary = article.get('summary', '')
            if summary:
                summary_display = summary[:100] + "..." if len(summary) > 100 else summary
            else:
                summary_display = "No summary available"
            print(f"  {i}. {headline}")
            print(f"     {summary_display}")
            print()
    except Exception as e:
        print(f"❌ AI Summarization failed: {e}")
        return
    
    # STEP 3: Fact Checking
    print("\n🔍 Fact Checking: Verifying article consistency and flagging unverified claims...")
    try:
        df_fact_checked = fact_checker.fact_check_articles(df_summarized)
        print(f"✅ Fact Checking complete!")
        
        # Show fact check results
        verified_count = len(df_fact_checked[df_fact_checked['fact_check_status'] == '🔍 Fact-checked'])
        unverified_count = len(df_fact_checked[df_fact_checked['fact_check_status'] == '⚠️ Unverified'])
        print(f"📊 Fact Check Results:")
        print(f"  🔍 Fact-checked: {verified_count}")
        print(f"  ⚠️ Unverified: {unverified_count}")
        
        # Show sample fact-checked articles
        print("\n📋 Sample Fact-Checked Articles:")
        for _, article in df_fact_checked.head().iterrows():
            headline = article.get('headline', 'Unknown headline')
            headline_display = headline[:60] + "..." if len(headline) > 60 else headline
            status = article.get('fact_check_status', '❓ Unknown')
            print(f"  {status} {headline_display}")
    except Exception as e:
        print(f"❌ Fact Checking failed: {e}")
        return
    
    # STEP 4: Government Bill Watcher
    print("\n🏛️ Government Bill Analysis: Analyzing government bills and policy impact...")
    try:
        df_with_bills, bill_impacts = bill_watcher.analyze_bill_impact(df_fact_checked)
        print(f"✅ Government Bill Analysis complete!")
        
        if bill_impacts:
            print(f"📋 Bill Analysis Results:")
            print(f"  📜 Bills found: {len(bill_impacts)}")
            for i, bill in enumerate(bill_impacts, 1):
                print(f"    {i}. {bill.get('bill_name', 'Unknown Bill')}")
                print(f"       Branch: {bill.get('branch_passed', 'Unknown')}")
                print(f"       Sectors: {', '.join(bill.get('affected_sectors', []))}")
        else:
            print("📝 No government bills found in current articles.")
    except Exception as e:
        print(f"❌ Government Bill Analysis failed: {e}")
        return
    
    # STEP 5: Email Composition
    print("\n📧 Email Composition: Creating HTML email with categorized sections...")
    try:
        html_email = email_composer.create_html_email(df_with_bills, bill_impacts)
        preview_filename = email_composer.save_email_preview(html_email)
        print(f"✅ Email Composition complete!")
        print(f"📄 Email preview saved to: {preview_filename}")
        print(f"📊 Email contains {len(df_with_bills)} articles with summaries")
        print(f"📋 Bill impacts: {len(bill_impacts)} bills analyzed")
    except Exception as e:
        print(f"❌ Email Composition failed: {e}")
        return
    
    # STEP 6: Email Sending
    print("\n📧 Email Delivery: Sending daily news digest...")
    try:
        recipient_email = os.getenv('EMAIL_RECIPIENTS')
        if not recipient_email:
            print("⚠️ EMAIL_RECIPIENTS not set in environment. Skipping email sending.")
            print("💡 Set EMAIL_RECIPIENTS in your .env file to enable email sending.")
        else:
            success = email_sender.send_daily_digest(html_email, recipient_email)
            if success:
                print(f"✅ Email Delivery successful! Sent to {recipient_email}")
            else:
                print("❌ Email Delivery failed. Check Gmail API credentials.")
    except Exception as e:
        print(f"❌ Email Delivery failed: {e}")
        return
    
    print("\n🎉 Daily News Digest Pipeline completed successfully!")
    print("📰 Your automated news digest is ready for daily delivery!")
    print("⏰ Next run scheduled for 9:00 AM Eastern Time tomorrow.")

if __name__ == "__main__":
    main() 