"""
Unit tests for DeduplicatorEngine module.

Tests deduplication logic, duplicate detection, and record selection.
"""

import pytest
from src.deduplicator import DeduplicatorEngine


class TestDeduplicatorEngine:
    """Test suite for DeduplicatorEngine."""
    
    @pytest.fixture
    def deduplicator(self):
        """Create a DeduplicatorEngine instance."""
        return DeduplicatorEngine()
    
    def test_deduplicate_empty_list(self, deduplicator):
        """Test deduplication with empty record list."""
        records = []
        deduplicated, count = deduplicator.deduplicate(records)
        
        assert deduplicated == []
        assert count == 0
    
    def test_deduplicate_single_record(self, deduplicator):
        """Test deduplication with single record."""
        records = [
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "01-01-2023",
            }
        ]
        deduplicated, count = deduplicator.deduplicate(records)
        
        assert len(deduplicated) == 1
        assert count == 0
        assert deduplicated[0]["license_number"] == "LIC001"
    
    def test_deduplicate_no_duplicates(self, deduplicator):
        """Test deduplication with no duplicate records."""
        records = [
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "01-01-2023",
            },
            {
                "license_number": "LIC002",
                "business_name": "Restaurant B",
                "issue_date": "02-01-2023",
            },
            {
                "license_number": "LIC003",
                "business_name": "Restaurant C",
                "issue_date": "03-01-2023",
            },
        ]
        deduplicated, count = deduplicator.deduplicate(records)
        
        assert len(deduplicated) == 3
        assert count == 0
    
    def test_deduplicate_with_duplicates(self, deduplicator):
        """Test deduplication with duplicate records."""
        records = [
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "01-01-2023",
            },
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "02-01-2023",
            },
            {
                "license_number": "LIC002",
                "business_name": "Restaurant B",
                "issue_date": "03-01-2023",
            },
        ]
        deduplicated, count = deduplicator.deduplicate(records)
        
        assert len(deduplicated) == 2
        assert count == 1
        
        # Check that the most recent record is kept
        lic001_record = next(r for r in deduplicated if r["license_number"] == "LIC001")
        assert lic001_record["issue_date"] == "02-01-2023"
    
    def test_deduplicate_multiple_duplicates(self, deduplicator):
        """Test deduplication with multiple duplicate groups."""
        records = [
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "01-01-2023",
            },
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "02-01-2023",
            },
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "03-01-2023",
            },
            {
                "license_number": "LIC002",
                "business_name": "Restaurant B",
                "issue_date": "01-01-2023",
            },
            {
                "license_number": "LIC002",
                "business_name": "Restaurant B",
                "issue_date": "02-01-2023",
            },
        ]
        deduplicated, count = deduplicator.deduplicate(records)
        
        assert len(deduplicated) == 2
        assert count == 3
        
        # Check that the most recent records are kept
        lic001_record = next(r for r in deduplicated if r["license_number"] == "LIC001")
        assert lic001_record["issue_date"] == "03-01-2023"
        
        lic002_record = next(r for r in deduplicated if r["license_number"] == "LIC002")
        assert lic002_record["issue_date"] == "02-01-2023"
    
    def test_find_duplicates_by_license_empty(self, deduplicator):
        """Test finding duplicates with empty list."""
        records = []
        grouped = deduplicator.find_duplicates_by_license(records)
        
        assert grouped == {}
    
    def test_find_duplicates_by_license_single(self, deduplicator):
        """Test finding duplicates with single record."""
        records = [
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
            }
        ]
        grouped = deduplicator.find_duplicates_by_license(records)
        
        assert len(grouped) == 1
        assert "LIC001" in grouped
        assert len(grouped["LIC001"]) == 1
    
    def test_find_duplicates_by_license_multiple(self, deduplicator):
        """Test finding duplicates with multiple records."""
        records = [
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
            },
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
            },
            {
                "license_number": "LIC002",
                "business_name": "Restaurant B",
            },
        ]
        grouped = deduplicator.find_duplicates_by_license(records)
        
        assert len(grouped) == 2
        assert len(grouped["LIC001"]) == 2
        assert len(grouped["LIC002"]) == 1
    
    def test_keep_most_recent_empty(self, deduplicator):
        """Test keeping most recent with empty list."""
        duplicates = []
        result = deduplicator.keep_most_recent(duplicates)
        
        assert result == {}
    
    def test_keep_most_recent_single(self, deduplicator):
        """Test keeping most recent with single record."""
        duplicates = [
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "01-01-2023",
            }
        ]
        result = deduplicator.keep_most_recent(duplicates)
        
        assert result["license_number"] == "LIC001"
        assert result["issue_date"] == "01-01-2023"
    
    def test_keep_most_recent_multiple(self, deduplicator):
        """Test keeping most recent with multiple records."""
        duplicates = [
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "01-01-2023",
            },
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "03-01-2023",
            },
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "02-01-2023",
            },
        ]
        result = deduplicator.keep_most_recent(duplicates)
        
        assert result["issue_date"] == "03-01-2023"
    
    def test_keep_most_recent_different_date_formats(self, deduplicator):
        """Test keeping most recent with different date formats."""
        duplicates = [
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "2023-01-01",
            },
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "03/01/2023",
            },
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "02-01-2023",
            },
        ]
        result = deduplicator.keep_most_recent(duplicates)
        
        # Should select the most recent date
        assert result["issue_date"] == "03/01/2023"
    
    def test_keep_most_recent_missing_date(self, deduplicator):
        """Test keeping most recent with missing issue date."""
        duplicates = [
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "",
            },
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "01-01-2023",
            },
        ]
        result = deduplicator.keep_most_recent(duplicates)
        
        # Should select the record with a valid date
        assert result["issue_date"] == "01-01-2023"
    
    def test_deduplicate_preserves_all_fields(self, deduplicator):
        """Test that deduplication preserves all record fields."""
        records = [
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "01-01-2023",
                "email": "old@example.com",
                "mobile": "9999999999",
            },
            {
                "license_number": "LIC001",
                "business_name": "Restaurant A",
                "issue_date": "02-01-2023",
                "email": "new@example.com",
                "mobile": "8888888888",
            },
        ]
        deduplicated, count = deduplicator.deduplicate(records)
        
        assert len(deduplicated) == 1
        assert count == 1
        assert deduplicated[0]["email"] == "new@example.com"
        assert deduplicated[0]["mobile"] == "8888888888"
