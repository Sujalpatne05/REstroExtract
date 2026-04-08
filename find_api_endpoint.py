#!/usr/bin/env python
"""
Find the actual API endpoint for restaurant data
"""

from playwright.sync_api import sync_playwright
import json
import time

def find_api():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Listen for all network requests
        api_requests = []
        
        def handle_route(route):
            request = route.request
            url = request.url
            
            # Capture API calls
            if '/api/' in url or '/gateway/' in url:
                api_requests.append({
                    'url': url,
                    'method': request.method,
                    'post_data': request.post_data
                })
            
            route.continue_()
        
        page.route('**/*', handle_route)
        
        print("Loading FSSAI portal...")
        page.goto('https://foscos.fssai.gov.in/fbo-search', wait_until='networkidle', timeout=30000)
        
        # Wait for page to fully load
        page.wait_for_timeout(3000)
        
        # Try to interact with the page - look for search button or form
        print("\nLooking for search elements...")
        
        # Try to find and click search button
        try:
            search_buttons = page.query_selector_all('button')
            print(f"Found {len(search_buttons)} buttons")
            
            # Try to find input fields
            inputs = page.query_selector_all('input')
            print(f"Found {len(inputs)} input fields")
            
            # Try to find select/dropdown elements
            selects = page.query_selector_all('select')
            print(f"Found {len(selects)} select elements")
        except:
            pass
        
        # Wait a bit more for any lazy-loaded content
        page.wait_for_timeout(2000)
        
        print("\n=== API Requests Made ===")
        for i, req in enumerate(api_requests):
            print(f"{i+1}. {req['method']} {req['url']}")
            if req['post_data']:
                print(f"   POST Data: {req['post_data'][:100]}")
        
        # Get page HTML to look for data
        html = page.content()
        
        # Look for any JSON data in the page
        if 'window.' in html:
            print("\n=== Found window objects ===")
            import re
            window_vars = re.findall(r'window\.(\w+)\s*=', html)
            for var in set(window_vars)[:10]:
                print(f"  window.{var}")
        
        # Look for data attributes
        if 'data-' in html:
            print("\n=== Found data attributes ===")
            import re
            data_attrs = re.findall(r'data-(\w+)', html)
            for attr in set(data_attrs)[:10]:
                print(f"  data-{attr}")
        
        browser.close()

if __name__ == '__main__':
    find_api()
