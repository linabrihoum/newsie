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

load_dotenv()

def main():
    """Main function to demonstrate the news collection and summarization pipeline"""
    print("📰 Daily News Digest Pipeline")
    print("=" * 50)
    
    # STEP 1: Collect News
    print("\n🔍 STEP 1: Collecting news articles...")
    try:
        df = news_collector.collect_all_news()
        
        if df.empty:
            print("❌ No articles found. Check your API key and network connection.")
            return
            
        print(f"✅ Successfully collected {len(df)} articles!")
        
        # Show category distribution
        print("\n📊 Category Distribution:")
        category_counts = df['category'].value_counts()
        for category, count in category_counts.items():
            print(f"  {category}: {count} articles")
            
        # Show priority-sorted sample articles
        print("\n📝 Priority-Sorted Sample Articles:")
        categorized_articles = df[df['category'] != 'Miscellaneous']
        if not categorized_articles.empty:
            print("  🎯 Categorized Articles (High Priority):")
            for i, row in categorized_articles.head(3).iterrows():
                print(f"    {i+1}. [{row['category']}] {row['headline'][:70]}...")
                print(f"       Source: {row['source']}")
                print()
        
        # Show miscellaneous articles (lower priority)
        misc_articles = df[df['category'] == 'Miscellaneous']
        if not misc_articles.empty:
            print("  📰 Miscellaneous Articles (Lower Priority):")
            for i, row in misc_articles.head(2).iterrows():
                print(f"    {i+1}. {row['headline'][:70]}...")
                print(f"       Source: {row['source']}")
                print()
            
    except Exception as e:
        print(f"❌ Error in STEP 1: {e}")
        return
    
    # Summarize Articles
    print("\n🤖 STEP 2: Summarizing articles...")
    try:
        # Only summarize first 5 articles to avoid rate limits
        df_sample = df.head(5).copy()
        df_summarized = summarizer.summarize_articles(df_sample)
        
        print(f"✅ Successfully summarized {len(df_summarized)} articles!")
        
        # Show sample summaries
        print("\n📝 Sample Summaries:")
        for i, row in df_summarized.iterrows():
            if row.get('summary'):
                print(f"  {i+1}. {row['summary'][:150]}...")
                print()
                
    except Exception as e:
        print(f"❌ Error in STEP 2: {e}")
        return
    
    # Fact Checking
    print("\n🔍 STEP 3: Fact checking articles...")
    try:
        df_fact_checked = fact_checker.fact_check_articles(df_summarized)
        
        print(f"✅ Fact checking complete!")
        
        # Show fact check results
        print("\n📊 Fact Check Results:")
        for i, row in df_fact_checked.iterrows():
            status = row.get('fact_check_status', '❓ Unknown')
            headline = row.get('headline', '')[:60]
            print(f"  {status} {headline}...")
                
    except Exception as e:
        print(f"❌ Error in STEP 3: {e}")
        return
    
    # Government Bill Watcher
    print("\n🏛️  STEP 4: Analyzing government bills and policy impact...")
    try:
        df_with_bills, bill_impacts = bill_watcher.analyze_bill_impact(df_fact_checked)
        
        print(f"✅ Bill analysis complete!")
        
        # Show bill impact results
        if bill_impacts:
            print("\n📋 Bill Impact Analysis:")
            for impact in bill_impacts:
                print(f"  📋 {impact['bill_name'] or impact['bill_number']}")
                print(f"     Branch: {impact['branch_passed']}")
                print(f"     Sectors: {', '.join(impact['sectors_affected'])}")
                print(f"     Companies: {', '.join(impact['companies_affected'][:5])}...")
                print()
        else:
            print("📝 No government bills found in current articles.")
                
    except Exception as e:
        print(f"❌ Error in STEP 4: {e}")
        return
    
    print("\n🎉 Pipeline completed successfully!")
    print("Ready for STEP 5 (Email Composition) and beyond!")

if __name__ == "__main__":
    main() 