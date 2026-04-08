#!/usr/bin/env python
"""
Investigate FSSAI portal structure to find API endpoints and data format
"""

from playwright.sync_api import sync_playwright
import json
import time

def investigate_portal():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Intercept network requests
        requests_made = []
        responses_data = []
        
        def handle_route(route):
            request = route.request
            requests_made.append({
                'url': request.url,
                'method': request.method,
                'headers': dict(request.headers)
            })
            
            response = route.fetch()
            if 'api' in request.url.lower() or 'search' in request.url.lower():
                try:
                    text = response.text()
                    responses_data.append({
                        'url': request.url,
                        'status': response.status,
                        'content_type': response.headers.get('content-type', ''),
                        'body_preview': text[:500] if text else ''
                    })
                except:
                    pass
            
            route.fulfill(response=response)
        
        page.route('**/*', handle_route)
        
        print("Navigating to FSSAI portal...")
        page.goto('https://foscos.fssai.gov.in/fbo-search', wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(5000)
        
        print("\n=== API Calls Found ===")
        api_calls = [r for r in requests_made if 'api' in r['url'].lower()]
        for i, call in enumerate(api_calls[:15]):
            print(f"{i+1}. {call['method']} {call['url']}")
        
        print("\n=== API Responses ===")
        for resp in responses_data[:5]:
            print(f"\nURL: {resp['url']}")
            print(f"Status: {resp['status']}")
            print(f"Content-Type: {resp['content_type']}")
            print(f"Body Preview: {resp['body_preview']}")
        
        # Check page content
        html = page.content()
        print(f"\n=== Page Analysis ===")
        print(f"Total HTML length: {len(html)}")
        print(f"Contains 'restaurant': {'restaurant' in html.lower()}")
        print(f"Contains 'license': {'license' in html.lower()}")
        print(f"Contains 'Maharashtra': {'Maharashtra' in html}")
        print(f"Contains 'FBO': {'FBO' in html}")
        print(f"Contains 'fbo': {'fbo' in html}")
        
        # Try to find data in page
        if '<table' in html:
            print("Contains table elements: Yes")
        if 'ng-app' in html or '_ngcontent' in html:
            print("Angular app detected: Yes")
        
        browser.close()

if __name__ == '__main__':
    investigate_portal()
