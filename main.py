"""FSSAI Restaurant Scraper - Main entry point.

This module provides the CLI interface for the FSSAI Restaurant Scraper.
It parses command-line arguments, initializes the orchestrator, and handles
the execution flow.

Requirements: 9.1, 9.2, 9.3
"""

import argparse
import sys
from typing import Optional, Dict, Any
from src.orchestrator import ScraperOrchestrator


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Supported arguments:
    - --state: Target state for filtering (default: Maharashtra)
    - --output: Output directory for Excel files (default: ./output)
    - --timeout: Request timeout in seconds (default: 30)
    - --rate-limit: Rate limit delay between requests in seconds (default: 1.0)
    - --max-retries: Maximum number of retries for failed requests (default: 3)
    - --log-level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) (default: INFO)
    - --config: Path to configuration file (optional)
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="FSSAI Restaurant Scraper - Extract restaurant license data from FSSAI portal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --state Maharashtra --output ./output
  python main.py --config config.yaml --log-level DEBUG
  python main.py --state Maharashtra --timeout 60 --max-retries 5
        """
    )
    
    parser.add_argument(
        "--state",
        type=str,
        default="Maharashtra",
        help="Target state for filtering (default: Maharashtra)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="./output",
        help="Output directory for Excel files (default: ./output)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)"
    )
    
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=1.0,
        help="Rate limit delay between requests in seconds (default: 1.0)"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum number of retries for failed requests (default: 3)"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration file (optional)"
    )
    
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock data for testing (when FSSAI portal is unavailable)"
    )
    
    parser.add_argument(
        "--append-mode",
        action="store_true",
        help="Append data to existing Excel file instead of creating new one"
    )
    
    return parser.parse_args()


def convert_args_to_dict(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Convert parsed arguments to dictionary format for ConfigManager.
    
    Args:
        args: Parsed arguments namespace
        
    Returns:
        Dictionary of CLI arguments
    """
    return {
        "target_state": args.state,
        "output_directory": args.output,
        "request_timeout": args.timeout,
        "rate_limit_delay": args.rate_limit,
        "max_retries": args.max_retries,
        "log_level": args.log_level,
        "use_mock_data": args.mock,
        "append_mode": args.append_mode,
    }


def main() -> int:
    """
    Main entry point for the FSSAI Restaurant Scraper.
    
    Parses command-line arguments, initializes the orchestrator,
    executes the scraping pipeline, and prints the execution summary.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Convert arguments to dictionary
        cli_args = convert_args_to_dict(args)
        
        # Initialize orchestrator with config file and CLI arguments
        orchestrator = ScraperOrchestrator(
            config_file=args.config,
            cli_args=cli_args
        )
        
        # Execute the scraping pipeline
        success = orchestrator.run()
        
        # Print execution summary to console
        print("\n" + "=" * 60)
        print("EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Status: {'SUCCESS' if success else 'FAILED'}")
        print(f"Total Records Extracted: {orchestrator.stats.get('total_extracted', 0)}")
        print(f"Total Records Validated: {orchestrator.stats.get('total_validated', 0)}")
        print(f"Total Records Rejected: {orchestrator.stats.get('total_rejected', 0)}")
        print(f"Total Duplicates Removed: {orchestrator.stats.get('total_duplicates_removed', 0)}")
        print(f"Extraction Status: {orchestrator.stats.get('extraction_status', 'Unknown')}")
        
        if orchestrator.stats.get("errors"):
            print("\nErrors Encountered:")
            for error in orchestrator.stats["errors"]:
                print(f"  - {error}")
        
        print("=" * 60 + "\n")
        
        # Return appropriate exit code
        return 0 if success else 1
    
    except KeyboardInterrupt:
        print("\n\nScraper interrupted by user")
        return 1
    
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
