"""
Use Playwright to render the FSSAI portal and extract restaurant data
"""
import json
import time
from playwright.sync_api import sync_playwright

print('Scraping FSSAI Portal with Playwright (JavaScript Rendering)')
print('=' * 70)

try:
    with sync_playwright() as p:
        print('Launching browser...')
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print('Loading FSSAI portal...')
        page.goto('https://foscos.fssai.gov.in/fbo-search', timeout=60000, wait_until='networkidle')
        
        print('Page loaded. Waiting for content...')
        time.sleep(3)
        
        # Try to find and fill state input
        print('Looking for state input...')
        state_inputs = page.locator('input[placeholder*="state"], input[name*="state"], select')
        if state_inputs.count() > 0:
            print(f'Found {state_inputs.count()} input fields')
            # Try first input
            state_inputs.first.fill('Maharashtra')
            time.sleep(1)
        
        # Try to find search button
        print('Looking for search button...')
        buttons = page.locator('button')
        print(f'Found {buttons.count()} buttons')
        
        for i in range(min(5, buttons.count())):
            btn_text = buttons.nth(i).text_content()
            print(f'  Button {i}: {btn_text[:30]}')
            if 'search' in btn_text.lower():
                print(f'  Clicking search button...')
                buttons.nth(i).click()
                time.sleep(5)
                break
        
        # Try to extract table data
        print('Extracting restaurant data...')
        
        # Look for table
        tables = page.locator('table')
        print(f'Found {tables.count()} tables')
        
        if tables.count() > 0:
            rows = page.locator('table tbody tr')
            row_count = rows.count()
            print(f'Found {row_count} restaurant records')
            
            if row_count > 0:
                print('\nFirst 3 records:')
                for i in range(min(3, row_count)):
                    cells = rows.nth(i).locator('td')
                    cell_count = cells.count()
                    row_data = []
                    for j in range(cell_count):
                        text = cells.nth(j).text_content().strip()
                        row_data.append(text[:30])
                    print(f'  Record {i+1}: {row_data}')
        
        # Try to get data from page content
        print('\nSearching for data in page content...')
        content = page.content()
        
        # Look for JSON data in script tags
        if 'window.__INITIAL_STATE__' in content:
            print('Found initial state data')
        if 'restaurants' in content.lower():
            print('Found restaurant data in page')
        
        browser.close()
        print('\n✓ Scraping completed')
        
except Exception as e:
    print(f'\n✗ Error: {str(e)}')
    print('\nNote: This requires Playwright to be installed and working')
    print('Install with: pip install playwright')
    print('Then run: python -m playwright install chromium')
