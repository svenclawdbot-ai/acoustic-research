#!/usr/bin/env python3
"""
Enhanced Morning Brief RSS Fetcher
==================================

Fetches news from expanded RSS sources with optional AI summarization
via Moonshot API (Kimi).

Environment Variables:
    MOONSHOT_API_KEY: API key for AI summarization (optional)
    
Usage:
    export MOONSHOT_API_KEY="your-key-here"
    python3 morning_brief_rss_enhanced.py
"""

import feedparser
import json
import os
import re
import sys
from datetime import datetime, timedelta
from html import unescape
from typing import List, Dict, Optional

# Try to import Moonshot client (optional dependency)
try:
    from openai import OpenAI
    HAS_MOONSHOT = True
except ImportError:
    HAS_MOONSHOT = False

# Expanded RSS Feed Sources
FEEDS = {
    # World News
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Reuters": "http://feeds.reuters.com/reuters/worldnews",
    
    # Science
    "Nature News": "https://www.nature.com/nature.rss",
    "Science Magazine": "https://www.science.org/rss/news_current.xml",
    "New Scientist": "https://www.newscientist.com/feed/home/",
    
    # Tech
    "TechCrunch": "https://techcrunch.com/feed/",
    "Ars Technica": "http://feeds.arstechnica.com/arstechnica/index",
    "IEEE Spectrum": "https://spectrum.ieee.org/rss",
    "Hackaday": "https://hackaday.com/feed/",
    
    # Finance / Business
    "Bloomberg": "https://feeds.bloomberg.com/bloomberg/news",
    "Financial Times": "https://www.ft.com/?format=rss",
    "WSJ Markets": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    
    # Alternative / Investigative
    "Mother Jones": "https://www.motherjones.com/feed/",
    "Consortium News": "https://consortiumnews.com/feed/",
    
    # AI / Research
    "AI News": "https://www.artificialintelligence-news.com/feed/",
    "Papers With Code": "http://paperswithcode.com/rss",
    "MIT Tech Review": "https://www.technologyreview.com/feed/",
    
    # Medical
    "Medscape": "https://www.medscape.com/cx/rssfeeds/2700.xml",
    "Medical News Today": "https://www.medicalnewstoday.com/news.rss",
}


def clean_text(text: str, max_length: int = 500) -> str:
    """Clean HTML and extra whitespace from text."""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Unescape HTML entities
    text = unescape(text)
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_length]


def fetch_feed(name: str, url: str) -> List[Dict]:
    """Fetch and parse a single RSS feed."""
    try:
        feed = feedparser.parse(url)
        articles = []
        
        for entry in feed.entries[:10]:  # Get last 10 entries
            # Parse published date
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6])
            
            # Skip articles older than 48 hours (expanded window for more sources)
            if published and published < datetime.now() - timedelta(hours=48):
                continue
            
            article = {
                "title": clean_text(entry.get("title", ""), 200),
                "link": entry.get("link", ""),
                "summary": clean_text(entry.get("summary", entry.get("description", "")), 400),
                "published": published.isoformat() if published else None,
                "source": name,
                "raw_content": entry.get("summary", entry.get("description", ""))[:2000]
            }
            articles.append(article)
        
        return articles
    except Exception as e:
        print(f"⚠️  Warning: Failed to fetch {name}: {str(e)[:80]}", file=sys.stderr)
        return []


def categorize_article(title: str, summary: str) -> str:
    """Categorize article based on content with expanded keywords."""
    text = (title + " " + summary).lower()
    
    # Finance/Business
    if any(word in text for word in [
        "stock", "market", "economy", "fed", "trade", "tariff", "inflation", 
        "interest rate", "gdp", "finance", "earnings", "investor", "bloomberg",
        "ftse", "nasdaq", "dow jones", "s&p", "wall street", "bank", "recession"
    ]):
        return "FINANCE"
    
    # AI / Machine Learning
    elif any(word in text for word in [
        "ai", "artificial intelligence", "machine learning", "deep learning", 
        "neural network", "llm", "gpt", "chatbot", "algorithm", "automation",
        "robotics", "computer vision", "nlp", "openai", "anthropic", "google gemini"
    ]):
        return "AI_ML"
    
    # Tech
    elif any(word in text for word in [
        "software", "app", "iphone", "android", "google", "apple", "microsoft", 
        "tesla", "tech", "startup", "cyber", "hack", "crypto", "bitcoin",
        "semiconductor", "chip", "iphone", "gadget", "review"
    ]):
        return "TECH"
    
    # Science
    elif any(word in text for word in [
        "nature", "science", "research", "study", "experiment", "physics", 
        "chemistry", "biology", "quantum", "gene", "crispr", "vaccine",
        "climate", "space", "nasa", "astrophysics", "evolution"
    ]):
        return "SCIENCE"
    
    # Engineering
    elif any(word in text for word in [
        "ieee", "engineering", "circuit", "robot", "manufacturing", "3d print",
        "iot", "sensor", "hardware", "prototype", "hackaday", "maker"
    ]):
        return "ENGINEERING"
    
    # Medical/Health
    elif any(word in text for word in [
        "medical", "health", "drug", "fda", "clinical", "patient", "doctor",
        "hospital", "disease", "cancer", "therapy", "treatment", "vaccine"
    ]):
        return "MEDICAL"
    
    # Politics/World (expanded for Mother Jones, Consortium News)
    elif any(word in text for word in [
        "war", "ukraine", "israel", "iran", "china", "russia", "trump", 
        "election", "president", "minister", "government", "sanction", 
        "embassy", "attack", "bomb", "missile", "pentagon", "cia",
        "congress", "senate", "investigation", "whistleblower", "intelligence"
    ]):
        return "WORLD"
    
    else:
        return "GENERAL"


def summarize_with_moonshot(article: Dict, api_key: str) -> Optional[str]:
    """Generate AI summary using Moonshot API."""
    if not HAS_MOONSHOT:
        return None
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1"
        )
        
        prompt = f"""Summarize this news article in 2-3 sentences. Focus on the key facts and why it matters.

Title: {article['title']}
Source: {article['source']}
Content: {article['raw_content'][:1500]}

Provide a concise summary:"""
        
        response = client.chat.completions.create(
            model="kimi-latest",
            messages=[
                {"role": "system", "content": "You are a news summarizer. Be concise and factual."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️  Moonshot summary failed: {str(e)[:80]}", file=sys.stderr)
        return None


def generate_brief(categorized: Dict, total_articles: int, use_ai: bool) -> str:
    """Generate human-readable morning brief."""
    now = datetime.now().strftime("%A, %B %d, %Y")
    
    lines = [
        "=" * 70,
        f"MORNING BRIEF — {now}",
        "=" * 70,
        f"Sources: {len(FEEDS)} feeds | Articles: {total_articles} | AI Summary: {'✓' if use_ai else '✗'}",
        ""
    ]
    
    # Top stories (most recent from each major category)
    priority_categories = ["WORLD", "FINANCE", "AI_ML", "TECH", "SCIENCE"]
    
    lines.append("📰 TOP STORIES")
    lines.append("-" * 70)
    
    story_count = 0
    for cat in priority_categories:
        if categorized[cat] and story_count < 5:
            article = categorized[cat][0]  # Most recent
            lines.append(f"\n[{cat}] {article['source']}")
            lines.append(f"→ {article['title']}")
            if article.get('ai_summary'):
                lines.append(f"  {article['ai_summary'][:200]}...")
            else:
                lines.append(f"  {article['summary'][:200]}...")
            lines.append(f"  🔗 {article['link'][:70]}...")
            story_count += 1
    
    # Category summaries
    lines.extend([
        "",
        "=" * 70,
        "📊 CATEGORY BREAKDOWN",
        "=" * 70
    ])
    
    for cat in ["WORLD", "FINANCE", "AI_ML", "TECH", "SCIENCE", "ENGINEERING", "MEDICAL", "GENERAL"]:
        count = len(categorized[cat])
        if count > 0:
            lines.append(f"  {cat:15s}: {count:2d} articles")
    
    # Recent highlights by category
    for cat in priority_categories:
        if categorized[cat]:
            lines.extend([
                "",
                f"📌 {cat.replace('_', '/')} HIGHLIGHTS",
                "-" * 70
            ])
            for article in categorized[cat][:3]:
                lines.append(f"• {article['source']}: {article['title'][:70]}")
    
    lines.extend([
        "",
        "=" * 70,
        "End of Brief",
        "=" * 70
    ])
    
    return "\n".join(lines)


def main():
    # Check for Moonshot API key
    moonshot_key = os.environ.get("MOONSHOT_API_KEY")
    use_ai = moonshot_key and HAS_MOONSHOT
    
    if moonshot_key and not HAS_MOONSHOT:
        print("⚠️  MOONSHOT_API_KEY found but 'openai' package not installed.", file=sys.stderr)
        print("   Run: pip install openai", file=sys.stderr)
    
    print("Fetching RSS feeds...", file=sys.stderr)
    all_articles = []
    errors = []
    
    for name, url in FEEDS.items():
        articles = fetch_feed(name, url)
        if articles:
            all_articles.extend(articles)
            print(f"  ✓ {name}: {len(articles)} articles", file=sys.stderr)
        else:
            print(f"  ✗ {name}: No articles", file=sys.stderr)
    
    # Categorize articles
    categorized = {
        "WORLD": [],
        "FINANCE": [],
        "AI_ML": [],
        "TECH": [],
        "SCIENCE": [],
        "ENGINEERING": [],
        "MEDICAL": [],
        "GENERAL": []
    }
    
    for article in all_articles:
        category = categorize_article(article["title"], article["summary"])
        article["category"] = category
        categorized[category].append(article)
    
    # Sort each category by date
    for cat in categorized:
        categorized[cat].sort(key=lambda x: x.get("published", ""), reverse=True)
    
    # Generate AI summaries if key available
    if use_ai:
        print("\nGenerating AI summaries...", file=sys.stderr)
        # Summarize top 5 stories across categories
        top_stories = []
        for cat in ["WORLD", "FINANCE", "AI_ML", "TECH", "SCIENCE"]:
            if categorized[cat]:
                top_stories.append(categorized[cat][0])
        
        for article in top_stories:
            summary = summarize_with_moonshot(article, moonshot_key)
            if summary:
                article["ai_summary"] = summary
                print(f"  ✓ {article['source']}: {article['title'][:50]}...", file=sys.stderr)
    
    # Generate output
    output = {
        "fetched_at": datetime.now().isoformat(),
        "total_articles": len(all_articles),
        "ai_enabled": use_ai,
        "categories": categorized
    }
    
    # Print JSON for programmatic use
    json_output = json.dumps(output, indent=2)
    
    # Print human-readable brief
    brief = generate_brief(categorized, len(all_articles), use_ai)
    
    # Output based on mode
    if "--json" in sys.argv:
        print(json_output)
    else:
        print(brief)
    
    # Also save to file
    output_file = f"/home/james/.openclaw/workspace/morning_brief_{datetime.now().strftime('%Y-%m-%d')}.txt"
    with open(output_file, 'w') as f:
        f.write(brief)
    print(f"\n💾 Saved to: {output_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
