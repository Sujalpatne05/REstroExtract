"""
Unit tests for LoggerSystem module.

Tests logging at different levels, file creation, and summary generation.
"""

import os
import tempfile
import unittest
from pathlib import Path

from src.logger import LoggerSystem


class TestLoggerSystem(unittest.TestCase):
    """Test cases for LoggerSystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")
    
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
        
        # Clean up nested directories if they exist
        try:
            nested_dir = os.path.join(self.temp_dir, "nested", "dir")
            if os.path.exists(nested_dir):
                os.rmdir(nested_dir)
            nested_parent = os.path.join(self.temp_dir, "nested")
            if os.path.exists(nested_parent):
                os.rmdir(nested_parent)
        except (OSError, PermissionError):
            pass
        
        if os.path.exists(self.temp_dir):
            try:
                os.rmdir(self.temp_dir)
            except (OSError, PermissionError):
                pass
    
    def test_logger_initialization(self):
        """Test LoggerSystem initialization creates log file."""
        logger = LoggerSystem(self.log_file, log_level="INFO")
        self.assertIsNotNone(logger)
        self.assertEqual(logger.log_file, self.log_file)
        self.assertEqual(logger.log_level, "INFO")
    
    def test_log_file_creation(self):
        """Test that log file is created when logging."""
        logger = LoggerSystem(self.log_file, log_level="INFO")
        logger.info("Test message")
        self.assertTrue(os.path.exists(self.log_file))
    
    def test_info_logging(self):
        """Test info level logging."""
        logger = LoggerSystem(self.log_file, log_level="INFO")
        logger.info("Test info message")
        
        with open(self.log_file, 'r') as f:
            content = f.read()
        
        self.assertIn("Test info message", content)
        self.assertIn("[INFO]", content)
    
    def test_error_logging(self):
        """Test error level logging."""
        logger = LoggerSystem(self.log_file, log_level="INFO")
        logger.error("Test error message")
        
        with open(self.log_file, 'r') as f:
            content = f.read()
        
        self.assertIn("Test error message", content)
        self.assertIn("[ERROR]", content)
    
    def test_warning_logging(self):
        """Test warning level logging."""
        logger = LoggerSystem(self.log_file, log_level="INFO")
        logger.warning("Test warning message")
        
        with open(self.log_file, 'r') as f:
            content = f.read()
        
        self.assertIn("Test warning message", content)
        self.assertIn("[WARNING]", content)
    
    def test_debug_logging(self):
        """Test debug level logging."""
        logger = LoggerSystem(self.log_file, log_level="DEBUG")
        logger.debug("Test debug message")
        
        with open(self.log_file, 'r') as f:
            content = f.read()
        
        self.assertIn("Test debug message", content)
        self.assertIn("[DEBUG]", content)
    
    def test_debug_not_logged_at_info_level(self):
        """Test that debug messages are not logged at INFO level."""
        logger = LoggerSystem(self.log_file, log_level="INFO")
        logger.debug("Test debug message")
        
        with open(self.log_file, 'r') as f:
            content = f.read()
        
        self.assertNotIn("Test debug message", content)
    
    def test_logging_with_context(self):
        """Test logging with context dictionary."""
        logger = LoggerSystem(self.log_file, log_level="INFO")
        context = {"user": "test_user", "action": "test_action"}
        logger.info("Test message with context", context=context)
        
        with open(self.log_file, 'r') as f:
            content = f.read()
        
        self.assertIn("Test message with context", content)
        self.assertIn("Context:", content)
        self.assertIn("test_user", content)
        self.assertIn("test_action", content)
    
    def test_error_logging_with_exception(self):
        """Test error logging with exception."""
        logger = LoggerSystem(self.log_file, log_level="INFO")
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            logger.error("An error occurred", exception=e)
        
        with open(self.log_file, 'r') as f:
            content = f.read()
        
        self.assertIn("An error occurred", content)
        self.assertIn("ValueError", content)
        self.assertIn("Test exception", content)
    
    def test_generate_summary(self):
        """Test summary generation with statistics."""
        logger = LoggerSystem(self.log_file, log_level="INFO")
        stats = {
            "total_attempted": 100,
            "total_extracted": 95,
            "total_validated": 90,
            "total_rejected": 5,
            "total_duplicates_removed": 3,
            "extraction_status": "Success"
        }
        
        summary = logger.generate_summary(stats)
        
        self.assertIn("EXTRACTION SUMMARY", summary)
        self.assertIn("Total Records Attempted: 100", summary)
        self.assertIn("Total Records Extracted: 95", summary)
        self.assertIn("Total Records Validated: 90", summary)
        self.assertIn("Total Records Rejected: 5", summary)
        self.assertIn("Total Duplicates Removed: 3", summary)
        self.assertIn("Extraction Status: Success", summary)
    
    def test_generate_summary_with_missing_stats(self):
        """Test summary generation with missing statistics."""
        logger = LoggerSystem(self.log_file, log_level="INFO")
        stats = {
            "total_attempted": 50,
            "extraction_status": "Partial"
        }
        
        summary = logger.generate_summary(stats)
        
        self.assertIn("Total Records Attempted: 50", summary)
        self.assertIn("Total Records Extracted: 0", summary)
        self.assertIn("Extraction Status: Partial", summary)
    
    def test_log_directory_creation(self):
        """Test that log directory is created if it doesn't exist."""
        nested_log_file = os.path.join(self.temp_dir, "nested", "dir", "test.log")
        logger = LoggerSystem(nested_log_file, log_level="INFO")
        logger.info("Test message")
        
        self.assertTrue(os.path.exists(nested_log_file))
        
        # Close handlers to release file locks
        import logging
        nested_logger = logging.getLogger("FSSAI_Scraper")
        for handler in nested_logger.handlers[:]:
            handler.close()
            nested_logger.removeHandler(handler)
    
    def test_multiple_log_entries(self):
        """Test multiple log entries are all recorded."""
        logger = LoggerSystem(self.log_file, log_level="INFO")
        logger.info("First message")
        logger.warning("Second message")
        logger.error("Third message")
        
        with open(self.log_file, 'r') as f:
            content = f.read()
        
        self.assertIn("First message", content)
        self.assertIn("Second message", content)
        self.assertIn("Third message", content)
    
    def test_timestamp_in_log_entries(self):
        """Test that timestamps are included in log entries."""
        logger = LoggerSystem(self.log_file, log_level="INFO")
        logger.info("Test message")
        
        with open(self.log_file, 'r') as f:
            content = f.read()
        
        # Check for timestamp pattern (YYYY-MM-DD HH:MM:SS)
        self.assertRegex(content, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')


if __name__ == '__main__':
    unittest.main()
