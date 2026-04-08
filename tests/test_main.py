"""
Unit tests for the main entry point.

Tests CLI argument parsing, orchestrator initialization, and execution flow.

Requirements: 9.1, 9.2, 9.3
"""

import pytest
import sys
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import main


class TestArgumentParsing:
    """Test suite for command-line argument parsing."""
    
    def test_parse_arguments_defaults(self):
        """Test parsing with default arguments."""
        with patch('sys.argv', ['main.py']):
            args = main.parse_arguments()
            
            assert args.state == "Maharashtra"
            assert args.output == "./output"
            assert args.timeout == 30
            assert args.rate_limit == 1.0
            assert args.max_retries == 3
            assert args.log_level == "INFO"
            assert args.config is None
    
    def test_parse_arguments_custom_state(self):
        """Test parsing with custom state argument."""
        with patch('sys.argv', ['main.py', '--state', 'Gujarat']):
            args = main.parse_arguments()
            
            assert args.state == "Gujarat"
    
    def test_parse_arguments_custom_output(self):
        """Test parsing with custom output directory."""
        with patch('sys.argv', ['main.py', '--output', '/custom/path']):
            args = main.parse_arguments()
            
            assert args.output == "/custom/path"
    
    def test_parse_arguments_custom_timeout(self):
        """Test parsing with custom timeout."""
        with patch('sys.argv', ['main.py', '--timeout', '60']):
            args = main.parse_arguments()
            
            assert args.timeout == 60
    
    def test_parse_arguments_custom_rate_limit(self):
        """Test parsing with custom rate limit."""
        with patch('sys.argv', ['main.py', '--rate-limit', '2.5']):
            args = main.parse_arguments()
            
            assert args.rate_limit == 2.5
    
    def test_parse_arguments_custom_max_retries(self):
        """Test parsing with custom max retries."""
        with patch('sys.argv', ['main.py', '--max-retries', '5']):
            args = main.parse_arguments()
            
            assert args.max_retries == 5
    
    def test_parse_arguments_custom_log_level(self):
        """Test parsing with custom log level."""
        with patch('sys.argv', ['main.py', '--log-level', 'DEBUG']):
            args = main.parse_arguments()
            
            assert args.log_level == "DEBUG"
    
    def test_parse_arguments_custom_config(self):
        """Test parsing with custom config file."""
        with patch('sys.argv', ['main.py', '--config', 'config.yaml']):
            args = main.parse_arguments()
            
            assert args.config == "config.yaml"
    
    def test_parse_arguments_all_custom(self):
        """Test parsing with all custom arguments."""
        with patch('sys.argv', [
            'main.py',
            '--state', 'Karnataka',
            '--output', '/output',
            '--timeout', '45',
            '--rate-limit', '1.5',
            '--max-retries', '4',
            '--log-level', 'WARNING',
            '--config', 'custom.yaml'
        ]):
            args = main.parse_arguments()
            
            assert args.state == "Karnataka"
            assert args.output == "/output"
            assert args.timeout == 45
            assert args.rate_limit == 1.5
            assert args.max_retries == 4
            assert args.log_level == "WARNING"
            assert args.config == "custom.yaml"
    
    def test_parse_arguments_invalid_log_level(self):
        """Test parsing with invalid log level."""
        with patch('sys.argv', ['main.py', '--log-level', 'INVALID']):
            with pytest.raises(SystemExit):
                main.parse_arguments()


class TestConvertArgsToDict:
    """Test suite for argument conversion."""
    
    def test_convert_args_to_dict(self):
        """Test conversion of arguments to dictionary."""
        with patch('sys.argv', [
            'main.py',
            '--state', 'Maharashtra',
            '--output', './output',
            '--timeout', '30',
            '--rate-limit', '1.0',
            '--max-retries', '3',
            '--log-level', 'INFO'
        ]):
            args = main.parse_arguments()
            cli_dict = main.convert_args_to_dict(args)
            
            assert cli_dict["target_state"] == "Maharashtra"
            assert cli_dict["output_directory"] == "./output"
            assert cli_dict["request_timeout"] == 30
            assert cli_dict["rate_limit_delay"] == 1.0
            assert cli_dict["max_retries"] == 3
            assert cli_dict["log_level"] == "INFO"
    
    def test_convert_args_to_dict_custom_values(self):
        """Test conversion with custom values."""
        with patch('sys.argv', [
            'main.py',
            '--state', 'Gujarat',
            '--output', '/custom',
            '--timeout', '60',
            '--rate-limit', '2.0',
            '--max-retries', '5',
            '--log-level', 'DEBUG'
        ]):
            args = main.parse_arguments()
            cli_dict = main.convert_args_to_dict(args)
            
            assert cli_dict["target_state"] == "Gujarat"
            assert cli_dict["output_directory"] == "/custom"
            assert cli_dict["request_timeout"] == 60
            assert cli_dict["rate_limit_delay"] == 2.0
            assert cli_dict["max_retries"] == 5
            assert cli_dict["log_level"] == "DEBUG"


class TestMainFunction:
    """Test suite for main function."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_main_success(self, temp_dir):
        """Test main function with successful execution."""
        with patch('sys.argv', ['main.py']):
            with patch('main.ScraperOrchestrator') as mock_orchestrator_class:
                mock_orchestrator = Mock()
                mock_orchestrator.run.return_value = True
                mock_orchestrator.stats = {
                    "total_extracted": 100,
                    "total_validated": 95,
                    "total_rejected": 5,
                    "total_duplicates_removed": 10,
                    "extraction_status": "Success",
                    "errors": []
                }
                mock_orchestrator_class.return_value = mock_orchestrator
                
                with patch('sys.stdout', new=StringIO()) as fake_out:
                    exit_code = main.main()
                    
                    assert exit_code == 0
                    output = fake_out.getvalue()
                    assert "SUCCESS" in output
                    assert "100" in output
    
    def test_main_failure(self, temp_dir):
        """Test main function with failed execution."""
        with patch('sys.argv', ['main.py']):
            with patch('main.ScraperOrchestrator') as mock_orchestrator_class:
                mock_orchestrator = Mock()
                mock_orchestrator.run.return_value = False
                mock_orchestrator.stats = {
                    "total_extracted": 0,
                    "total_validated": 0,
                    "total_rejected": 0,
                    "total_duplicates_removed": 0,
                    "extraction_status": "Failed",
                    "errors": ["Network error"]
                }
                mock_orchestrator_class.return_value = mock_orchestrator
                
                with patch('sys.stdout', new=StringIO()) as fake_out:
                    exit_code = main.main()
                    
                    assert exit_code == 1
                    output = fake_out.getvalue()
                    assert "FAILED" in output
    
    def test_main_with_errors(self, temp_dir):
        """Test main function with errors in stats."""
        with patch('sys.argv', ['main.py']):
            with patch('main.ScraperOrchestrator') as mock_orchestrator_class:
                mock_orchestrator = Mock()
                mock_orchestrator.run.return_value = False
                mock_orchestrator.stats = {
                    "total_extracted": 50,
                    "total_validated": 40,
                    "total_rejected": 10,
                    "total_duplicates_removed": 5,
                    "extraction_status": "Partial",
                    "errors": ["Error 1", "Error 2"]
                }
                mock_orchestrator_class.return_value = mock_orchestrator
                
                with patch('sys.stdout', new=StringIO()) as fake_out:
                    exit_code = main.main()
                    
                    assert exit_code == 1
                    output = fake_out.getvalue()
                    assert "Error 1" in output
                    assert "Error 2" in output
    
    def test_main_keyboard_interrupt(self):
        """Test main function with keyboard interrupt."""
        with patch('sys.argv', ['main.py']):
            with patch('main.ScraperOrchestrator') as mock_orchestrator_class:
                mock_orchestrator_class.side_effect = KeyboardInterrupt()
                
                with patch('sys.stdout', new=StringIO()) as fake_out:
                    exit_code = main.main()
                    
                    assert exit_code == 1
                    output = fake_out.getvalue()
                    assert "interrupted" in output.lower()
    
    def test_main_exception(self):
        """Test main function with exception."""
        with patch('sys.argv', ['main.py']):
            with patch('main.ScraperOrchestrator') as mock_orchestrator_class:
                mock_orchestrator_class.side_effect = Exception("Test error")
                
                with patch('sys.stdout', new=StringIO()) as fake_out:
                    exit_code = main.main()
                    
                    assert exit_code == 1
                    output = fake_out.getvalue()
                    assert "Fatal error" in output
    
    def test_main_with_config_file(self):
        """Test main function with config file argument."""
        with patch('sys.argv', ['main.py', '--config', 'config.yaml']):
            with patch('main.ScraperOrchestrator') as mock_orchestrator_class:
                mock_orchestrator = Mock()
                mock_orchestrator.run.return_value = True
                mock_orchestrator.stats = {
                    "total_extracted": 50,
                    "total_validated": 50,
                    "total_rejected": 0,
                    "total_duplicates_removed": 0,
                    "extraction_status": "Success",
                    "errors": []
                }
                mock_orchestrator_class.return_value = mock_orchestrator
                
                with patch('sys.stdout', new=StringIO()):
                    exit_code = main.main()
                    
                    assert exit_code == 0
                    # Verify orchestrator was called with config file
                    mock_orchestrator_class.assert_called_once()
                    call_kwargs = mock_orchestrator_class.call_args[1]
                    assert call_kwargs["config_file"] == "config.yaml"
    
    def test_main_with_custom_arguments(self):
        """Test main function with custom CLI arguments."""
        with patch('sys.argv', [
            'main.py',
            '--state', 'Gujarat',
            '--output', '/output',
            '--timeout', '60',
            '--rate-limit', '2.0',
            '--max-retries', '5',
            '--log-level', 'DEBUG'
        ]):
            with patch('main.ScraperOrchestrator') as mock_orchestrator_class:
                mock_orchestrator = Mock()
                mock_orchestrator.run.return_value = True
                mock_orchestrator.stats = {
                    "total_extracted": 0,
                    "total_validated": 0,
                    "total_rejected": 0,
                    "total_duplicates_removed": 0,
                    "extraction_status": "Success",
                    "errors": []
                }
                mock_orchestrator_class.return_value = mock_orchestrator
                
                with patch('sys.stdout', new=StringIO()):
                    exit_code = main.main()
                    
                    assert exit_code == 0
                    # Verify orchestrator was called with correct CLI args
                    mock_orchestrator_class.assert_called_once()
                    call_kwargs = mock_orchestrator_class.call_args[1]
                    cli_args = call_kwargs["cli_args"]
                    assert cli_args["target_state"] == "Gujarat"
                    assert cli_args["output_directory"] == "/output"
                    assert cli_args["request_timeout"] == 60
                    assert cli_args["rate_limit_delay"] == 2.0
                    assert cli_args["max_retries"] == 5
                    assert cli_args["log_level"] == "DEBUG"
