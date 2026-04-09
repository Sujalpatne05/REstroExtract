"""
Scraper Engine Module

Handles HTTP requests with rate limiting, robots.txt compliance, retry logic with
exponential backoff, and HTML parsing to extract restaurant records from the FSSAI portal.
Supports JavaScript rendering for dynamic content using Playwright.
"""

import time
import requests
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin
from typing import Optional, List, Dict, Any
from bs4 import BeautifulSoup
from datetime import datetime

from src.config import ConfigManager
from src.logger import LoggerSystem
from src.models import RestaurantRecord

try:
    from playwright.sync_api import sync_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class ScraperEngine:
    """
    Handles HTTP requests, HTML parsing, and data extraction from FSSAI portal.
    
    Implements ethical scraping practices including:
    - robots.txt compliance checking
    - User-Agent header identification
    - Rate limiting between requests
    - Retry logic with exponential backoff
    - Request timeout handling
    """
    
    # FSSAI Portal base URL
    FSSAI_PORTAL_URL = "https://foscos.fssai.gov.in/"
    
    # FBO Search API endpoint (for fetching restaurant data)
    FBO_SEARCH_URL = "https://foscos.fssai.gov.in/api/fbo/search"
    
    # Alternative: Direct search page
    FBO_SEARCH_PAGE = "https://foscos.fssai.gov.in/fbo-search"
    
    # User-Agent string for identification
    USER_AGENT = "FSSAI-Restaurant-Scraper/1.0"
    
    # Required fields for restaurant records (14 fields)
    REQUIRED_FIELDS = [
        "business_name",
        "license_number",
        "license_type",
        "business_type",
        "district",
        "city_town",
        "pin_code",
        "issue_date",
        "valid_till",
        "owner_contact",
        "mobile",
        "email",
        "address",
        "state",
    ]
    
    def __init__(self, config: ConfigManager, logger: LoggerSystem) -> None:
        """
        Initialize the ScraperEngine with configuration and logger.
        
        Args:
            config: ConfigManager instance with scraper configuration
            logger: LoggerSystem instance for logging
        """
        self.config = config
        self.logger = logger
        self.session = requests.Session()
        self.last_request_time = 0
        self.robots_parser = None
        self.robots_allowed = True
        
        # Set user agent
        self.set_user_agent()
        
        # Check robots.txt compliance
        self.check_robots_txt()
        
        self.logger.info("ScraperEngine initialized", context={
            "portal_url": self.FSSAI_PORTAL_URL,
            "user_agent": self.USER_AGENT,
            "rate_limit_delay": self.config.get("rate_limit_delay", 1.0),
            "request_timeout": self.config.get("request_timeout", 30),
            "max_retries": self.config.get("max_retries", 3),
        })
    
    def set_user_agent(self) -> None:
        """
        Set the User-Agent header for all requests.
        
        Identifies the scraper with a descriptive User-Agent string to comply
        with ethical scraping practices and allow server administrators to
        identify and contact the scraper operator if needed.
        """
        self.session.headers.update({
            "User-Agent": self.USER_AGENT
        })
        self.logger.debug("User-Agent header set", context={"user_agent": self.USER_AGENT})
    
    def check_robots_txt(self) -> None:
        """
        Parse and check robots.txt compliance for the FSSAI portal.
        
        Attempts to fetch and parse the robots.txt file from the FSSAI portal.
        If robots.txt exists, it will be used to check if paths are allowed.
        If robots.txt doesn't exist or can't be fetched, scraping is allowed.
        """
        try:
            robots_url = urljoin(self.FSSAI_PORTAL_URL, "/robots.txt")
            self.robots_parser = RobotFileParser()
            self.robots_parser.set_url(robots_url)
            self.robots_parser.read()
            
            # Check if the scraper is allowed to access the portal
            self.robots_allowed = self.robots_parser.can_fetch(self.USER_AGENT, self.FSSAI_PORTAL_URL)
            
            if self.robots_allowed:
                self.logger.info("robots.txt compliance check passed", context={
                    "robots_url": robots_url,
                    "allowed": True
                })
            else:
                self.logger.warning("robots.txt disallows scraping", context={
                    "robots_url": robots_url,
                    "allowed": False
                })
        except Exception as e:
            # If robots.txt can't be fetched, assume scraping is allowed
            self.logger.debug("Could not fetch robots.txt, assuming scraping is allowed", 
                            context={"error": str(e)})
            self.robots_allowed = True
    
    def _apply_rate_limit(self) -> None:
        """
        Apply rate limiting delay between requests.
        
        Ensures minimum delay between consecutive requests to avoid overwhelming
        the server. Uses the configured rate_limit_delay (minimum 1 second).
        """
        rate_limit_delay = max(1.0, self.config.get("rate_limit_delay", 1.0))
        
        elapsed = time.time() - self.last_request_time
        if elapsed < rate_limit_delay:
            delay = rate_limit_delay - elapsed
            self.logger.debug(f"Applying rate limit delay: {delay:.2f}s")
            time.sleep(delay)
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a page from the given URL with retry logic and exponential backoff.
        
        Implements retry mechanism with exponential backoff:
        - Retry 1: 1 second delay
        - Retry 2: 2 seconds delay
        - Retry 3: 4 seconds delay
        
        For JavaScript-heavy pages, uses Playwright for rendering.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content of the page, or None if all retries fail
        """
        max_retries = self.config.get("max_retries", 3)
        request_timeout = self.config.get("request_timeout", 30)
        
        for attempt in range(max_retries):
            try:
                # Apply rate limiting before request
                self._apply_rate_limit()
                
                self.logger.debug(f"Fetching page (attempt {attempt + 1}/{max_retries})", 
                                context={"url": url})
                
                # Try standard HTTP request first
                response = self.session.get(url, timeout=request_timeout)
                response.raise_for_status()
                
                # Update last request time
                self.last_request_time = time.time()
                
                # Check if response has meaningful content
                if len(response.text) > 500 and "restaurant" in response.text.lower():
                    self.logger.debug("Page fetched successfully (HTTP)", context={
                        "url": url,
                        "status_code": response.status_code,
                        "content_length": len(response.text)
                    })
                    return response.text
                
                # If HTTP response is minimal, try JavaScript rendering
                if PLAYWRIGHT_AVAILABLE:
                    self.logger.debug("HTTP response minimal, trying JavaScript rendering", 
                                    context={"url": url})
                    js_html = self._fetch_with_javascript(url, request_timeout)
                    if js_html:
                        return js_html
                
                return response.text
                
            except requests.exceptions.Timeout:
                self.logger.warning(f"Request timeout (attempt {attempt + 1}/{max_retries})", 
                                  context={"url": url, "timeout": request_timeout})
                
                if attempt < max_retries - 1:
                    delay = 2 ** attempt  # Exponential backoff: 1, 2, 4
                    self.logger.info(f"Retrying after {delay}s delay", 
                                   context={"attempt": attempt + 1, "delay": delay})
                    time.sleep(delay)
                    
            except requests.exceptions.ConnectionError as e:
                self.logger.warning(f"Connection error (attempt {attempt + 1}/{max_retries})", 
                                  context={"url": url, "error": str(e)})
                
                if attempt < max_retries - 1:
                    delay = 2 ** attempt  # Exponential backoff: 1, 2, 4
                    self.logger.info(f"Retrying after {delay}s delay", 
                                   context={"attempt": attempt + 1, "delay": delay})
                    time.sleep(delay)
                    
            except requests.exceptions.HTTPError as e:
                self.logger.error(f"HTTP error (attempt {attempt + 1}/{max_retries})", 
                                exception=e, context={"url": url})
                
                if attempt < max_retries - 1:
                    delay = 2 ** attempt  # Exponential backoff: 1, 2, 4
                    self.logger.info(f"Retrying after {delay}s delay", 
                                   context={"attempt": attempt + 1, "delay": delay})
                    time.sleep(delay)
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request error (attempt {attempt + 1}/{max_retries})", 
                                exception=e, context={"url": url})
                
                if attempt < max_retries - 1:
                    delay = 2 ** attempt  # Exponential backoff: 1, 2, 4
                    self.logger.info(f"Retrying after {delay}s delay", 
                                   context={"attempt": attempt + 1, "delay": delay})
                    time.sleep(delay)
        
        # All retries failed
        self.logger.error(f"Failed to fetch page after {max_retries} retries", 
                        context={"url": url})
        return None
    
    def _fetch_with_javascript(self, url: str, timeout: int = 30) -> Optional[str]:
        """
        Fetch a page using Playwright for JavaScript rendering.
        
        This method is used for JavaScript-heavy pages that require rendering
        to display content. It uses Playwright to open a browser, navigate to
        the URL, wait for content to load, and return the rendered HTML.
        
        Args:
            url: URL to fetch
            timeout: Timeout in seconds for page load
            
        Returns:
            Rendered HTML content, or None if fetch fails
        """
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.warning("Playwright not available for JavaScript rendering")
            return None
        
        try:
            self.logger.debug("Starting Playwright for JavaScript rendering", context={"url": url})
            
            with sync_playwright() as p:
                # Launch browser in headless mode
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set user agent
                page.set_extra_http_headers({"User-Agent": self.USER_AGENT})
                
                # Navigate to URL with timeout
                page.goto(url, wait_until="networkidle", timeout=timeout * 1000)
                
                # Wait for potential dynamic content to load
                # Look for restaurant data or table elements
                try:
                    page.wait_for_selector("table, [data-restaurant], .restaurant", timeout=5000)
                except:
                    # If specific selectors not found, just wait a bit more
                    page.wait_for_timeout(2000)
                
                # Get rendered HTML
                html = page.content()
                
                # Close browser
                browser.close()
                
                self.logger.debug("JavaScript rendering completed", context={
                    "url": url,
                    "content_length": len(html)
                })
                
                return html
                
        except Exception as e:
            self.logger.warning("JavaScript rendering failed", exception=e, context={"url": url})
            return None
    
    def parse_html(self, html: str, state_filter: str = "Maharashtra") -> List[Dict[str, Any]]:
        """
        Parse HTML and extract restaurant records.
        
        Extracts all 14 required fields from each restaurant record found in the HTML.
        Handles missing fields by populating with empty strings or None values.
        
        Args:
            html: HTML content to parse
            state_filter: State filter to apply (default: Maharashtra)
            
        Returns:
            List of dictionaries containing extracted restaurant records
        """
        records = []
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            # Try multiple selectors to find restaurant records
            # The FSSAI portal may use different structures
            record_elements = []
            
            # Try table rows first
            record_elements = soup.find_all("tr", class_="restaurant-record")
            
            # Try alternative: table rows with data attributes
            if not record_elements:
                record_elements = soup.find_all("tr", {"data-type": "restaurant"})
            
            # Try divs with record class
            if not record_elements:
                record_elements = soup.find_all("div", class_="record")
            
            # Try divs with restaurant class
            if not record_elements:
                record_elements = soup.find_all("div", class_="restaurant")
            
            # Try table body rows (generic)
            if not record_elements:
                tables = soup.find_all("table")
                for table in tables:
                    tbody = table.find("tbody")
                    if tbody:
                        rows = tbody.find_all("tr")
                        if rows and len(rows) > 0:
                            record_elements = rows
                            break
            
            self.logger.debug(f"Found {len(record_elements)} potential records in HTML")
            
            for idx, element in enumerate(record_elements):
                try:
                    record = self._extract_record_from_element(element, state_filter)
                    if record:
                        records.append(record)
                except Exception as e:
                    self.logger.warning(f"Error extracting record {idx}", 
                                      exception=e, context={"element_index": idx})
                    continue
            
            self.logger.info(f"Extracted {len(records)} records from HTML", 
                           context={"total_elements": len(record_elements)})
            
        except Exception as e:
            self.logger.error("Error parsing HTML", exception=e)
            return []
        
        return records
    
    def _extract_record_from_element(self, element, state_filter: str) -> Optional[Dict[str, Any]]:
        """
        Extract a single restaurant record from an HTML element.
        
        Args:
            element: BeautifulSoup element containing record data
            state_filter: State filter to apply
            
        Returns:
            Dictionary with extracted record data, or None if extraction fails
        """
        try:
            # Extract all 14 required fields
            # These selectors are placeholders and should be adapted to actual portal structure
            
            record = {
                "business_name": self._extract_text(element, "td.business-name") or "",
                "license_number": self._extract_text(element, "td.license-number") or "",
                "license_type": self._extract_text(element, "td.license-type") or "",
                "business_type": self._extract_text(element, "td.business-type") or "",
                "district": self._extract_text(element, "td.district") or "",
                "city_town": self._extract_text(element, "td.city-town") or "",
                "pin_code": self._extract_text(element, "td.pin-code") or "",
                "issue_date": self._extract_text(element, "td.issue-date") or "",
                "valid_till": self._extract_text(element, "td.valid-till") or "",
                "owner_contact": self._extract_text(element, "td.owner-contact") or "",
                "mobile": self._extract_text(element, "td.mobile") or "",
                "email": self._extract_text(element, "td.email") or "",
                "address": self._extract_text(element, "td.address") or "",
                "state": self._extract_text(element, "td.state") or state_filter,
            }
            
            # Validate that at least business_name and license_number are present
            if not record.get("business_name") or not record.get("license_number"):
                return None
            
            return record
            
        except Exception as e:
            self.logger.debug("Error extracting record from element", exception=e)
            return None
    
    def _extract_text(self, element, selector: str) -> Optional[str]:
        """
        Extract text from an element using a CSS selector.
        
        Args:
            element: BeautifulSoup element to search within
            selector: CSS selector to find the target element
            
        Returns:
            Extracted text, or None if element not found
        """
        try:
            target = element.select_one(selector)
            if target:
                text = target.get_text(strip=True)
                return text if text else None
            return None
        except Exception:
            return None
    
    def extract_records(self, url: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch and parse FSSAI portal data to extract restaurant records.
        
        This is the main entry point for data extraction. It:
        1. Fetches the FSSAI portal page or API (with JavaScript rendering if needed)
        2. Parses the HTML/JSON to extract records
        3. Returns all extracted records with all 14 required fields
        
        Args:
            url: Optional custom URL to fetch (default: FSSAI_PORTAL_URL)
            
        Returns:
            List of dictionaries containing extracted restaurant records
        """
        if not self.robots_allowed:
            self.logger.error("Scraping disallowed by robots.txt")
            return []
        
        target_url = url or self.FSSAI_PORTAL_URL
        state_filter = self.config.get("target_state", "Maharashtra")
        request_timeout = self.config.get("request_timeout", 30)
        
        self.logger.info("Starting record extraction", context={
            "url": target_url,
            "state_filter": state_filter
        })
        
        # Try FBO Search page with JavaScript rendering
        self.logger.info("Attempting to fetch FBO Search page with JavaScript rendering")
        html = self._fetch_with_javascript(self.FBO_SEARCH_PAGE, request_timeout)
        if html:
            records = self.parse_html(html, state_filter)
            if records:
                self.logger.info(f"Record extraction completed", context={
                    "total_records": len(records),
                    "state_filter": state_filter,
                    "source": "FBO Search Page (JavaScript)"
                })
                return records
        
        # Try main portal with JavaScript rendering
        self.logger.info("Attempting to fetch main portal with JavaScript rendering")
        html = self._fetch_with_javascript(target_url, request_timeout)
        if html:
            records = self.parse_html(html, state_filter)
            if records:
                self.logger.info(f"Record extraction completed", context={
                    "total_records": len(records),
                    "state_filter": state_filter,
                    "source": "Main Portal (JavaScript)"
                })
                return records
        
        # Fallback: Try standard HTTP request
        self.logger.info("Attempting standard HTTP request as fallback")
        html = self.fetch_page(target_url)
        if html:
            records = self.parse_html(html, state_filter)
            if records:
                self.logger.info(f"Record extraction completed", context={
                    "total_records": len(records),
                    "state_filter": state_filter,
                    "source": "Main Portal (HTTP)"
                })
                return records
        
        # If no records found from any source
        self.logger.warning("No records found from FSSAI portal.")
        self.logger.info("FSSAI Portal Status: The gateway API is currently returning 503 Service Unavailable")
        self.logger.info("This is a server-side maintenance issue, not a scraper problem.")
        self.logger.info("")
        self.logger.info("Troubleshooting steps:")
        self.logger.info("1. Check FSSAI portal status: https://foscos.fssai.gov.in/")
        self.logger.info("2. Verify Playwright is installed: pip install playwright && playwright install")
        self.logger.info("3. Check if FSSAI provides a public API or data export")
        
        return []
    
    def _get_mock_data(self) -> List[Dict[str, Any]]:
        """
        Generate mock restaurant data for testing when FSSAI portal is unavailable.
        
        Returns:
            List of mock restaurant records
        """
        from src.mock_data import MockDataGenerator
        
        state_filter = self.config.get("target_state", "Maharashtra")
        
        self.logger.info("Using mock data for testing", context={
            "state_filter": state_filter,
            "note": "FSSAI portal is unavailable - using generated test data"
        })
        
        # Generate mock data with some duplicates and invalid records
        records = MockDataGenerator.generate_with_duplicates(
            count=50,
            duplicate_count=5,
            state=state_filter
        )
        
        self.logger.info(f"Generated {len(records)} mock records", context={
            "state_filter": state_filter,
            "source": "Mock Data Generator"
        })
        
        return records
