"""Unit tests for DataValidator module.

Tests cover:
- Valid records pass validation
- Records with missing required fields fail validation
- Invalid email formats are rejected
- Invalid phone formats are rejected
- Records with non-matching state are rejected
"""

import pytest
from src.validator import DataValidator


class TestDataValidator:
    """Test suite for DataValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create a DataValidator instance with Maharashtra as target state."""
        return DataValidator(target_state="Maharashtra")
    
    @pytest.fixture
    def valid_record(self):
        """Create a valid restaurant record for testing."""
        return {
            "business_name": "Test Restaurant",
            "license_number": "FSSAI123456",
            "license_type": "State License",
            "business_type": "Restaurant",
            "district": "Mumbai",
            "city_town": "Mumbai",
            "pin_code": "400001",
            "issue_date": "2023-01-15",
            "valid_till": "2025-01-15",
            "owner_contact": "John Doe",
            "mobile": "+91-9876543210",
            "email": "test@restaurant.com",
            "address": "123 Main Street, Mumbai",
            "state": "Maharashtra",
        }
    
    # Tests for validate_record()
    
    def test_validate_record_with_valid_record(self, validator, valid_record):
        """Test that valid records pass validation."""
        is_valid, error = validator.validate_record(valid_record)
        assert is_valid is True
        assert error is None
    
    def test_validate_record_missing_business_name(self, validator, valid_record):
        """Test that records with missing business name fail validation."""
        valid_record["business_name"] = ""
        is_valid, error = validator.validate_record(valid_record)
        assert is_valid is False
        assert "required fields" in error.lower()
    
    def test_validate_record_missing_license_number(self, validator, valid_record):
        """Test that records with missing license number fail validation."""
        valid_record["license_number"] = ""
        is_valid, error = validator.validate_record(valid_record)
        assert is_valid is False
        assert "required fields" in error.lower()
    
    def test_validate_record_missing_state(self, validator, valid_record):
        """Test that records with missing state fail validation."""
        valid_record["state"] = ""
        is_valid, error = validator.validate_record(valid_record)
        assert is_valid is False
        assert "required fields" in error.lower()
    
    def test_validate_record_invalid_email(self, validator, valid_record):
        """Test that records with invalid email fail validation."""
        valid_record["email"] = "invalid-email"
        is_valid, error = validator.validate_record(valid_record)
        assert is_valid is False
        assert "email" in error.lower()
    
    def test_validate_record_invalid_phone(self, validator, valid_record):
        """Test that records with invalid phone fail validation."""
        valid_record["mobile"] = "abc@#$%"
        is_valid, error = validator.validate_record(valid_record)
        assert is_valid is False
        assert "phone" in error.lower()
    
    def test_validate_record_wrong_state(self, validator, valid_record):
        """Test that records with non-matching state fail validation."""
        valid_record["state"] = "Gujarat"
        is_valid, error = validator.validate_record(valid_record)
        assert is_valid is False
        assert "state" in error.lower()
    
    def test_validate_record_with_empty_email(self, validator, valid_record):
        """Test that records with empty email pass validation (email is optional)."""
        valid_record["email"] = ""
        is_valid, error = validator.validate_record(valid_record)
        assert is_valid is True
        assert error is None
    
    def test_validate_record_with_empty_phone(self, validator, valid_record):
        """Test that records with empty phone pass validation (phone is optional)."""
        valid_record["mobile"] = ""
        is_valid, error = validator.validate_record(valid_record)
        assert is_valid is True
        assert error is None
    
    # Tests for validate_required_fields()
    
    def test_validate_required_fields_all_present(self, validator, valid_record):
        """Test that records with all required fields pass validation."""
        assert validator.validate_required_fields(valid_record) is True
    
    def test_validate_required_fields_missing_business_name(self, validator, valid_record):
        """Test that missing business name fails validation."""
        del valid_record["business_name"]
        assert validator.validate_required_fields(valid_record) is False
    
    def test_validate_required_fields_empty_business_name(self, validator, valid_record):
        """Test that empty business name fails validation."""
        valid_record["business_name"] = ""
        assert validator.validate_required_fields(valid_record) is False
    
    def test_validate_required_fields_whitespace_business_name(self, validator, valid_record):
        """Test that whitespace-only business name fails validation."""
        valid_record["business_name"] = "   "
        assert validator.validate_required_fields(valid_record) is False
    
    def test_validate_required_fields_missing_license_number(self, validator, valid_record):
        """Test that missing license number fails validation."""
        del valid_record["license_number"]
        assert validator.validate_required_fields(valid_record) is False
    
    def test_validate_required_fields_empty_license_number(self, validator, valid_record):
        """Test that empty license number fails validation."""
        valid_record["license_number"] = ""
        assert validator.validate_required_fields(valid_record) is False
    
    def test_validate_required_fields_missing_state(self, validator, valid_record):
        """Test that missing state fails validation."""
        del valid_record["state"]
        assert validator.validate_required_fields(valid_record) is False
    
    def test_validate_required_fields_empty_state(self, validator, valid_record):
        """Test that empty state fails validation."""
        valid_record["state"] = ""
        assert validator.validate_required_fields(valid_record) is False
    
    # Tests for validate_email()
    
    def test_validate_email_valid_format(self, validator):
        """Test that valid email formats pass validation."""
        valid_emails = [
            "test@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "test123@test-domain.com",
            "a@b.co",
        ]
        for email in valid_emails:
            assert validator.validate_email(email) is True, f"Failed for {email}"
    
    def test_validate_email_missing_at_symbol(self, validator):
        """Test that emails without @ symbol fail validation."""
        assert validator.validate_email("testexample.com") is False
    
    def test_validate_email_missing_domain(self, validator):
        """Test that emails without domain fail validation."""
        assert validator.validate_email("test@") is False
    
    def test_validate_email_missing_tld(self, validator):
        """Test that emails without top-level domain fail validation."""
        assert validator.validate_email("test@example") is False
    
    def test_validate_email_multiple_at_symbols(self, validator):
        """Test that emails with multiple @ symbols fail validation."""
        assert validator.validate_email("test@@example.com") is False
    
    def test_validate_email_empty_string(self, validator):
        """Test that empty email string fails validation."""
        assert validator.validate_email("") is False
    
    def test_validate_email_whitespace_only(self, validator):
        """Test that whitespace-only email fails validation."""
        assert validator.validate_email("   ") is False
    
    def test_validate_email_with_spaces(self, validator):
        """Test that emails with spaces fail validation."""
        assert validator.validate_email("test @example.com") is False
    
    def test_validate_email_none_type(self, validator):
        """Test that None type fails validation."""
        assert validator.validate_email(None) is False
    
    # Tests for validate_phone()
    
    def test_validate_phone_valid_formats(self, validator):
        """Test that valid phone formats pass validation."""
        valid_phones = [
            "9876543210",
            "+91-9876543210",
            "+91 9876543210",
            "(91) 9876543210",
            "91-98-765-43210",
            "+1-800-555-0123",
            "555 123 4567",
        ]
        for phone in valid_phones:
            assert validator.validate_phone(phone) is True, f"Failed for {phone}"
    
    def test_validate_phone_no_digits(self, validator):
        """Test that phone with no digits fails validation."""
        assert validator.validate_phone("+-() ") is False
    
    def test_validate_phone_with_letters(self, validator):
        """Test that phone with letters fails validation."""
        assert validator.validate_phone("9876543210abc") is False
    
    def test_validate_phone_with_special_chars(self, validator):
        """Test that phone with invalid special characters fails validation."""
        assert validator.validate_phone("9876543210@#$") is False
    
    def test_validate_phone_empty_string(self, validator):
        """Test that empty phone string fails validation."""
        assert validator.validate_phone("") is False
    
    def test_validate_phone_whitespace_only(self, validator):
        """Test that whitespace-only phone fails validation."""
        assert validator.validate_phone("   ") is False
    
    def test_validate_phone_none_type(self, validator):
        """Test that None type fails validation."""
        assert validator.validate_phone(None) is False
    
    # Tests for validate_state()
    
    def test_validate_state_exact_match(self, validator):
        """Test that exact state match passes validation."""
        assert validator.validate_state("Maharashtra", "Maharashtra") is True
    
    def test_validate_state_case_insensitive(self, validator):
        """Test that state comparison is case-insensitive."""
        assert validator.validate_state("maharashtra", "Maharashtra") is True
        assert validator.validate_state("MAHARASHTRA", "maharashtra") is True
        assert validator.validate_state("MaHaRaShTrA", "maharashtra") is True
    
    def test_validate_state_with_whitespace(self, validator):
        """Test that state comparison handles whitespace."""
        assert validator.validate_state("  Maharashtra  ", "Maharashtra") is True
        assert validator.validate_state("Maharashtra", "  Maharashtra  ") is True
    
    def test_validate_state_mismatch(self, validator):
        """Test that mismatched states fail validation."""
        assert validator.validate_state("Gujarat", "Maharashtra") is False
        assert validator.validate_state("Karnataka", "Maharashtra") is False
    
    def test_validate_state_empty_state(self, validator):
        """Test that empty state fails validation."""
        assert validator.validate_state("", "Maharashtra") is False
    
    def test_validate_state_empty_expected(self, validator):
        """Test that empty expected state fails validation."""
        assert validator.validate_state("Maharashtra", "") is False
    
    def test_validate_state_both_empty(self, validator):
        """Test that both empty states fail validation."""
        assert validator.validate_state("", "") is False
    
    # Tests for different target states
    
    def test_validator_with_different_target_state(self):
        """Test validator with different target state."""
        validator = DataValidator(target_state="Gujarat")
        record = {
            "business_name": "Test",
            "license_number": "123",
            "state": "Gujarat",
            "email": "test@example.com",
            "mobile": "9876543210",
        }
        is_valid, error = validator.validate_record(record)
        assert is_valid is True
    
    def test_validator_rejects_wrong_state_for_target(self):
        """Test validator rejects records with wrong state for target."""
        validator = DataValidator(target_state="Gujarat")
        record = {
            "business_name": "Test",
            "license_number": "123",
            "state": "Maharashtra",
            "email": "test@example.com",
            "mobile": "9876543210",
        }
        is_valid, error = validator.validate_record(record)
        assert is_valid is False
        assert "state" in error.lower()
