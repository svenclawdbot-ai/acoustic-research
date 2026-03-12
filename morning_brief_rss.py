#!/usr/bin/env python3
"""
Morning Brief RSS Fetcher
Fetches news from RSS feeds and outputs structured data.
"""

import feedparser
import json
from datetime import datetime, timedelta
from html import unescape
import re

# RSS Feed Sources
FEEDS = {
    # World News
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Reuters": "http://feeds.reuters.com/reuters/worldnews",
    
    # Tech
    "TechCrunch": "https://techcrunch.com/feed/",
    "Ars Technica": "http://feeds.arstechnica.com/arstechnica/index",
    
    # Finance
    "Bloomberg": "https://feeds.bloomberg.com/bloomberg/news",
}

def clean_text(text):
    """Clean HTML and extra whitespace from text."""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Unescape HTML entities
    text = unescape(text)
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def fetch_feed(name, url):
    """Fetch and parse a single RSS feed."""
    try:
        feed = feedparser.parse(url)
        articles = []
        
        for entry in feed.entries[:15]:  # Get last 15 entries
            # Parse published date
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6])
            
            # Skip articles older than 24 hours
            if published and published < datetime.now() - timedelta(hours=24):
                continue
            
            article = {
                "title": clean_text(entry.get("title", "")),
                "link": entry.get("link", ""),
                "summary": clean_text(entry.get("summary", entry.get("description", "")))[:300],
                "published": published.isoformat() if published else None,
                "source": name
            }
            articles.append(article)
        
        return articles
    except Exception as e:
        return [{"error": f"Failed to fetch {name}: {str(e)}"}]

def categorize_article(title, summary):
    """Categorize article based on content."""
    text = (title + " " + summary).lower()
    
    if any(word in text for word in ["stock", "market", "economy", "fed", "trade", "tariff", "inflation", "interest rate", "gdp", "finance", "earnings", "investor", "bloomberg"]):
        return "FINANCE"
    elif any(word in text for word in ["ai", "software", "app", "iphone", "android", "google", "apple", "microsoft", "tesla", "tech", "startup", "cyber", "hack", "crypto", "bitcoin"]):
        return "TECH"
    elif any(word in text for word in ["war", "ukraine", "israel", "iran", "china", "trump", "election", "president", "minister", "government", "sanction", "embassy", "attack", "bomb", "missile"]):
        return "WORLD"
    else:
        return "GENERAL"

def main():
    all_articles = []
    errors = []
    
    for name, url in FEEDS.items():
        articles = fetch_feed(name, url)
        if articles and "error" in articles[0]:
            errors.append(articles[0]["error"])
        else:
            all_articles.extend(articles)
    
    # Categorize articles
    categorized = {
        "WORLD": [],
        "TECH": [],
        "FINANCE": [],
        "GENERAL": []
    }
    
    for article in all_articles:
        category = categorize_article(article["title"], article["summary"])
        categorized[category].append(article)
    
    # Sort each category by date
    for cat in categorized:
        categorized[cat].sort(key=lambda x: x.get("published", ""), reverse=True)
    
    output = {
        "fetched_at": datetime.now().isoformat(),
        "total_articles": len(all_articles),
        "errors": errors,
        "categories": categorized
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
