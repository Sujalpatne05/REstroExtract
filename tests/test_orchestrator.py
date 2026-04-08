"""
Unit tests for the ScraperOrchestrator class.

Tests the orchestration of all components and the execution flow of the
FSSAI Restaurant Scraper.

Requirements: 9.1, 9.2, 9.3
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, MagicMock, patch
from src.orchestrator import ScraperOrchestrator
from src.config import ConfigManager
from src.logger import LoggerSystem


class TestScraperOrchestrator:
    """Test suite for ScraperOrchestrator class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def mock_config(self, temp_dir):
        """Create a mock ConfigManager."""
        config = Mock(spec=ConfigManager)
        config.get.side_effect = lambda key, default=None: {
            "target_state": "Maharashtra",
            "output_directory": temp_dir,
            "request_timeout": 30,
            "rate_limit_delay": 1.0,
            "max_retries": 3,
            "log_file": os.path.join(temp_dir, "test.log"),
            "log_level": "INFO",
        }.get(key, default)
        config.load_config.return_value = None
        config.validate_config.return_value = True
        return config
    
    @pytest.fixture
    def orchestrator(self, temp_dir):
        """Create a ScraperOrchestrator instance for testing."""
        with patch('src.orchestrator.ConfigManager') as mock_config_class:
            mock_config = Mock(spec=ConfigManager)
            mock_config.get.side_effect = lambda key, default=None: {
                "target_state": "Maharashtra",
                "output_directory": temp_dir,
                "request_timeout": 30,
                "rate_limit_delay": 1.0,
                "max_retries": 3,
                "log_file": os.path.join(temp_dir, "test.log"),
                "log_level": "INFO",
            }.get(key, default)
            mock_config.load_config.return_value = None
            mock_config.validate_config.return_value = True
            mock_config_class.return_value = mock_config
            
            orchestrator = ScraperOrchestrator()
            yield orchestrator
            
            # Clean up logger handlers to release file locks
            for handler in orchestrator.logger.logger.handlers[:]:
                handler.close()
                orchestrator.logger.logger.removeHandler(handler)
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test that orchestrator initializes with all components."""
        assert orchestrator.config is not None
        assert orchestrator.logger is not None
        assert orchestrator.scraper is not None
        assert orchestrator.validator is not None
        assert orchestrator.deduplicator is not None
        assert orchestrator.exporter is not None
    
    def test_orchestrator_stats_initialization(self, orchestrator):
        """Test that orchestrator initializes statistics correctly."""
        assert orchestrator.stats["total_attempted"] == 0
        assert orchestrator.stats["total_extracted"] == 0
        assert orchestrator.stats["total_validated"] == 0
        assert orchestrator.stats["total_rejected"] == 0
        assert orchestrator.stats["total_duplicates_removed"] == 0
        assert orchestrator.stats["extraction_status"] == "Pending"
        assert orchestrator.stats["errors"] == []
    
    def test_execute_scraping_pipeline_success(self, orchestrator):
        """Test successful execution of scraping pipeline."""
        # Mock scraper to return sample records
        sample_records = [
            {
                "business_name": "Restaurant A",
                "license_number": "LIC001",
                "license_type": "Central",
                "business_type": "Restaurant",
                "district": "Mumbai",
                "city_town": "Mumbai",
                "pin_code": "400001",
                "issue_date": "01-01-2023",
                "valid_till": "31-12-2024",
                "owner_contact": "John Doe",
                "mobile": "9876543210",
                "email": "john@example.com",
                "address": "123 Main St",
                "state": "Maharashtra",
            }
        ]
        
        orchestrator.scraper.extract_records = Mock(return_value=sample_records)
        orchestrator.scraper.check_robots_txt = Mock()
        orchestrator.scraper.set_user_agent = Mock()
        
        records = orchestrator.execute_scraping_pipeline()
        
        assert len(records) == 1
        assert records[0]["business_name"] == "Restaurant A"
        assert orchestrator.stats["total_attempted"] == 1
        assert orchestrator.stats["total_extracted"] == 1
    
    def test_execute_scraping_pipeline_empty(self, orchestrator):
        """Test scraping pipeline with no records."""
        orchestrator.scraper.extract_records = Mock(return_value=[])
        orchestrator.scraper.check_robots_txt = Mock()
        orchestrator.scraper.set_user_agent = Mock()
        
        records = orchestrator.execute_scraping_pipeline()
        
        assert len(records) == 0
        assert orchestrator.stats["total_attempted"] == 0
        assert orchestrator.stats["total_extracted"] == 0
    
    def test_execute_scraping_pipeline_error(self, orchestrator):
        """Test scraping pipeline error handling."""
        orchestrator.scraper.extract_records = Mock(
            side_effect=Exception("Network error")
        )
        orchestrator.scraper.check_robots_txt = Mock()
        orchestrator.scraper.set_user_agent = Mock()
        
        records = orchestrator.execute_scraping_pipeline()
        
        assert len(records) == 0
        assert len(orchestrator.stats["errors"]) > 0
    
    def test_execute_validation_pipeline_all_valid(self, orchestrator):
        """Test validation pipeline with all valid records."""
        records = [
            {
                "business_name": "Restaurant A",
                "license_number": "LIC001",
                "state": "Maharashtra",
                "email": "john@example.com",
                "mobile": "9876543210",
            },
            {
                "business_name": "Restaurant B",
                "license_number": "LIC002",
                "state": "Maharashtra",
                "email": "jane@example.com",
                "mobile": "9876543211",
            }
        ]
        
        validated = orchestrator.execute_validation_pipeline(records)
        
        assert len(validated) == 2
        assert orchestrator.stats["total_validated"] == 2
        assert orchestrator.stats["total_rejected"] == 0
    
    def test_execute_validation_pipeline_mixed(self, orchestrator):
        """Test validation pipeline with mixed valid and invalid records."""
        records = [
            {
                "business_name": "Restaurant A",
                "license_number": "LIC001",
                "state": "Maharashtra",
                "email": "john@example.com",
                "mobile": "9876543210",
            },
            {
                "business_name": "",  # Missing business name
                "license_number": "LIC002",
                "state": "Maharashtra",
                "email": "jane@example.com",
                "mobile": "9876543211",
            }
        ]
        
        validated = orchestrator.execute_validation_pipeline(records)
        
        assert len(validated) == 1
        assert orchestrator.stats["total_validated"] == 1
        assert orchestrator.stats["total_rejected"] == 1
    
    def test_execute_validation_pipeline_error(self, orchestrator):
        """Test validation pipeline error handling."""
        orchestrator.validator.validate_record = Mock(
            side_effect=Exception("Validation error")
        )
        
        records = [{"business_name": "Test"}]
        validated = orchestrator.execute_validation_pipeline(records)
        
        assert len(validated) == 0
        assert len(orchestrator.stats["errors"]) > 0
    
    def test_execute_deduplication_pipeline_no_duplicates(self, orchestrator):
        """Test deduplication pipeline with no duplicates."""
        records = [
            {
                "business_name": "Restaurant A",
                "license_number": "LIC001",
                "issue_date": "01-01-2023",
            },
            {
                "business_name": "Restaurant B",
                "license_number": "LIC002",
                "issue_date": "02-01-2023",
            }
        ]
        
        deduplicated = orchestrator.execute_deduplication_pipeline(records)
        
        assert len(deduplicated) == 2
        assert orchestrator.stats["total_duplicates_removed"] == 0
    
    def test_execute_deduplication_pipeline_with_duplicates(self, orchestrator):
        """Test deduplication pipeline with duplicate records."""
        records = [
            {
                "business_name": "Restaurant A",
                "license_number": "LIC001",
                "issue_date": "01-01-2023",
            },
            {
                "business_name": "Restaurant A Updated",
                "license_number": "LIC001",
                "issue_date": "02-01-2023",
            }
        ]
        
        deduplicated = orchestrator.execute_deduplication_pipeline(records)
        
        assert len(deduplicated) == 1
        assert orchestrator.stats["total_duplicates_removed"] == 1
        assert deduplicated[0]["business_name"] == "Restaurant A Updated"
    
    def test_execute_deduplication_pipeline_error(self, orchestrator):
        """Test deduplication pipeline error handling."""
        orchestrator.deduplicator.deduplicate = Mock(
            side_effect=Exception("Deduplication error")
        )
        
        records = [{"business_name": "Test"}]
        deduplicated = orchestrator.execute_deduplication_pipeline(records)
        
        # Should return original records on error
        assert len(deduplicated) == 1
        assert len(orchestrator.stats["errors"]) > 0
    
    def test_execute_export_pipeline_success(self, orchestrator, temp_dir):
        """Test successful execution of export pipeline."""
        records = [
            {
                "business_name": "Restaurant A",
                "license_number": "LIC001",
                "license_type": "Central",
                "business_type": "Restaurant",
                "district": "Mumbai",
                "city_town": "Mumbai",
                "pin_code": "400001",
                "issue_date": "01-01-2023",
                "valid_till": "31-12-2024",
                "owner_contact": "John Doe",
                "mobile": "9876543210",
                "email": "john@example.com",
                "address": "123 Main St",
                "state": "Maharashtra",
            }
        ]
        
        output_file = os.path.join(temp_dir, "test_export.xlsx")
        orchestrator.exporter.export_to_excel = Mock(return_value=output_file)
        
        result = orchestrator.execute_export_pipeline(records)
        
        assert result == output_file
        orchestrator.exporter.export_to_excel.assert_called_once()
    
    def test_execute_export_pipeline_error(self, orchestrator):
        """Test export pipeline error handling."""
        orchestrator.exporter.export_to_excel = Mock(
            side_effect=Exception("Export error")
        )
        
        records = [{"business_name": "Test"}]
        
        with pytest.raises(Exception):
            orchestrator.execute_export_pipeline(records)
        
        assert len(orchestrator.stats["errors"]) > 0
    
    def test_run_success(self, orchestrator, temp_dir):
        """Test successful complete execution."""
        sample_records = [
            {
                "business_name": "Restaurant A",
                "license_number": "LIC001",
                "license_type": "Central",
                "business_type": "Restaurant",
                "district": "Mumbai",
                "city_town": "Mumbai",
                "pin_code": "400001",
                "issue_date": "01-01-2023",
                "valid_till": "31-12-2024",
                "owner_contact": "John Doe",
                "mobile": "9876543210",
                "email": "john@example.com",
                "address": "123 Main St",
                "state": "Maharashtra",
            }
        ]
        
        # Mock all pipelines
        orchestrator.scraper.extract_records = Mock(return_value=sample_records)
        orchestrator.scraper.check_robots_txt = Mock()
        orchestrator.scraper.set_user_agent = Mock()
        orchestrator.exporter.export_to_excel = Mock(
            return_value=os.path.join(temp_dir, "output.xlsx")
        )
        
        success = orchestrator.run()
        
        assert success is True
        assert orchestrator.stats["extraction_status"] == "Success"
        assert orchestrator.stats["total_extracted"] == 1
    
    def test_run_no_records(self, orchestrator):
        """Test execution with no records extracted."""
        orchestrator.scraper.extract_records = Mock(return_value=[])
        orchestrator.scraper.check_robots_txt = Mock()
        orchestrator.scraper.set_user_agent = Mock()
        
        success = orchestrator.run()
        
        assert success is False
        assert orchestrator.stats["extraction_status"] == "Failed"
    
    def test_run_fatal_error(self, orchestrator):
        """Test execution with fatal error."""
        orchestrator.scraper.extract_records = Mock(
            side_effect=Exception("Fatal error")
        )
        orchestrator.scraper.check_robots_txt = Mock()
        orchestrator.scraper.set_user_agent = Mock()
        
        success = orchestrator.run()
        
        assert success is False
        assert orchestrator.stats["extraction_status"] == "Failed"
        assert len(orchestrator.stats["errors"]) > 0
    
    def test_generate_execution_summary(self, orchestrator):
        """Test execution summary generation."""
        orchestrator.stats["total_extracted"] = 100
        orchestrator.stats["total_validated"] = 95
        orchestrator.stats["total_rejected"] = 5
        orchestrator.stats["total_duplicates_removed"] = 10
        orchestrator.stats["extraction_status"] = "Success"
        
        summary = orchestrator.generate_execution_summary()
        
        assert "EXTRACTION SUMMARY" in summary
        assert "100" in summary
        assert "95" in summary
        assert "5" in summary
        assert "10" in summary
        assert "Success" in summary
    
    def test_generate_execution_summary_with_errors(self, orchestrator):
        """Test execution summary generation with errors."""
        orchestrator.stats["errors"] = ["Error 1", "Error 2"]
        
        summary = orchestrator.generate_execution_summary()
        
        assert "EXTRACTION SUMMARY" in summary
