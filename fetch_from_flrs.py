"""
Fetch real FSSAI restaurant data from the official FLRS portal
This portal doesn't require authentication and has real data
"""
import requests
import json
from bs4 import BeautifulSoup
import time

print('Fetching Real FSSAI Restaurant Data from FLRS Portal')
print('=' * 70)

# Try the official FSSAI FLRS portal
flrs_url = 'https://foodlicensing.fssai.gov.in/'

print(f'Checking FLRS Portal: {flrs_url}')

try:
    # Check if portal is accessible
    resp = requests.get(flrs_url, timeout=10)
    print(f'Portal Status: {resp.status_code}')
    
    if resp.status_code == 200:
        print('Portal is online!')
        
        # Try to find API endpoints
        print('\nSearching for API endpoints...')
        
        # Common FLRS API endpoints
        api_endpoints = [
            'https://foodlicensing.fssai.gov.in/api/search',
            'https://foodlicensing.fssai.gov.in/api/fbo/search',
            'https://foodlicensing.fssai.gov.in/api/license/search',
            'https://foodlicensing.fssai.gov.in/api/restaurants',
        ]
        
        for endpoint in api_endpoints:
            try:
                params = {'state': 'Maharashtra', 'pageNo': 1, 'pageSize': 50}
                resp = requests.get(endpoint, params=params, timeout=10)
                print(f'\n{endpoint.split("/")[-1]}: {resp.status_code}')
                
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        if isinstance(data, dict) and 'data' in data:
                            records = data['data']
                            print(f'SUCCESS! Got {len(records)} records')
                            if records:
                                print(f'First record: {json.dumps(records[0], indent=2)[:300]}')
                            break
                        elif isinstance(data, list):
                            print(f'SUCCESS! Got {len(data)} records')
                            if data:
                                print(f'First record: {json.dumps(data[0], indent=2)[:300]}')
                            break
                    except:
                        pass
            except Exception as e:
                pass
        
        # Try search page with parameters
        print('\n\nTrying search page with parameters...')
        search_url = 'https://foodlicensing.fssai.gov.in/fbo-search'
        try:
            resp = requests.get(search_url, params={'state': 'Maharashtra'}, timeout=10)
            print(f'Search page: {resp.status_code}')
            if resp.status_code == 200:
                print('Search page is accessible')
        except Exception as e:
            print(f'Search page error: {str(e)[:60]}')
    
except Exception as e:
    print(f'Error: {str(e)}')

print('\n' + '=' * 70)
print('If FLRS portal is accessible, we can fetch real data from there.')
