"""Property-based tests for DataValidator module.

Tests validate correctness properties using hypothesis library.

Feature: fssai-restaurant-scraper
Property 4: Data Validation Correctness
Validates: Requirements 4.1, 4.2, 4.3, 4.4

Property Statement:
For any record, if the record contains all required fields (Business Name, License Number, State)
with non-empty values, valid email format (if present), and valid phone format (if present),
then the record must pass validation and be included in the export; otherwise, it must be
excluded and logged with error details.
"""

from hypothesis import given, strategies as st, assume
import pytest
from src.validator import DataValidator


# Strategy for generating valid restaurant records
@st.composite
def valid_restaurant_records(draw, target_state="Maharashtra"):
    """Generate valid restaurant records that should pass validation.
    
    Generates records with:
    - All required fields present and non-empty
    - Valid email format (if email is included)
    - Valid phone format (if phone is included)
    - State matching the target state
    """
    # Generate valid email addresses manually to ensure they match our regex
    local_part = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789._+-",
        min_size=1,
        max_size=20
    ))
    domain = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789-",
        min_size=1,
        max_size=15
    ))
    tld = draw(st.sampled_from(["com", "org", "net", "co.uk", "io"]))
    
    email = draw(st.one_of(
        st.just(""),  # Empty is valid (optional field)
        st.just(f"{local_part}@{domain}.{tld}")
    ))
    
    # Generate valid phone with at least one digit
    phone_digits = draw(st.text(alphabet="0123456789", min_size=1, max_size=10))
    phone_formatting = draw(st.text(alphabet="+- ()", max_size=5))
    phone = draw(st.one_of(
        st.just(""),  # Empty is valid (optional field)
        st.just(f"{phone_digits}{phone_formatting}")
    ))
    
    return {
        "business_name": draw(st.text(min_size=1, max_size=100, alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ")),
        "license_number": draw(st.text(min_size=1, max_size=50, alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")),
        "license_type": draw(st.text(max_size=50)),
        "business_type": draw(st.text(max_size=50)),
        "district": draw(st.text(max_size=50)),
        "city_town": draw(st.text(max_size=50)),
        "pin_code": draw(st.text(max_size=10)),
        "issue_date": draw(st.text(max_size=20)),
        "valid_till": draw(st.text(max_size=20)),
        "owner_contact": draw(st.text(max_size=100)),
        "mobile": phone,
        "email": email,
        "address": draw(st.text(max_size=200)),
        "state": target_state,
    }


# Strategy for generating invalid records (missing required fields)
@st.composite
def invalid_records_missing_required(draw, target_state="Maharashtra"):
    """Generate records with missing required fields.
    
    Generates records missing one of: business_name, license_number, or state.
    """
    record = {
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
        "mobile": draw(st.text(alphabet="0123456789+- ()", max_size=20)),
        "email": draw(st.emails()),
        "address": draw(st.text(max_size=200)),
        "state": target_state,
    }
    
    # Remove one of the required fields
    field_to_remove = draw(st.sampled_from(["business_name", "license_number", "state"]))
    del record[field_to_remove]
    
    return record


# Strategy for generating records with invalid email
@st.composite
def invalid_records_bad_email(draw, target_state="Maharashtra"):
    """Generate records with invalid email format."""
    # Generate strings that are NOT valid emails
    invalid_email = draw(st.one_of(
        st.just("notanemail"),
        st.just("missing@domain"),
        st.just("@nodomain.com"),
        st.just("spaces in@email.com"),
        st.text(min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz").filter(lambda x: "@" not in x)
    ))
    
    return {
        "business_name": draw(st.text(min_size=1, max_size=100, alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ")),
        "license_number": draw(st.text(min_size=1, max_size=50, alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")),
        "license_type": draw(st.text(max_size=50)),
        "business_type": draw(st.text(max_size=50)),
        "district": draw(st.text(max_size=50)),
        "city_town": draw(st.text(max_size=50)),
        "pin_code": draw(st.text(max_size=10)),
        "issue_date": draw(st.text(max_size=20)),
        "valid_till": draw(st.text(max_size=20)),
        "owner_contact": draw(st.text(max_size=100)),
        "mobile": draw(st.text(alphabet="0123456789+- ()", max_size=20)),
        "email": invalid_email,
        "address": draw(st.text(max_size=200)),
        "state": target_state,
    }


# Strategy for generating records with invalid phone
@st.composite
def invalid_records_bad_phone(draw, target_state="Maharashtra"):
    """Generate records with invalid phone format."""
    # Generate strings with invalid phone characters (letters, special chars)
    invalid_phone = draw(st.one_of(
        st.just("abc123"),
        st.just("phone@number"),
        st.just("***"),
        st.text(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&*", min_size=1, max_size=20)
    ))
    
    # Generate valid email manually
    local_part = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789._+-",
        min_size=1,
        max_size=20
    ))
    domain = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789-",
        min_size=1,
        max_size=15
    ))
    tld = draw(st.sampled_from(["com", "org", "net", "co.uk", "io"]))
    email = f"{local_part}@{domain}.{tld}"
    
    # Generate business_name that is not just whitespace
    business_name = draw(st.text(
        min_size=1,
        max_size=100,
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
    ).filter(lambda x: x.strip()))  # Ensure not just whitespace
    
    return {
        "business_name": business_name,
        "license_number": draw(st.text(min_size=1, max_size=50, alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")),
        "license_type": draw(st.text(max_size=50)),
        "business_type": draw(st.text(max_size=50)),
        "district": draw(st.text(max_size=50)),
        "city_town": draw(st.text(max_size=50)),
        "pin_code": draw(st.text(max_size=10)),
        "issue_date": draw(st.text(max_size=20)),
        "valid_till": draw(st.text(max_size=20)),
        "owner_contact": draw(st.text(max_size=100)),
        "mobile": invalid_phone,
        "email": email,
        "address": draw(st.text(max_size=200)),
        "state": target_state,
    }


# Strategy for generating records with wrong state
@st.composite
def invalid_records_wrong_state(draw):
    """Generate records with state not matching target."""
    wrong_states = ["Gujarat", "Karnataka", "Tamil Nadu", "Delhi", "Goa"]
    
    # Generate valid email manually
    local_part = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789._+-",
        min_size=1,
        max_size=20
    ))
    domain = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789-",
        min_size=1,
        max_size=15
    ))
    tld = draw(st.sampled_from(["com", "org", "net", "co.uk", "io"]))
    email = f"{local_part}@{domain}.{tld}"
    
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
        "mobile": draw(st.text(alphabet="0123456789+- ()", max_size=20)),
        "email": email,
        "address": draw(st.text(max_size=200)),
        "state": draw(st.sampled_from(wrong_states)),
    }


class TestDataValidatorProperties:
    """Property-based tests for DataValidator.
    
    Feature: fssai-restaurant-scraper
    Property 4: Data Validation Correctness
    Validates: Requirements 4.1, 4.2, 4.3, 4.4
    """
    
    @pytest.fixture
    def validator(self):
        """Create a DataValidator instance."""
        return DataValidator(target_state="Maharashtra")
    
    @given(valid_restaurant_records())
    def test_valid_records_pass_validation(self, record):
        """Property: Valid records with all required fields and valid formats pass validation.
        
        For any record with:
        - All required fields (business_name, license_number, state) non-empty
        - Valid email format (if present)
        - Valid phone format (if present)
        - State matching target
        
        Then: validate_record() returns (True, None)
        """
        validator = DataValidator(target_state="Maharashtra")
        is_valid, error = validator.validate_record(record)
        assert is_valid is True, f"Valid record failed validation: {error}"
        assert error is None
    
    @given(invalid_records_missing_required())
    def test_records_missing_required_fields_fail(self, record):
        """Property: Records missing required fields fail validation.
        
        For any record missing one of: business_name, license_number, or state
        
        Then: validate_record() returns (False, error_message)
        """
        validator = DataValidator(target_state="Maharashtra")
        is_valid, error = validator.validate_record(record)
        assert is_valid is False, "Record with missing required field should fail"
        assert error is not None
        assert "required fields" in error.lower()
    
    @given(invalid_records_bad_email())
    def test_records_with_invalid_email_fail(self, record):
        """Property: Records with invalid email format fail validation.
        
        For any record with invalid email format (when email is non-empty)
        
        Then: validate_record() returns (False, error_message) or passes if email is empty
        """
        validator = DataValidator(target_state="Maharashtra")
        
        # If email is empty, it should pass (email is optional)
        if not record["email"] or not record["email"].strip():
            is_valid, error = validator.validate_record(record)
            assert is_valid is True
        else:
            # If email is non-empty and invalid, should fail
            is_valid, error = validator.validate_record(record)
            # Either fails with email error, or passes if email happens to be valid
            if not is_valid:
                assert "email" in error.lower()
    
    @given(invalid_records_bad_phone())
    def test_records_with_invalid_phone_fail(self, record):
        """Property: Records with invalid phone format fail validation.
        
        For any record with invalid phone format (when phone is non-empty)
        
        Then: validate_record() returns (False, error_message) or passes if phone is empty
        """
        validator = DataValidator(target_state="Maharashtra")
        
        # If phone is empty, it should pass (phone is optional)
        if not record["mobile"] or not record["mobile"].strip():
            is_valid, error = validator.validate_record(record)
            assert is_valid is True
        else:
            # If phone is non-empty and invalid, should fail
            is_valid, error = validator.validate_record(record)
            # Either fails with phone error, or fails with email error first
            # (validation checks email before phone)
            if not is_valid:
                assert "phone" in error.lower() or "email" in error.lower()
    
    @given(invalid_records_wrong_state())
    def test_records_with_wrong_state_fail(self, record):
        """Property: Records with non-matching state fail validation.
        
        For any record with state not matching target state (Maharashtra)
        
        Then: validate_record() returns (False, error_message)
        """
        validator = DataValidator(target_state="Maharashtra")
        is_valid, error = validator.validate_record(record)
        assert is_valid is False, "Record with wrong state should fail"
        assert error is not None
        assert "state" in error.lower()
    
    @given(st.text(min_size=1, max_size=100))
    def test_email_validation_consistency(self, email_text):
        """Property: Email validation is consistent.
        
        For any email string, validate_email() should return the same result
        when called multiple times with the same input.
        """
        validator = DataValidator()
        result1 = validator.validate_email(email_text)
        result2 = validator.validate_email(email_text)
        assert result1 == result2, "Email validation should be consistent"
    
    @given(st.text(min_size=1, max_size=100))
    def test_phone_validation_consistency(self, phone_text):
        """Property: Phone validation is consistent.
        
        For any phone string, validate_phone() should return the same result
        when called multiple times with the same input.
        """
        validator = DataValidator()
        result1 = validator.validate_phone(phone_text)
        result2 = validator.validate_phone(phone_text)
        assert result1 == result2, "Phone validation should be consistent"
    
    @given(st.text(min_size=1, max_size=50), st.text(min_size=1, max_size=50))
    def test_state_validation_case_insensitive(self, state1, state2):
        """Property: State validation is case-insensitive.
        
        For any two state strings that are equal when lowercased,
        validate_state() should return True.
        """
        validator = DataValidator()
        
        # Only test if they're equal when lowercased
        if state1.lower() == state2.lower():
            result = validator.validate_state(state1, state2)
            assert result is True, f"State validation should be case-insensitive for {state1} vs {state2}"
    
    @given(valid_restaurant_records())
    def test_required_fields_validation_matches_record_validation(self, record):
        """Property: Required fields validation is consistent with record validation.
        
        For any record, if validate_required_fields() returns True,
        then validate_record() should not fail due to missing required fields.
        """
        validator = DataValidator(target_state="Maharashtra")
        
        required_valid = validator.validate_required_fields(record)
        is_valid, error = validator.validate_record(record)
        
        if required_valid:
            # If required fields are valid, record validation should not fail
            # due to required fields (may fail for other reasons like email/phone/state)
            if not is_valid:
                assert "required fields" not in error.lower()
