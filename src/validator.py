"""Data validation module for FSSAI Restaurant Scraper.

This module provides the DataValidator class for validating extracted restaurant
records against business rules defined in requirements 4.1-4.4.

Validation Rules:
- Required fields: Business Name, License Number, State (must be non-empty)
- Email: Must match standard email format (if present)
- Phone: Must contain only digits and standard formatting characters (if present)
- State: Must match the configured target state filter
"""

import re
from typing import Dict, Any, Tuple, Optional


class DataValidator:
    """Validates extracted restaurant records against business rules.
    
    Provides methods to validate individual records and specific fields according
    to the validation rules defined in the FSSAI Restaurant Scraper specification.
    
    Validation includes:
    - Required field presence and non-empty values
    - Email format validation using regex
    - Phone number format validation
    - State filter matching
    """
    
    # Email regex pattern for standard email format validation
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Phone regex pattern: digits, +, -, space, and parentheses
    PHONE_PATTERN = r'^[\d\s\-\+\(\)]+$'
    
    def __init__(self, target_state: str = "Maharashtra"):
        """Initialize DataValidator with target state filter.
        
        Args:
            target_state: The state to filter records by (default: "Maharashtra")
        """
        self.target_state = target_state
    
    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate a complete restaurant record against all validation rules.
        
        Performs comprehensive validation including:
        1. Required fields presence and non-empty values
        2. Email format validation (if email field is present and non-empty)
        3. Phone format validation (if mobile field is present and non-empty)
        4. State filter matching
        
        Args:
            record: Dictionary containing restaurant record data
            
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
            - If valid: (True, None)
            - If invalid: (False, error_message describing the validation failure)
        """
        # Check required fields first
        if not self.validate_required_fields(record):
            return False, "Missing or empty required fields (Business Name, License Number, State)"
        
        # Validate state matches filter
        state = record.get("state", "").strip()
        if not self.validate_state(state, self.target_state):
            return False, f"State '{state}' does not match filter '{self.target_state}'"
        
        # Validate email if present and non-empty
        email = record.get("email", "").strip()
        if email and not self.validate_email(email):
            return False, f"Invalid email format: '{email}'"
        
        # Validate phone if present and non-empty
        mobile = record.get("mobile", "").strip()
        if mobile and not self.validate_phone(mobile):
            return False, f"Invalid phone format: '{mobile}'"
        
        return True, None
    
    def validate_required_fields(self, record: Dict[str, Any]) -> bool:
        """Validate that all required fields are present and non-empty.
        
        Required fields are:
        - Business Name
        - License Number
        - State
        
        Args:
            record: Dictionary containing restaurant record data
            
        Returns:
            True if all required fields are present and non-empty, False otherwise
        """
        required_fields = ["business_name", "license_number", "state"]
        
        for field in required_fields:
            value = record.get(field, "")
            # Check if field exists and has non-empty value after stripping whitespace
            if not value or not str(value).strip():
                return False
        
        return True
    
    def validate_email(self, email: str) -> bool:
        """Validate email address format using regex pattern matching.
        
        Validates against standard email format:
        - Must have local part (before @)
        - Must have @ symbol
        - Must have domain name
        - Must have top-level domain (after .)
        
        Args:
            email: Email address string to validate
            
        Returns:
            True if email matches valid format, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        
        email = email.strip()
        return bool(re.match(self.EMAIL_PATTERN, email))
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format.
        
        Valid phone numbers contain only:
        - Digits (0-9)
        - Plus sign (+) for country code
        - Hyphen (-) for formatting
        - Space for formatting
        - Parentheses for area code formatting
        
        Args:
            phone: Phone number string to validate
            
        Returns:
            True if phone contains only valid characters, False otherwise
        """
        if not phone or not isinstance(phone, str):
            return False
        
        phone = phone.strip()
        # Phone must have at least one digit
        if not any(c.isdigit() for c in phone):
            return False
        
        return bool(re.match(self.PHONE_PATTERN, phone))
    
    def validate_state(self, state: str, expected_state: str) -> bool:
        """Validate that state matches the expected/configured state filter.
        
        Performs case-insensitive comparison to handle variations in state names.
        
        Args:
            state: State value from the record
            expected_state: Expected state filter value
            
        Returns:
            True if state matches expected state (case-insensitive), False otherwise
        """
        if not state or not expected_state:
            return False
        
        # Case-insensitive comparison
        return state.strip().lower() == expected_state.strip().lower()
