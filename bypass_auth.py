"""
Try multiple approaches to access FSSAI API without authentication
"""
import requests
import json
from bs4 import BeautifulSoup
import time

print('Attempting to access FSSAI API - Multiple Approaches')
print('=' * 70)

# Approach 1: Try with session cookies
print('\n[1] Trying with session cookies...')
try:
    session = requests.Session()
    # First visit the portal to get cookies
    session.get('https://foscos.fssai.gov.in/', timeout=10)
    time.sleep(1)
    
    # Then try API
    resp = session.get(
        'https://foscos.fssai.gov.in/gateway/api/fbo/search',
        params={'state': 'Maharashtra', 'pageNo': 1, 'pageSize': 50},
        timeout=10
    )
    print(f'Status: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'✓ SUCCESS! Got {len(data.get("data", []))} records')
except Exception as e:
    print(f'Failed: {str(e)[:60]}')

# Approach 2: Try with different User-Agent
print('\n[2] Trying with Chrome User-Agent...')
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://foscos.fssai.gov.in/fbo-search',
        'X-Requested-With': 'XMLHttpRequest'
    }
    resp = requests.get(
        'https://foscos.fssai.gov.in/gateway/api/fbo/search',
        params={'state': 'Maharashtra', 'pageNo': 1, 'pageSize': 50},
        headers=headers,
        timeout=10
    )
    print(f'Status: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'✓ SUCCESS! Got {len(data.get("data", []))} records')
except Exception as e:
    print(f'Failed: {str(e)[:60]}')

# Approach 3: Try webgateway endpoint
print('\n[3] Trying webgateway endpoint...')
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    resp = requests.get(
        'https://foscos.fssai.gov.in/webgateway/api/fbo/search',
        params={'state': 'Maharashtra', 'pageNo': 1, 'pageSize': 50},
        headers=headers,
        timeout=10
    )
    print(f'Status: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'✓ SUCCESS! Got {len(data.get("data", []))} records')
except Exception as e:
    print(f'Failed: {str(e)[:60]}')

# Approach 4: Try direct API without gateway
print('\n[4] Trying direct API endpoint...')
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    resp = requests.get(
        'https://foscos.fssai.gov.in/api/fbo/search',
        params={'state': 'Maharashtra', 'pageNo': 1, 'pageSize': 50},
        headers=headers,
        timeout=10
    )
    print(f'Status: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'✓ SUCCESS! Got {len(data.get("data", []))} records')
except Exception as e:
    print(f'Failed: {str(e)[:60]}')

# Approach 5: Try with Authorization header (empty token)
print('\n[5] Trying with Bearer token...')
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Authorization': 'Bearer '
    }
    resp = requests.get(
        'https://foscos.fssai.gov.in/gateway/api/fbo/search',
        params={'state': 'Maharashtra', 'pageNo': 1, 'pageSize': 50},
        headers=headers,
        timeout=10
    )
    print(f'Status: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'✓ SUCCESS! Got {len(data.get("data", []))} records')
except Exception as e:
    print(f'Failed: {str(e)[:60]}')

print('\n' + '=' * 70)
print('If all approaches failed, the API requires valid authentication.')
print('Alternative: Use mock data or official FSSAI FLRS portal')
