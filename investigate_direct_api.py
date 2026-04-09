"""
Investigate the direct API endpoint that returned 200
"""
import requests
import json

print('Investigating Direct API Endpoint')
print('=' * 70)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}

# Try different parameter combinations
test_cases = [
    {'state': 'Maharashtra'},
    {'state': 'Maharashtra', 'pageNo': 1},
    {'state': 'Maharashtra', 'pageNo': 1, 'pageSize': 50},
    {'state': 'Maharashtra', 'pageNo': 0, 'pageSize': 100},
    {'state': 'Maharashtra', 'page': 1, 'limit': 50},
    {'state': 'Maharashtra', 'offset': 0, 'limit': 50},
    {},
    {'pageNo': 1, 'pageSize': 50},
]

for i, params in enumerate(test_cases, 1):
    try:
        resp = requests.get(
            'https://foscos.fssai.gov.in/api/fbo/search',
            params=params,
            headers=headers,
            timeout=10
        )
        print(f'\n[Test {i}] Params: {params}')
        print(f'Status: {resp.status_code}')
        print(f'Content-Length: {len(resp.text)}')
        
        if resp.text:
            try:
                data = resp.json()
                print(f'Response type: {type(data)}')
                if isinstance(data, dict):
                    print(f'Keys: {list(data.keys())[:5]}')
                    if 'data' in data:
                        print(f'Records: {len(data["data"])}')
                elif isinstance(data, list):
                    print(f'Array length: {len(data)}')
                    if data:
                        print(f'First item: {json.dumps(data[0], indent=2)[:200]}')
            except:
                print(f'Response (first 200 chars): {resp.text[:200]}')
        else:
            print('Empty response')
    except Exception as e:
        print(f'[Test {i}] Error: {str(e)[:60]}')

print('\n' + '=' * 70)
