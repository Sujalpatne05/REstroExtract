"""
Logger System Module

Provides centralized logging with structured output to both file and console.
Includes timestamp, level, component, and context in log entries.
"""

import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any


class LoggerSystem:
    """
    Centralized logging system with file and console output.
    
    Supports structured logging with timestamp, level, component, and context.
    Log entries follow the format: [TIMESTAMP] [LEVEL] [COMPONENT] Message | Context: {...}
    """
    
    def __init__(self, log_file: str, log_level: str = "INFO") -> None:
        """
        Initialize the LoggerSystem with file and console output.
        
        Args:
            log_file: Path to the log file
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_file = log_file
        self.log_level = log_level
        self.logger = logging.getLogger("FSSAI_Scraper")
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Set logger level
        level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _format_context(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Format context dictionary as a string.
        
        Args:
            context: Dictionary of context information
            
        Returns:
            Formatted context string
        """
        if not context:
            return ""
        return f" | Context: {context}"
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an info level message.
        
        Args:
            message: The message to log
            context: Optional context dictionary
        """
        formatted_message = message + self._format_context(context)
        self.logger.info(formatted_message)
    
    def error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an error level message.
        
        Args:
            message: The message to log
            exception: Optional exception object
            context: Optional context dictionary
        """
        formatted_message = message + self._format_context(context)
        if exception:
            self.logger.error(formatted_message, exc_info=exception)
        else:
            self.logger.error(formatted_message)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a warning level message.
        
        Args:
            message: The message to log
            context: Optional context dictionary
        """
        formatted_message = message + self._format_context(context)
        self.logger.warning(formatted_message)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a debug level message.
        
        Args:
            message: The message to log
            context: Optional context dictionary
        """
        formatted_message = message + self._format_context(context)
        self.logger.debug(formatted_message)
    
    def generate_summary(self, stats: Dict[str, int]) -> str:
        """
        Generate a summary log containing extraction statistics.
        
        Args:
            stats: Dictionary containing extraction statistics with keys:
                - total_attempted: Total records attempted
                - total_extracted: Total records successfully extracted
                - total_validated: Total records that passed validation
                - total_rejected: Total records rejected due to validation errors
                - total_duplicates_removed: Total duplicate records removed
                - extraction_status: Status of extraction (Success/Partial/Failed)
        
        Returns:
            Formatted summary string
        """
        summary_lines = [
            "=" * 60,
            "EXTRACTION SUMMARY",
            "=" * 60,
            f"Timestamp: {datetime.now().isoformat()}",
            f"Total Records Attempted: {stats.get('total_attempted', 0)}",
            f"Total Records Extracted: {stats.get('total_extracted', 0)}",
            f"Total Records Validated: {stats.get('total_validated', 0)}",
            f"Total Records Rejected: {stats.get('total_rejected', 0)}",
            f"Total Duplicates Removed: {stats.get('total_duplicates_removed', 0)}",
            f"Extraction Status: {stats.get('extraction_status', 'Unknown')}",
            "=" * 60,
        ]
        
        summary = "\n".join(summary_lines)
        self.info(f"\n{summary}")
        
        return summary
