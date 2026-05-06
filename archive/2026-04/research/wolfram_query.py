#!/usr/bin/env python3
"""
Wolfram Alpha Query Tool
Simple wrapper for Wolfram Alpha API queries
Usage: python3 wolfram_query.py "integrate x^2 from 0 to 1"
"""

import sys
import urllib.parse
import urllib.request
import json
import os

# Get App ID from environment or config
WOLFRAM_APP_ID = os.environ.get('WOLFRAM_APP_ID', 'LHQJ395EVU')
WOLFRAM_API_URL = "https://api.wolframalpha.com/v1/result"

def query_wolfram(query):
    """Query Wolfram Alpha and return result."""
    if not WOLFRAM_APP_ID or WOLFRAM_APP_ID == 'YOUR_APP_ID':
        return "Error: WOLFRAM_APP_ID not set"
    
    encoded_query = urllib.parse.quote(query)
    url = f"{WOLFRAM_API_URL}?appid={WOLFRAM_APP_ID}&i={encoded_query}"
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        if e.code == 501:
            return "Wolfram Alpha: No short answer available for this query"
        return f"Error: {e.code} - {e.reason}"
    except Exception as e:
        return f"Error: {str(e)}"

def query_full(query):
    """Query Wolfram Alpha full API (JSON format)."""
    encoded_query = urllib.parse.quote(query)
    url = f"https://api.wolframalpha.com/v2/query?appid={WOLFRAM_APP_ID}&input={encoded_query}&format=plaintext&output=json"
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 wolfram_query.py 'your query here'")
        print("Examples:")
        print("  python3 wolfram_query.py 'integrate x^2 dx'")
        print("  python3 wolfram_query.py 'thermal conductivity of steel'")
        print("  python3 wolfram_query.py 'convert 500 watts to horsepower'")
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    result = query_wolfram(query)
    print(result)
