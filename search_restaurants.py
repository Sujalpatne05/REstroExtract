#!/usr/bin/env python
"""
Search for restaurants on FSSAI portal and capture the API call
"""

from playwright.sync_api import sync_playwright
import json
import time

def search_restaurants():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Listen for all network requests
        api_requests = []
        
        def handle_route(route):
            request = route.request
            url = request.url
            
            # Capture all requests
            if '/api/' in url or '/gateway/' in url or 'search' in url.lower():
                api_requests.append({
                    'url': url,
                    'method': request.method,
                })
                print(f"API Call: {request.method} {url}")
            
            route.continue_()
        
        page.route('**/*', handle_route)
        
        print("Loading FSSAI portal...")
        page.goto('https://foscos.fssai.gov.in/fbo-search', wait_until='networkidle', timeout=30000)
        
        # Wait for page to fully load
        page.wait_for_timeout(3000)
        
        # Try to find the search form and submit it
        print("\nTrying to interact with search form...")
        
        # Look for any form or search mechanism
        try:
            # Try to find Maharashtra in the page
            page.fill('input', 'Maharashtra')
            page.wait_for_timeout(1000)
        except:
            pass
        
        # Try to find and click any button that might trigger search
        try:
            buttons = page.query_selector_all('button')
            if buttons:
                print(f"Clicking first button...")
                buttons[0].click()
                page.wait_for_timeout(3000)
        except:
            pass
        
        # Try pressing Enter
        try:
            page.press('input', 'Enter')
            page.wait_for_timeout(3000)
        except:
            pass
        
        # Check if any data appeared
        html = page.content()
        print(f"\nPage HTML length: {len(html)}")
        print(f"Contains 'restaurant': {'restaurant' in html.lower()}")
        print(f"Contains 'license': {'license' in html.lower()}")
        
        # Try to evaluate JavaScript to get data
        try:
            result = page.evaluate('() => window.__data__ || window.__state__ || {}')
            print(f"\nWindow data: {json.dumps(result, indent=2)[:500]}")
        except:
            pass
        
        browser.close()

if __name__ == '__main__':
    search_restaurants()
