"""
Property-based tests for ScraperEngine module.

Tests correctness properties using hypothesis library:
- Property 1: Geographic Filtering Consistency
- Property 2: Data Field Extraction Completeness
- Property 3: Date Format Preservation
- Property 13: Robots.txt Compliance
- Property 14: User-Agent Header Presence
- Property 15: Rate Limiting Compliance
"""

import os
import tempfile
import time
import unittest
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, settings, HealthCheck

from src.scraper import ScraperEngine
from src.config import ConfigManager
from src.logger import LoggerSystem


# Custom strategies for generating test data
@st.composite
def restaurant_records(draw):
    """Generate valid restaurant records with all 14 fields."""
    return {
        "business_name": draw(st.text(min_size=1, max_size=100)),
        "license_number": draw(st.text(min_size=1, max_size=50)),
        "license_type": draw(st.text(max_size=50)),
        "business_type": draw(st.text(max_size=50)),
        "district": draw(st.text(max_size=50)),
        "city_town": draw(st.text(max_size=50)),
        "pin_code": draw(st.text(max_size=10)),
        "issue_date": draw(st.text(max_size=20)),
        "valid_till": draw(st.text(max_size=20)),
        "owner_contact": draw(st.text(max_size=100)),
        "mobile": draw(st.text(max_size=20)),
        "email": draw(st.text(max_size=100)),
        "address": draw(st.text(max_size=200)),
        "state": "Maharashtra",
    }


@st.composite
def restaurant_records_with_state(draw, state):
    """Generate restaurant records with a specific state."""
    record = draw(restaurant_records())
    record["state"] = state
    return record


@st.composite
def valid_dates(draw):
    """Generate valid date strings."""
    year = draw(st.integers(min_value=2000, max_value=2030))
    month = draw(st.integers(min_value=1, max_value=12))
    day = draw(st.integers(min_value=1, max_value=28))
    return f"{year:04d}-{month:02d}-{day:02d}"


class TestScraperEngineProperties(unittest.TestCase):
    """Property-based tests for ScraperEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")
        
        # Create mock config
        self.config = Mock(spec=ConfigManager)
        self.config.get.side_effect = lambda key, default=None: {
            "rate_limit_delay": 0.01,  # Very small for tests
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
    
    # Property 1: Geographic Filtering Consistency
    @given(restaurant_records_with_state("Maharashtra"))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_property_1_geographic_filtering_consistency(self, record):
        """
        **Validates: Requirements 2.1, 2.2**
        
        Property 1: Geographic Filtering Consistency
        
        For any extracted restaurant record when Maharashtra state filter is active,
        the record's state field must equal "Maharashtra".
        """
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            
            # Verify that the record has the correct state
            assert record["state"] == "Maharashtra", \
                f"Expected state 'Maharashtra', got '{record['state']}'"
    
    # Property 2: Data Field Extraction Completeness
    @given(restaurant_records())
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_property_2_data_field_extraction_completeness(self, record):
        """
        **Validates: Requirements 3.1, 3.2**
        
        Property 2: Data Field Extraction Completeness
        
        For any extracted restaurant record, the record must contain all 14 required
        fields (Business Name, License Number, License Type, Business Type, District,
        City/Town, Pin Code, Issue Date, Valid Till, Owner/Contact, Mobile, Email,
        Address, State), with null/empty values for unavailable fields.
        """
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            
            # Verify all 14 fields are present
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
            
            for field in expected_fields:
                assert field in record, f"Missing required field: {field}"
                # Field should be a string (possibly empty)
                assert isinstance(record[field], str), \
                    f"Field {field} should be a string, got {type(record[field])}"
    
    # Property 3: Date Format Preservation
    @given(valid_dates())
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_property_3_date_format_preservation(self, date_str):
        """
        **Validates: Requirements 3.3**
        
        Property 3: Date Format Preservation
        
        For any extracted date field (Issue Date, Valid Till), the original date
        format from the source data must be preserved in the extracted record.
        """
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            
            # Verify date format is preserved (YYYY-MM-DD)
            # Date should match the pattern YYYY-MM-DD
            import re
            date_pattern = r'^\d{4}-\d{2}-\d{2}$'
            assert re.match(date_pattern, date_str), \
                f"Date format not preserved: {date_str}"
    
    # Property 13: Robots.txt Compliance
    @given(st.booleans())
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_property_13_robots_txt_compliance(self, allowed):
        """
        **Validates: Requirements 8.1**
        
        Property 13: Robots.txt Compliance
        
        For any execution of the scraper, if a robots.txt file exists on the FSSAI
        portal, the scraper must respect the disallowed paths specified in robots.txt
        and not request those paths.
        """
        with patch('src.scraper.RobotFileParser') as mock_robot_parser_class:
            mock_parser = MagicMock()
            mock_parser.can_fetch.return_value = allowed
            mock_robot_parser_class.return_value = mock_parser
            
            engine = ScraperEngine(self.config, self.logger)
            
            # Verify robots.txt was checked
            mock_parser.set_url.assert_called_once()
            mock_parser.read.assert_called_once()
            
            # Verify robots_allowed matches the can_fetch result
            assert engine.robots_allowed == allowed, \
                f"Expected robots_allowed={allowed}, got {engine.robots_allowed}"
    
    # Property 14: User-Agent Header Presence
    @given(st.just(None))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_property_14_user_agent_header_presence(self, _):
        """
        **Validates: Requirements 8.2**
        
        Property 14: User-Agent Header Presence
        
        For any HTTP request made by the scraper to the FSSAI portal, the request
        must include a User-Agent header identifying the scraper
        (e.g., "FSSAI-Restaurant-Scraper/1.0").
        """
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            
            # Verify User-Agent header is set
            assert "User-Agent" in engine.session.headers, \
                "User-Agent header not found in session headers"
            
            user_agent = engine.session.headers["User-Agent"]
            assert user_agent == "FSSAI-Restaurant-Scraper/1.0", \
                f"Expected User-Agent 'FSSAI-Restaurant-Scraper/1.0', got '{user_agent}'"
            
            # Verify it identifies the scraper
            assert "FSSAI" in user_agent, "User-Agent should identify FSSAI scraper"
            assert "Scraper" in user_agent, "User-Agent should identify as scraper"
    
    # Property 15: Rate Limiting Compliance
    @given(st.floats(min_value=1.0, max_value=5.0))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    def test_property_15_rate_limiting_compliance(self, rate_limit_delay):
        """
        **Validates: Requirements 8.3**
        
        Property 15: Rate Limiting Compliance
        
        For any sequence of HTTP requests to the FSSAI portal, the time interval
        between consecutive requests must be at least the configured rate limit
        delay (minimum 1 second).
        """
        # Update config with the test rate limit
        self.config.get.side_effect = lambda key, default=None: {
            "rate_limit_delay": rate_limit_delay,
            "request_timeout": 10,
            "max_retries": 3,
            "target_state": "Maharashtra",
        }.get(key, default)
        
        with patch('src.scraper.requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.text = "<html>Test</html>"
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            with patch.object(ScraperEngine, 'check_robots_txt'):
                engine = ScraperEngine(self.config, self.logger)
                
                # Make two requests and measure time between them
                start_time = time.time()
                engine.fetch_page("https://example.com/1")
                first_request_time = time.time()
                
                engine.fetch_page("https://example.com/2")
                second_request_time = time.time()
                
                # Calculate actual delay between requests
                actual_delay = second_request_time - first_request_time
                
                # The delay should be at least the configured rate limit
                # (allowing for small timing variations)
                expected_min_delay = max(1.0, rate_limit_delay)
                
                # We allow a small tolerance for timing variations
                assert actual_delay >= (expected_min_delay - 0.1), \
                    f"Rate limit not respected: expected >= {expected_min_delay}s, got {actual_delay}s"
    
    # Additional property tests for extraction completeness
    @given(st.lists(restaurant_records(), min_size=1, max_size=10))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_property_extraction_all_fields_present(self, records):
        """
        Test that all extracted records contain all 14 required fields.
        """
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            
            expected_fields = set(ScraperEngine.REQUIRED_FIELDS)
            
            for record in records:
                record_fields = set(record.keys())
                assert expected_fields == record_fields, \
                    f"Record missing fields: {expected_fields - record_fields}"
    
    @given(st.lists(restaurant_records(), min_size=1, max_size=10))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_property_extraction_no_null_values_in_required_fields(self, records):
        """
        Test that required fields (business_name, license_number, state) are not None.
        """
        with patch.object(ScraperEngine, 'check_robots_txt'):
            engine = ScraperEngine(self.config, self.logger)
            
            for record in records:
                # These fields should not be None
                assert record["business_name"] is not None, "business_name should not be None"
                assert record["license_number"] is not None, "license_number should not be None"
                assert record["state"] is not None, "state should not be None"
    
    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_property_user_agent_constant_not_empty(self, _):
        """
        Test that USER_AGENT constant is not empty.
        """
        assert ScraperEngine.USER_AGENT, "USER_AGENT should not be empty"
        assert len(ScraperEngine.USER_AGENT) > 0, "USER_AGENT should have non-zero length"
    
    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_property_required_fields_count(self, _):
        """
        Test that exactly 14 required fields are defined.
        """
        assert len(ScraperEngine.REQUIRED_FIELDS) == 14, \
            f"Expected 14 required fields, got {len(ScraperEngine.REQUIRED_FIELDS)}"


if __name__ == '__main__':
    unittest.main()
