"""
Main Orchestration Module

Coordinates all components and manages the execution flow of the FSSAI Restaurant Scraper.
Orchestrates the scraping, validation, deduplication, and export pipelines.

Requirements: 1.1, 1.4, 2.1, 2.2, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4, 
6.1, 6.2, 6.3, 7.1, 7.2, 7.3, 8.1, 8.2, 8.3, 9.1, 9.2, 9.3, 10.1, 10.2
"""

from typing import Dict, List, Any, Optional
from src.config import ConfigManager
from src.logger import LoggerSystem
from src.scraper import ScraperEngine
from src.validator import DataValidator
from src.deduplicator import DeduplicatorEngine
from src.exporter import ExporterEngine


class ScraperOrchestrator:
    """
    Main orchestration class that coordinates all components.
    
    Manages the execution flow of the scraping pipeline:
    1. Initialize configuration and logger
    2. Check robots.txt compliance
    3. Fetch and parse data from FSSAI portal
    4. Validate extracted records
    5. Deduplicate records by License Number
    6. Export to Excel with metadata
    7. Generate summary log
    """
    
    def __init__(
        self,
        config_file: Optional[str] = None,
        cli_args: Optional[Dict] = None
    ):
        """
        Initialize the ScraperOrchestrator.
        
        Args:
            config_file: Path to configuration file (optional)
            cli_args: Dictionary of CLI arguments (optional)
        """
        # Initialize configuration
        self.config = ConfigManager(config_file=config_file, cli_args=cli_args)
        self.config.load_config()
        self.config.validate_config()
        
        # Initialize logger
        log_file = self.config.get("log_file", "./logs/scraper.log")
        log_level = self.config.get("log_level", "INFO")
        self.logger = LoggerSystem(log_file=log_file, log_level=log_level)
        
        # Initialize components
        self.scraper = ScraperEngine(config=self.config, logger=self.logger)
        self.validator = DataValidator(
            target_state=self.config.get("target_state", "Maharashtra")
        )
        self.deduplicator = DeduplicatorEngine()
        self.exporter = ExporterEngine(config=self.config, logger=self.logger)
        
        # Statistics tracking
        self.stats = {
            "total_attempted": 0,
            "total_extracted": 0,
            "total_validated": 0,
            "total_rejected": 0,
            "total_duplicates_removed": 0,
            "extraction_status": "Pending",
            "errors": [],
        }
    
    def run(self) -> bool:
        """
        Main entry point for the scraper orchestration.
        
        Executes the complete scraping pipeline:
        1. Scraping pipeline (fetch and parse data)
        2. Validation pipeline (validate records)
        3. Deduplication pipeline (remove duplicates)
        4. Export pipeline (export to Excel)
        5. Generate execution summary
        
        Returns:
            True if execution completed successfully, False otherwise
        """
        try:
            self.logger.info("Starting FSSAI Restaurant Scraper")
            
            # Execute scraping pipeline
            raw_records = self.execute_scraping_pipeline()
            if not raw_records:
                self.stats["extraction_status"] = "Failed"
                self.logger.error("No records extracted from FSSAI portal")
                self.generate_execution_summary()
                return False
            
            # Execute validation pipeline
            validated_records = self.execute_validation_pipeline(raw_records)
            
            # Execute deduplication pipeline
            deduplicated_records = self.execute_deduplication_pipeline(validated_records)
            
            # Execute export pipeline
            output_file = self.execute_export_pipeline(deduplicated_records)
            
            # Generate execution summary
            self.stats["extraction_status"] = "Success"
            self.generate_execution_summary()
            
            self.logger.info(
                "FSSAI Restaurant Scraper completed successfully",
                context={"output_file": output_file}
            )
            
            return True
        
        except Exception as e:
            self.stats["extraction_status"] = "Failed"
            self.stats["errors"].append(str(e))
            self.logger.error(
                "FSSAI Restaurant Scraper encountered a fatal error",
                exception=e
            )
            self.generate_execution_summary()
            return False
    
    def execute_scraping_pipeline(self) -> List[Dict[str, Any]]:
        """
        Execute the scraping pipeline.
        
        Fetches and parses data from the FSSAI portal.
        
        Returns:
            List of extracted restaurant records
        """
        try:
            self.logger.info("Starting scraping pipeline")
            
            # Check robots.txt compliance
            self.scraper.check_robots_txt()
            
            # Set user agent
            self.scraper.set_user_agent()
            
            # Extract records from FSSAI portal
            records = self.scraper.extract_records()
            
            self.stats["total_attempted"] = len(records)
            self.stats["total_extracted"] = len(records)
            
            self.logger.info(
                "Scraping pipeline completed",
                context={"records_extracted": len(records)}
            )
            
            return records
        
        except Exception as e:
            self.logger.error(
                "Scraping pipeline failed",
                exception=e
            )
            self.stats["errors"].append(f"Scraping pipeline error: {str(e)}")
            return []
    
    def execute_validation_pipeline(
        self, records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute the validation pipeline.
        
        Validates extracted records against business rules.
        
        Args:
            records: List of extracted records to validate
            
        Returns:
            List of validated records
        """
        try:
            self.logger.info("Starting validation pipeline")
            
            validated_records = []
            rejected_count = 0
            
            for idx, record in enumerate(records):
                is_valid, error_message = self.validator.validate_record(record)
                
                if is_valid:
                    validated_records.append(record)
                    self.stats["total_validated"] += 1
                else:
                    rejected_count += 1
                    self.stats["total_rejected"] += 1
                    self.logger.warning(
                        f"Record validation failed",
                        context={
                            "record_index": idx,
                            "license_number": record.get("license_number", "N/A"),
                            "error": error_message
                        }
                    )
            
            self.logger.info(
                "Validation pipeline completed",
                context={
                    "validated": len(validated_records),
                    "rejected": rejected_count
                }
            )
            
            return validated_records
        
        except Exception as e:
            self.logger.error(
                "Validation pipeline failed",
                exception=e
            )
            self.stats["errors"].append(f"Validation pipeline error: {str(e)}")
            return []
    
    def execute_deduplication_pipeline(
        self, records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute the deduplication pipeline.
        
        Removes duplicate records by License Number, keeping the most recent.
        
        Args:
            records: List of validated records to deduplicate
            
        Returns:
            List of deduplicated records
        """
        try:
            self.logger.info("Starting deduplication pipeline")
            
            deduplicated_records, duplicate_count = self.deduplicator.deduplicate(records)
            
            self.stats["total_duplicates_removed"] = duplicate_count
            
            self.logger.info(
                "Deduplication pipeline completed",
                context={
                    "deduplicated": len(deduplicated_records),
                    "duplicates_removed": duplicate_count
                }
            )
            
            return deduplicated_records
        
        except Exception as e:
            self.logger.error(
                "Deduplication pipeline failed",
                exception=e
            )
            self.stats["errors"].append(f"Deduplication pipeline error: {str(e)}")
            return records  # Return original records if deduplication fails
    
    def execute_export_pipeline(
        self, records: List[Dict[str, Any]]
    ) -> str:
        """
        Execute the export pipeline.
        
        Exports records to Excel file with metadata.
        
        Args:
            records: List of deduplicated records to export
            
        Returns:
            Path to the exported Excel file
        """
        try:
            self.logger.info("Starting export pipeline")
            
            output_file = self.exporter.export_to_excel(records, self.stats)
            
            self.logger.info(
                "Export pipeline completed",
                context={"output_file": output_file}
            )
            
            return output_file
        
        except Exception as e:
            self.logger.error(
                "Export pipeline failed",
                exception=e
            )
            self.stats["errors"].append(f"Export pipeline error: {str(e)}")
            raise
    
    def generate_execution_summary(self) -> str:
        """
        Generate execution summary with statistics.
        
        Creates a summary log containing extraction statistics and any errors.
        
        Returns:
            Formatted summary string
        """
        summary = self.logger.generate_summary(self.stats)
        
        # Log any errors that occurred
        if self.stats["errors"]:
            self.logger.warning(
                "Errors encountered during execution",
                context={"errors": self.stats["errors"]}
            )
        
        return summary
