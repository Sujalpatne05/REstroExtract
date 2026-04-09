import requests
import json

print('Checking FSSAI Portal - LIVE STATUS')
print('=' * 70)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Referer': 'https://foscos.fssai.gov.in/'
}

# Try to get real data
endpoints = [
    'https://foscos.fssai.gov.in/gateway/api/fbo/search',
    'https://foscos.fssai.gov.in/webgateway/api/fbo/search',
]

for endpoint in endpoints:
    try:
        params = {'state': 'Maharashtra', 'pageNo': 1, 'pageSize': 50}
        resp = requests.get(endpoint, params=params, headers=headers, timeout=10)
        ep_name = endpoint.split('/')[-2]
        print(f'\n{ep_name}: Status {resp.status_code}')
        
        if resp.status_code == 200:
            data = resp.json()
            records = data.get('data', [])
            print(f'✓ SUCCESS! Got {len(records)} restaurant records')
            if records:
                print(f'\nFirst record sample:')
                print(json.dumps(records[0], indent=2)[:500])
            break
        elif resp.status_code == 401:
            print('✗ Authentication required (401)')
        elif resp.status_code == 503:
            print('✗ Service unavailable (503) - Still under maintenance')
        else:
            print(f'Response: {resp.text[:100]}')
    except Exception as e:
        ep_name = endpoint.split('/')[-2]
        print(f'{ep_name}: ERROR - {str(e)[:60]}')

print('\n' + '=' * 70)
