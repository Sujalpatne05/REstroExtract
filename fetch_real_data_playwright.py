"""
Fetch real FSSAI data using Playwright to handle JavaScript rendering
"""
import json
import time
from playwright.sync_api import sync_playwright

print('Fetching FSSAI Restaurant Data (Real-time)')
print('=' * 70)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print('Opening FSSAI Portal...')
        page.goto('https://foscos.fssai.gov.in/fbo-search', timeout=30000)
        
        # Wait for page to load
        time.sleep(3)
        
        # Try to find search form
        print('Looking for search form...')
        
        # Try to find state dropdown
        try:
            state_input = page.locator('input[placeholder*="state"], select[name*="state"]')
            if state_input.count() > 0:
                print('Found state input field')
                state_input.first.fill('Maharashtra')
                time.sleep(1)
        except:
            print('Could not find state input')
        
        # Try to find search button
        try:
            search_btn = page.locator('button:has-text("Search"), button:has-text("search")')
            if search_btn.count() > 0:
                print('Found search button, clicking...')
                search_btn.first.click()
                time.sleep(5)
        except:
            print('Could not find search button')
        
        # Try to extract table data
        print('Extracting data...')
        
        # Get all table rows
        rows = page.locator('table tbody tr')
        row_count = rows.count()
        print(f'Found {row_count} rows')
        
        if row_count > 0:
            print('\nFirst 5 records:')
            for i in range(min(5, row_count)):
                cells = rows.nth(i).locator('td')
                cell_count = cells.count()
                row_data = []
                for j in range(cell_count):
                    row_data.append(cells.nth(j).text_content())
                print(f'Row {i+1}: {row_data[:5]}')
        
        # Try to get API response from network
        print('\nChecking network requests...')
        
        browser.close()
        
except Exception as e:
    print(f'Error: {str(e)}')
    print('\nNote: Playwright approach requires interactive browser rendering')
    print('This may not work in all environments')
