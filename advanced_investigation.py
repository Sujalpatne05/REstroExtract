#!/usr/bin/env python
"""
Advanced investigation - intercept XHR requests and check JavaScript
"""

from playwright.sync_api import sync_playwright
import json
import time
import re

def advanced_investigation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Intercept XHR/Fetch requests specifically
        xhr_requests = []
        
        def handle_route(route):
            request = route.request
            resource_type = request.resource_type
            url = request.url
            
            # Capture XHR and fetch requests
            if resource_type in ['xhr', 'fetch']:
                xhr_requests.append({
                    'url': url,
                    'method': request.method,
                    'headers': dict(request.headers),
                })
                print(f"XHR: {request.method} {url}")
            
            route.continue_()
        
        page.route('**/*', handle_route)
        
        print("Loading FSSAI portal with XHR interception...\n")
        page.goto('https://foscos.fssai.gov.in/fbo-search', wait_until='networkidle', timeout=30000)
        
        # Wait for page to fully load
        page.wait_for_timeout(5000)
        
        print(f"\nTotal XHR requests: {len(xhr_requests)}")
        
        # Try to find the search form and interact with it
        print("\nLooking for form elements...")
        
        try:
            # Get all form elements
            forms = page.query_selector_all('form')
            print(f"Found {len(forms)} forms")
            
            # Get all input elements
            inputs = page.query_selector_all('input')
            print(f"Found {len(inputs)} inputs")
            
            # Get all select elements
            selects = page.query_selector_all('select')
            print(f"Found {len(selects)} selects")
            
            # Try to find elements by text
            buttons = page.query_selector_all('button')
            print(f"Found {len(buttons)} buttons")
            
            # Print button texts
            for i, btn in enumerate(buttons[:5]):
                try:
                    text = btn.text_content()
                    print(f"  Button {i}: {text}")
                except:
                    pass
        except Exception as e:
            print(f"Error finding elements: {e}")
        
        # Try to evaluate JavaScript to find API endpoints
        print("\nChecking for API endpoints in JavaScript...")
        
        try:
            # Look for API URLs in the page
            html = page.content()
            
            # Find all URLs that look like API endpoints
            api_urls = re.findall(r'["\']([^"\']*(?:api|gateway|search|fbo)[^"\']*)["\']', html, re.IGNORECASE)
            
            print(f"Found {len(set(api_urls))} potential API URLs:")
            for url in list(set(api_urls))[:10]:
                if url and len(url) < 200:
                    print(f"  {url}")
        except Exception as e:
            print(f"Error finding API URLs: {e}")
        
        # Try to find data in window object
        print("\nChecking window object for data...")
        
        try:
            # Get all properties of window
            result = page.evaluate('''() => {
                const keys = Object.keys(window).filter(k => 
                    !k.startsWith('webkit') && 
                    !k.startsWith('chrome') &&
                    k.length < 50
                );
                return keys.slice(0, 50);
            }''')
            
            print(f"Window properties: {result[:20]}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Try to find Angular app data
        print("\nChecking for Angular app data...")
        
        try:
            result = page.evaluate('''() => {
                if (window.ng) return "Angular detected";
                if (window.__INITIAL_STATE__) return "Initial state found";
                if (window.__data__) return "Data found";
                return "No Angular data found";
            }''')
            
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        browser.close()

if __name__ == '__main__':
    advanced_investigation()
