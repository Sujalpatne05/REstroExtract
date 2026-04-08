#!/usr/bin/env python
"""
Test common API endpoints for restaurant data
"""

import requests
import json

endpoints = [
    'https://foscos.fssai.gov.in/api/fbo/search',
    'https://foscos.fssai.gov.in/api/restaurants',
    'https://foscos.fssai.gov.in/api/licenses',
    'https://foscos.fssai.gov.in/gateway/api/fbo/search',
    'https://foscos.fssai.gov.in/gateway/api/restaurants',
    'https://foscos.fssai.gov.in/gateway/api/fbo',
]

headers = {
    'User-Agent': 'FSSAI-Restaurant-Scraper/1.0'
}

print("Testing API endpoints...\n")

for endpoint in endpoints:
    try:
        print(f'Testing: {endpoint}')
        resp = requests.get(endpoint, headers=headers, timeout=5)
        print(f'  Status: {resp.status_code}')
        
        if resp.status_code == 200:
            content_type = resp.headers.get('content-type', '')
            print(f'  Content-Type: {content_type}')
            print(f'  Length: {len(resp.text)}')
            
            if 'json' in content_type.lower():
                try:
                    data = resp.json()
                    print(f'  JSON Data: {str(data)[:300]}')
                except:
                    print(f'  Could not parse JSON')
            else:
                print(f'  Response: {resp.text[:200]}')
        
        print()
    except Exception as e:
        print(f'  Error: {str(e)}\n')

# Also try POST requests
print("\n\nTesting POST endpoints...\n")

post_endpoints = [
    ('https://foscos.fssai.gov.in/api/fbo/search', {'state': 'Maharashtra'}),
    ('https://foscos.fssai.gov.in/gateway/api/fbo/search', {'state': 'Maharashtra'}),
]

for endpoint, data in post_endpoints:
    try:
        print(f'POST to: {endpoint}')
        resp = requests.post(endpoint, json=data, headers=headers, timeout=5)
        print(f'  Status: {resp.status_code}')
        print(f'  Response: {resp.text[:300]}')
        print()
    except Exception as e:
        print(f'  Error: {str(e)}\n')
