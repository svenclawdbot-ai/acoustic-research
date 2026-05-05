#!/usr/bin/env python3
"""
Morning Brief RSS - WORLD, TECH, FINANCE
"""

import xml.etree.ElementTree as ET
import urllib.request
from datetime import datetime

FEEDS = {
    # WORLD
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Reuters World": "http://feeds.reuters.com/reuters/worldnews",
    "The Guardian World": "https://www.theguardian.com/world/rss",
    
    # TECH
    "Hacker News": "https://news.ycombinator.com/rss",
    "TechCrunch": "https://techcrunch.com/feed/",
    "Ars Technica": "http://feeds.arstechnica.com/arstechnica/index",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    
    # FINANCE
    "Financial Times": "https://www.ft.com/?format=rss",
    "Bloomberg Markets": "https://feeds.bloomberg.com/markets/news.rss",
    "Economist Finance": "https://www.economist.com/finance-and-economics/rss.xml",
}

def fetch_feed(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except:
        return None

def parse_rss(xml_content, max_items=3):
    if not xml_content:
        return []
    try:
        root = ET.fromstring(xml_content)
        items = []
        for item in root.findall('.//item'):
            title = item.find('title')
            link = item.find('link')
            if title is not None and link is not None:
                items.append({'title': title.text or '', 'link': link.text or ''})
            if len(items) >= max_items:
                break
        return items
    except:
        return []

def fetch_category(feed_names, items_per=3):
    stories = []
    for name in feed_names:
        if name in FEEDS:
            xml = fetch_feed(FEEDS[name])
            items = parse_rss(xml, max_items=items_per)
            stories.extend(items)
    return stories[:5]

def main():
    now = datetime.now().strftime('%A, %B %d, %Y')
    
    world = fetch_category(["BBC World", "Reuters World", "The Guardian World"], 2)
    tech = fetch_category(["Hacker News", "TechCrunch", "Ars Technica", "The Verge"], 2)
    finance = fetch_category(["Financial Times", "Bloomberg Markets", "Economist Finance"], 2)
    
    print(f"📰 Morning Brief — {now}")
    print()
    
    print("🌍 **WORLD**")
    for i, s in enumerate(world, 1):
        print(f"  {i}. {s['title'][:90]}{'...' if len(s['title']) > 90 else ''}")
    print()
    
    print("💻 **TECH**")
    for i, s in enumerate(tech, 1):
        print(f"  {i}. {s['title'][:90]}{'...' if len(s['title']) > 90 else ''}")
    print()
    
    print("💰 **FINANCE**")
    for i, s in enumerate(finance, 1):
        print(f"  {i}. {s['title'][:90]}{'...' if len(s['title']) > 90 else ''}")

if __name__ == "__main__":
    main()
