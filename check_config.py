#!/usr/bin/env python
"""
Check the configuration files to find API endpoints
"""

import requests
import json

headers = {
    'User-Agent': 'FSSAI-Restaurant-Scraper/1.0'
}

config_urls = [
    'https://foscos.fssai.gov.in/config/env.json',
    'https://foscos.fssai.gov.in/config/development.json',
    'https://foscos.fssai.gov.in/config/production.json',
]

print("Checking configuration files...\n")

for url in config_urls:
    try:
        print(f"Fetching: {url}")
        resp = requests.get(url, headers=headers, timeout=5)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                print(f"Config: {json.dumps(data, indent=2)}")
            except:
                print(f"Response: {resp.text[:500]}")
        
        print()
    except Exception as e:
        print(f"Error: {e}\n")

# Also check for common config locations
print("\n\nChecking for API base URL patterns...\n")

try:
    resp = requests.get('https://foscos.fssai.gov.in/config/env.json', headers=headers, timeout=5)
    if resp.status_code == 200:
        config = resp.json()
        print("Configuration found:")
        print(json.dumps(config, indent=2))
        
        # Look for API endpoints
        if 'apiUrl' in config:
            print(f"\nAPI URL: {config['apiUrl']}")
        if 'gatewayUrl' in config:
            print(f"Gateway URL: {config['gatewayUrl']}")
        if 'baseUrl' in config:
            print(f"Base URL: {config['baseUrl']}")
except Exception as e:
    print(f"Error: {e}")
