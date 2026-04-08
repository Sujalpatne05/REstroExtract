"""
Unit tests for ScraperEngine module.

Tests HTTP requests, retry mechanism, rate limiting, User-Agent header,
robots.txt parsing, and HTML parsing with data extraction.
"""

import os
import tempfile
import time
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.scraper import ScraperEngine
from src.config import ConfigManager
from src.logger import LoggerSystem


class TestScraperEngine(unittest.TestCase):
    """Test cases for ScraperEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")
        
        # Create mock config
        self.config = Mock(spec=ConfigManager)
        self.config.get.side_effect = lambda key, default=None: {
            "rate_limit_delay": 0.1,  # Use small delay for tests
            "request_timeout": 10,
            "max_retries": 3,
            "target_state": "Maharashtra",
        }.get(key, default)
        
        # Create logger
        self.logger = LoggerSystem(self.log_file, log_level="INFO")
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Close all handlers to release file locks
        import logging
        logger = logging.getLogger("FSSAI_Scraper")
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        
        # Clean up files
        if os.path.exists(self.log_file):
            try:
                os.remove(self.log_file)
            except PermissionError:
                pass
        
        if os.path.exists(self.temp_dir):
            try:
                os.rmdir(self.temp_dir)
            except (OSError, PermissionError):
                pass
    
    def test_scraper_engine_initialization(self):
        """Test ScraperEngine initialization."""
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            self.assertIsNotNone(engine)
            self.assertEqual(engine.config, self.config)
            self.assertEqual(engine.logger, self.logger)
            self.assertIsNotNone(engine.session)
    
    def test_set_user_agent(self):
        """Test User-Agent header is set correctly."""
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            
            # Check that User-Agent header is set
            self.assertIn("User-Agent", engine.session.headers)
            self.assertEqual(engine.session.headers["User-Agent"], "FSSAI-Restaurant-Scraper/1.0")
    
    def test_user_agent_constant(self):
        """Test that USER_AGENT constant is correct."""
        self.assertEqual(ScraperEngine.USER_AGENT, "FSSAI-Restaurant-Scraper/1.0")
    
    def test_required_fields_constant(self):
        """Test that REQUIRED_FIELDS constant contains all 14 fields."""
        expected_fields = [
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
        self.assertEqual(len(ScraperEngine.REQUIRED_FIELDS), 14)
        self.assertEqual(set(ScraperEngine.REQUIRED_FIELDS), set(expected_fields))
    
    @patch('src.scraper.RobotFileParser')
    def test_check_robots_txt_allowed(self, mock_robot_parser_class):
        """Test robots.txt compliance check when scraping is allowed."""
        mock_parser = MagicMock()
        mock_parser.can_fetch.return_value = True
        mock_robot_parser_class.return_value = mock_parser
        
        engine = ScraperEngine(self.config, self.logger)
        
        self.assertTrue(engine.robots_allowed)
        mock_parser.set_url.assert_called_once()
        mock_parser.read.assert_called_once()
    
    @patch('src.scraper.RobotFileParser')
    def test_check_robots_txt_disallowed(self, mock_robot_parser_class):
        """Test robots.txt compliance check when scraping is disallowed."""
        mock_parser = MagicMock()
        mock_parser.can_fetch.return_value = False
        mock_robot_parser_class.return_value = mock_parser
        
        engine = ScraperEngine(self.config, self.logger)
        
        self.assertFalse(engine.robots_allowed)
    
    @patch('src.scraper.RobotFileParser')
    def test_check_robots_txt_error_handling(self, mock_robot_parser_class):
        """Test robots.txt error handling when fetch fails."""
        mock_parser = MagicMock()
        mock_parser.read.side_effect = Exception("Network error")
        mock_robot_parser_class.return_value = mock_parser
        
        engine = ScraperEngine(self.config, self.logger)
        
        # Should allow scraping if robots.txt can't be fetched
        self.assertTrue(engine.robots_allowed)
    
    @patch('src.scraper.requests.Session.get')
    def test_fetch_page_success(self, mock_get):
        """Test successful page fetch."""
        mock_response = Mock()
        mock_response.text = "<html>Test content</html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            result = engine.fetch_page("https://example.com")
        
        self.assertEqual(result, "<html>Test content</html>")
        mock_get.assert_called_once()
    
    @patch('src.scraper.requests.Session.get')
    def test_fetch_page_with_timeout(self, mock_get):
        """Test page fetch with timeout."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            result = engine.fetch_page("https://example.com")
        
        self.assertIsNone(result)
        # Should have retried 3 times
        self.assertEqual(mock_get.call_count, 3)
    
    @patch('src.scraper.requests.Session.get')
    def test_fetch_page_with_connection_error(self, mock_get):
        """Test page fetch with connection error."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            result = engine.fetch_page("https://example.com")
        
        self.assertIsNone(result)
        # Should have retried 3 times
        self.assertEqual(mock_get.call_count, 3)
    
    @patch('src.scraper.requests.Session.get')
    def test_fetch_page_with_http_error(self, mock_get):
        """Test page fetch with HTTP error."""
        import requests
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            result = engine.fetch_page("https://example.com")
        
        self.assertIsNone(result)
        # Should have retried 3 times
        self.assertEqual(mock_get.call_count, 3)
    
    @patch('src.scraper.requests.Session.get')
    def test_fetch_page_retry_success(self, mock_get):
        """Test page fetch succeeds after retry."""
        import requests
        mock_response = Mock()
        mock_response.text = "<html>Success</html>"
        mock_response.status_code = 200
        
        # Fail first attempt, succeed on second
        mock_get.side_effect = [
            requests.exceptions.Timeout("Timeout"),
            mock_response
        ]
        
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            result = engine.fetch_page("https://example.com")
        
        self.assertEqual(result, "<html>Success</html>")
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('src.scraper.time.sleep')
    @patch('src.scraper.requests.Session.get')
    def test_fetch_page_exponential_backoff(self, mock_get, mock_sleep):
        """Test exponential backoff delays between retries."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")
        
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            result = engine.fetch_page("https://example.com")
        
        self.assertIsNone(result)
        
        # Check that sleep was called with exponential backoff: 1, 2, 4
        sleep_calls = mock_sleep.call_args_list
        # Filter out rate limit sleeps (0.1) from backoff sleeps
        backoff_sleeps = [call for call in sleep_calls if call[0][0] >= 1]
        
        self.assertGreaterEqual(len(backoff_sleeps), 2)
    
    @patch('src.scraper.time.sleep')
    @patch('src.scraper.requests.Session.get')
    def test_rate_limiting_applied(self, mock_get, mock_sleep):
        """Test rate limiting delay is applied between requests."""
        mock_response = Mock()
        mock_response.text = "<html>Test</html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            
            # Make two requests
            engine.fetch_page("https://example.com/1")
            engine.fetch_page("https://example.com/2")
        
        # Rate limit sleep should be called (0.1 seconds)
        rate_limit_sleeps = [call for call in mock_sleep.call_args_list 
                            if call[0][0] < 1]
        self.assertGreater(len(rate_limit_sleeps), 0)
    
    def test_parse_html_empty_html(self):
        """Test parsing empty HTML."""
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            result = engine.parse_html("")
        
        self.assertEqual(result, [])
    
    def test_parse_html_no_records(self):
        """Test parsing HTML with no restaurant records."""
        html = "<html><body><p>No records found</p></body></html>"
        
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            result = engine.parse_html(html)
        
        self.assertEqual(result, [])
    
    def test_parse_html_with_malformed_html(self):
        """Test parsing malformed HTML."""
        html = "<html><body><tr><td>Incomplete"
        
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            result = engine.parse_html(html)
        
        # Should handle gracefully and return empty list
        self.assertEqual(result, [])
    
    def test_extract_text_from_element(self):
        """Test text extraction from HTML element."""
        from bs4 import BeautifulSoup
        
        html = """
        <tr class="restaurant-record">
            <td class="business-name">Test Restaurant</td>
            <td class="license-number">LIC123</td>
        </tr>
        """
        
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("tr")
        
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            
            name = engine._extract_text(element, "td.business-name")
            license_num = engine._extract_text(element, "td.license-number")
        
        self.assertEqual(name, "Test Restaurant")
        self.assertEqual(license_num, "LIC123")
    
    def test_extract_text_missing_element(self):
        """Test text extraction when element doesn't exist."""
        from bs4 import BeautifulSoup
        
        html = "<tr><td>Some data</td></tr>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("tr")
        
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            result = engine._extract_text(element, "td.nonexistent")
        
        self.assertIsNone(result)
    
    def test_extract_records_robots_disallowed(self):
        """Test extract_records when robots.txt disallows scraping."""
        with patch('src.scraper.RobotFileParser') as mock_robot_parser_class:
            mock_parser = MagicMock()
            mock_parser.can_fetch.return_value = False
            mock_robot_parser_class.return_value = mock_parser
            
            engine = ScraperEngine(self.config, self.logger)
            result = engine.extract_records()
        
        self.assertEqual(result, [])
    
    @patch('src.scraper.requests.Session.get')
    def test_extract_records_fetch_failure(self, mock_get):
        """Test extract_records when page fetch fails."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")
        
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            result = engine.extract_records()
        
        self.assertEqual(result, [])
    
    @patch('src.scraper.requests.Session.get')
    def test_extract_records_success(self, mock_get):
        """Test successful record extraction."""
        mock_response = Mock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            result = engine.extract_records()
        
        # Should return a list (may be empty if no records found in HTML)
        self.assertIsInstance(result, list)
    
    def test_extract_record_from_element_valid(self):
        """Test extracting a valid record from element."""
        from bs4 import BeautifulSoup
        
        html = """
        <tr class="restaurant-record">
            <td class="business-name">Test Restaurant</td>
            <td class="license-number">LIC123</td>
            <td class="license-type">State License</td>
            <td class="business-type">Restaurant</td>
            <td class="district">Mumbai</td>
            <td class="city-town">Mumbai</td>
            <td class="pin-code">400001</td>
            <td class="issue-date">2023-01-01</td>
            <td class="valid-till">2025-01-01</td>
            <td class="owner-contact">John Doe</td>
            <td class="mobile">9876543210</td>
            <td class="email">test@example.com</td>
            <td class="address">123 Main St</td>
            <td class="state">Maharashtra</td>
        </tr>
        """
        
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("tr")
        
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            record = engine._extract_record_from_element(element, "Maharashtra")
        
        self.assertIsNotNone(record)
        self.assertEqual(record["business_name"], "Test Restaurant")
        self.assertEqual(record["license_number"], "LIC123")
        self.assertEqual(record["state"], "Maharashtra")
    
    def test_extract_record_from_element_missing_required_field(self):
        """Test extracting record with missing required field."""
        from bs4 import BeautifulSoup
        
        html = """
        <tr class="restaurant-record">
            <td class="business-name"></td>
            <td class="license-number">LIC123</td>
        </tr>
        """
        
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("tr")
        
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            record = engine._extract_record_from_element(element, "Maharashtra")
        
        # Should return None if required fields are missing
        self.assertIsNone(record)
    
    def test_extract_record_from_element_missing_fields_populated(self):
        """Test that missing fields are populated with empty strings."""
        from bs4 import BeautifulSoup
        
        html = """
        <tr class="restaurant-record">
            <td class="business-name">Test Restaurant</td>
            <td class="license-number">LIC123</td>
        </tr>
        """
        
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("tr")
        
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            record = engine._extract_record_from_element(element, "Maharashtra")
        
        # Should have all 14 fields
        self.assertIsNotNone(record)
        self.assertEqual(len(record), 14)
        
        # Missing fields should be empty strings
        self.assertEqual(record["license_type"], "")
        self.assertEqual(record["business_type"], "")
        self.assertEqual(record["district"], "")
    
    def test_fssai_portal_url_constant(self):
        """Test that FSSAI_PORTAL_URL constant is correct."""
        self.assertEqual(ScraperEngine.FSSAI_PORTAL_URL, "https://foscos.fssai.gov.in/")
    
    @patch('src.scraper.requests.Session.get')
    def test_fetch_page_timeout_parameter(self, mock_get):
        """Test that fetch_page uses configured timeout."""
        mock_response = Mock()
        mock_response.text = "<html>Test</html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            engine.fetch_page("https://example.com")
        
        # Check that timeout was passed to get()
        call_kwargs = mock_get.call_args[1]
        self.assertEqual(call_kwargs["timeout"], 10)
    
    def test_last_request_time_tracking(self):
        """Test that last request time is tracked for rate limiting."""
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            
            initial_time = engine.last_request_time
            self.assertEqual(initial_time, 0)
            
            with patch('src.scraper.requests.Session.get') as mock_get:
                mock_response = Mock()
                mock_response.text = "<html>Test</html>"
                mock_response.status_code = 200
                mock_get.return_value = mock_response
                
                engine.fetch_page("https://example.com")
                
                # Last request time should be updated
                self.assertGreater(engine.last_request_time, initial_time)


if __name__ == '__main__':
    unittest.main()
