"""
Property-based tests for DeduplicatorEngine module.

Tests correctness properties using hypothesis library.
"""

from hypothesis import given, settings, strategies as st, HealthCheck
from src.deduplicator import DeduplicatorEngine


# Custom strategies for generating test data
@st.composite
def restaurant_records(draw, min_size=0, max_size=10):
    """Generate valid restaurant records."""
    num_records = draw(st.integers(min_value=min_size, max_value=max_size))
    records = []
    
    for i in range(num_records):
        record = {
            "business_name": draw(st.text(min_size=1, max_size=50)),
            "license_number": draw(st.text(min_size=1, max_size=20)),
            "license_type": draw(st.text(max_size=20)),
            "business_type": draw(st.text(max_size=20)),
            "district": draw(st.text(max_size=20)),
            "city_town": draw(st.text(max_size=20)),
            "pin_code": draw(st.text(max_size=10)),
            "issue_date": draw(st.sampled_from([
                "01-01-2023",
                "02-01-2023",
                "03-01-2023",
                "2023-01-01",
                "2023-01-02",
                "2023-01-03",
            ])),
            "valid_till": draw(st.text(max_size=20)),
            "owner_contact": draw(st.text(max_size=50)),
            "mobile": draw(st.text(max_size=15)),
            "email": draw(st.emails()),
            "address": draw(st.text(max_size=100)),
            "state": "Maharashtra",
        }
        records.append(record)
    
    return records


@st.composite
def duplicate_records(draw):
    """Generate records with intentional duplicates."""
    # Create a base record
    base_license = draw(st.text(min_size=1, max_size=20))
    num_duplicates = draw(st.integers(min_value=2, max_value=5))
    
    records = []
    for i in range(num_duplicates):
        record = {
            "business_name": "Test Restaurant",
            "license_number": base_license,
            "license_type": "State",
            "business_type": "Restaurant",
            "district": "Mumbai",
            "city_town": "Mumbai",
            "pin_code": "400001",
            "issue_date": draw(st.sampled_from([
                "01-01-2023",
                "02-01-2023",
                "03-01-2023",
            ])),
            "valid_till": "31-12-2024",
            "owner_contact": "Owner",
            "mobile": "9999999999",
            "email": "test@example.com",
            "address": "123 Main St",
            "state": "Maharashtra",
        }
        records.append(record)
    
    return records


class TestDeduplicatorProperties:
    """Property-based tests for DeduplicatorEngine."""
    
    @given(restaurant_records(min_size=0, max_size=20))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_deduplicate_returns_list(self, records):
        """
        Property: deduplicate() always returns a list and integer count.
        
        Validates: Requirements 10.1, 10.2
        """
        deduplicator = DeduplicatorEngine()
        deduplicated, count = deduplicator.deduplicate(records)
        
        assert isinstance(deduplicated, list)
        assert isinstance(count, int)
        assert count >= 0
    
    @given(restaurant_records(min_size=0, max_size=20))
    @settings(max_examples=20)
    def test_deduplicate_output_size(self, records):
        """
        Property: deduplicated list size + duplicate count = original size.
        
        Validates: Requirements 10.1, 10.2
        """
        deduplicator = DeduplicatorEngine()
        deduplicated, count = deduplicator.deduplicate(records)
        
        # Total records = deduplicated + removed duplicates
        assert len(deduplicated) + count == len(records)
    
    @given(restaurant_records(min_size=0, max_size=20))
    @settings(max_examples=20)
    def test_deduplicate_no_duplicate_licenses(self, records):
        """
        Property: After deduplication, no duplicate License Numbers exist.
        
        Validates: Requirements 10.1, 10.2
        """
        deduplicator = DeduplicatorEngine()
        deduplicated, _ = deduplicator.deduplicate(records)
        
        license_numbers = [r.get("license_number", "") for r in deduplicated]
        assert len(license_numbers) == len(set(license_numbers))
    
    @given(duplicate_records())
    @settings(max_examples=20)
    def test_deduplicate_keeps_most_recent(self, records):
        """
        Property: For duplicates, the most recent record (by Issue Date) is kept.
        
        Validates: Requirements 10.1, 10.2
        """
        deduplicator = DeduplicatorEngine()
        deduplicated, count = deduplicator.deduplicate(records)
        
        # Should have exactly 1 record (all duplicates)
        assert len(deduplicated) == 1
        assert count == len(records) - 1
        
        # The kept record should have the most recent date
        kept_record = deduplicated[0]
        
        # Parse dates and verify
        from datetime import datetime
        
        def parse_date(date_str):
            formats = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d"]
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return datetime.min
        
        kept_date = parse_date(kept_record.get("issue_date", ""))
        
        for record in records:
            record_date = parse_date(record.get("issue_date", ""))
            assert kept_date >= record_date
    
    @given(restaurant_records(min_size=0, max_size=20))
    @settings(max_examples=20)
    def test_find_duplicates_by_license_groups_correctly(self, records):
        """
        Property: find_duplicates_by_license() groups all records by License Number.
        
        Validates: Requirements 10.1
        """
        deduplicator = DeduplicatorEngine()
        grouped = deduplicator.find_duplicates_by_license(records)
        
        # All records should be in exactly one group
        total_grouped = sum(len(group) for group in grouped.values())
        assert total_grouped == len(records)
        
        # Each record should be in the correct group
        for license_number, group in grouped.items():
            for record in group:
                assert record.get("license_number", "") == license_number
    
    @given(restaurant_records(min_size=1, max_size=20))
    @settings(max_examples=20)
    def test_keep_most_recent_returns_record(self, records):
        """
        Property: keep_most_recent() returns a record from the input list.
        
        Validates: Requirements 10.2
        """
        deduplicator = DeduplicatorEngine()
        result = deduplicator.keep_most_recent(records)
        
        # Result should be one of the input records
        assert result in records
    
    @given(restaurant_records(min_size=0, max_size=20))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_deduplicate_preserves_all_fields(self, records):
        """
        Property: Deduplication preserves all fields in the kept records.
        
        Validates: Requirements 10.1, 10.2
        """
        deduplicator = DeduplicatorEngine()
        deduplicated, _ = deduplicator.deduplicate(records)
        
        # All deduplicated records should have all fields
        expected_fields = {
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
        }
        
        for record in deduplicated:
            # Record should have all expected fields (even if empty)
            for field in expected_fields:
                assert field in record or record.get(field) is not None
    
    @given(st.lists(
        st.fixed_dictionaries({
            "license_number": st.text(min_size=1),
            "issue_date": st.sampled_from(["01-01-2023", "02-01-2023", "03-01-2023"]),
        }),
        min_size=0,
        max_size=20,
        unique_by=lambda x: (x["license_number"], x["issue_date"])
    ))
    @settings(max_examples=20)
    def test_deduplicate_idempotent(self, records):
        """
        Property: Deduplicating twice gives the same result as deduplicating once.
        
        Validates: Requirements 10.1, 10.2
        """
        deduplicator = DeduplicatorEngine()
        
        # First deduplication
        deduplicated1, count1 = deduplicator.deduplicate(records)
        
        # Second deduplication on the result
        deduplicated2, count2 = deduplicator.deduplicate(deduplicated1)
        
        # Second deduplication should remove 0 duplicates
        assert count2 == 0
        assert len(deduplicated2) == len(deduplicated1)
