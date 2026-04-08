#!/usr/bin/env python
"""
Find the FBO search endpoint using the gateway base URL
"""

import requests
import json

headers = {
    'User-Agent': 'FSSAI-Restaurant-Scraper/1.0',
    'Content-Type': 'application/json',
}

# Try different FBO endpoints with the gateway base URL
endpoints = [
    'https://foscos.fssai.gov.in/gateway/api/fbo/search',
    'https://foscos.fssai.gov.in/gateway/api/fbo/list',
    'https://foscos.fssai.gov.in/gateway/api/fbo/getAll',
    'https://foscos.fssai.gov.in/gateway/api/fbo',
    'https://foscos.fssai.gov.in/webgateway/api/fbo/search',
    'https://foscos.fssai.gov.in/webgateway/api/fbo/list',
    'https://foscos.fssai.gov.in/webgateway/api/fbo',
]

print("Testing FBO endpoints with gateway base URL...\n")

for endpoint in endpoints:
    print(f"Testing: {endpoint}")
    
    # Try GET
    try:
        resp = requests.get(endpoint, headers=headers, timeout=5)
        print(f"  GET Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  Response: {resp.text[:200]}")
    except Exception as e:
        print(f"  GET Error: {str(e)[:100]}")
    
    # Try POST with Maharashtra filter
    try:
        data = {
            'state': 'Maharashtra',
            'pageNo': 1,
            'pageSize': 100
        }
        resp = requests.post(endpoint, json=data, headers=headers, timeout=5)
        print(f"  POST Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  Response: {resp.text[:300]}")
    except Exception as e:
        print(f"  POST Error: {str(e)[:100]}")
    
    print()

# Also try with different search parameters
print("\n\nTrying with different search parameters...\n")

search_params = [
    {'state': 'Maharashtra'},
    {'state': 'Maharashtra', 'pageNo': 1, 'pageSize': 100},
    {'state': 'Maharashtra', 'limit': 100},
    {'state': 'Maharashtra', 'offset': 0},
]

for params in search_params:
    endpoint = 'https://foscos.fssai.gov.in/gateway/api/fbo/search'
    try:
        print(f"POST with params: {params}")
        resp = requests.post(endpoint, json=params, headers=headers, timeout=5)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            try:
                data = resp.json()
                print(f"  JSON Response: {json.dumps(data, indent=2)[:500]}")
            except:
                print(f"  Response: {resp.text[:300]}")
        else:
            print(f"  Response: {resp.text[:300]}")
    except Exception as e:
        print(f"  Error: {str(e)[:100]}")
    
    print()
