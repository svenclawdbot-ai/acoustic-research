#!/usr/bin/env python3
"""
Morning Brief RSS Fetcher
Fetches news from RSS feeds and outputs structured data.
Uses stdlib only — no external dependencies.
"""

import xml.etree.ElementTree as ET
import urllib.request
import json
import re
from datetime import datetime, timedelta
from html import unescape

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
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            xml_content = r.read()
        
        root = ET.fromstring(xml_content)
        articles = []
        
        # Find all item elements (works for RSS 2.0)
        for item in root.findall('.//item'):
            title = item.find('title')
            link = item.find('link')
            desc = item.find('description')
            pub_date = item.find('pubDate')
            
            if title is not None and link is not None:
                article = {
                    "title": clean_text(title.text or ""),
                    "link": link.text or "",
                    "summary": clean_text(desc.text if desc is not None else "")[:300],
                    "published": pub_date.text if pub_date is not None else None,
                    "source": name
                }
                articles.append(article)
            
            if len(articles) >= 15:  # Limit to last 15 entries
                break
        
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
    
    output = {
        "fetched_at": datetime.now().isoformat(),
        "total_articles": len(all_articles),
        "errors": errors,
        "categories": categorized
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
