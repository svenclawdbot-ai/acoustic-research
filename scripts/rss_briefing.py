#!/usr/bin/env python3
"""
Lightweight RSS briefing tool
Fetches headlines from configured feeds
"""

import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
from datetime import datetime

FEEDS = {
    "Hacker News": "https://news.ycombinator.com/rss",
    "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
    "TechCrunch": "https://techcrunch.com/feed/",
    "The Guardian": "https://www.theguardian.com/uk/rss",
    "Ars Technica": "http://feeds.arstechnica.com/arstechnica/index",
}

def fetch_feed(url, timeout=10):
    """Fetch RSS feed content"""
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read()
    except Exception as e:
        return None

def parse_rss(xml_content, max_items=5):
    """Parse RSS XML and extract items"""
    if not xml_content:
        return []
    
    try:
        root = ET.fromstring(xml_content)
        items = []
        
        # Handle RSS 2.0
        for item in root.findall('.//item'):
            title = item.find('title')
            link = item.find('link')
            if title is not None and link is not None:
                items.append({
                    'title': title.text or '',
                    'link': link.text or ''
                })
            if len(items) >= max_items:
                break
        
        return items
    except ET.ParseError:
        return []

def get_briefing(feeds=None, items_per_feed=3):
    """Generate news briefing"""
    if feeds is None:
        feeds = ["Hacker News", "BBC News", "TechCrunch"]
    
    results = []
    results.append(f"📰 Morning Briefing — {datetime.now().strftime('%A, %B %d')}")
    results.append("")
    
    for feed_name in feeds:
        if feed_name not in FEEDS:
            continue
            
        url = FEEDS[feed_name]
        xml = fetch_feed(url)
        items = parse_rss(xml, max_items=items_per_feed)
        
        if items:
            results.append(f"**{feed_name}**")
            for i, item in enumerate(items, 1):
                title = item['title'][:80] + '...' if len(item['title']) > 80 else item['title']
                results.append(f"  {i}. {title}")
            results.append("")
    
    return '\n'.join(results)

if __name__ == "__main__":
    print(get_briefing())
