# Design Document: FSSAI Restaurant Scraper

## Overview

The FSSAI Restaurant Scraper is a Python-based web scraping application that extracts publicly available restaurant license data from the FSSAI portal (https://foscos.fssai.gov.in/). The system is designed to be ethical, maintainable, and reliable, with comprehensive error handling, data validation, and logging capabilities.

**Key Design Goals:**
- Extract restaurant license data with high accuracy and completeness
- Maintain ethical scraping practices (rate limiting, robots.txt compliance, proper User-Agent headers)
- Provide robust data validation and quality assurance
- Generate well-formatted Excel exports with metadata
- Enable easy configuration and customization
- Ensure comprehensive logging and error tracking

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FSSAI Restaurant Scraper                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Config     │  │   Logger     │  │   Validator  │       │
│  │  Management  │  │   System     │  │   Engine     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         ▲                  ▲                  ▲               │
│         │                  │                  │               │
│  ┌──────────────────────────────────────────────────┐        │
│  │         Main Orchestration Layer                 │        │
│  │  (Execution Flow, State Management)              │        │
│  └──────────────────────────────────────────────────┘        │
│         ▲                  ▲                  ▲               │
│         │                  │                  │               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Scraper    │  │ Deduplicator │  │   Exporter   │       │
│  │   Engine     │  │   Engine     │  │   Engine     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         │                  │                  │               │
│         └──────────────────┼──────────────────┘               │
│                            │                                  │
│                   ┌────────────────┐                          │
│                   │  Data Pipeline │                          │
│                   │  (In-Memory)   │                          │
│                   └────────────────┘                          │
│                            │                                  │
└────────────────────────────┼──────────────────────────────────┘
                             │
                    ┌────────────────┐
                    │  FSSAI Portal  │
                    │  (HTTP/HTTPS)  │
                    └────────────────┘
```

### Component Responsibilities

1. **Config Management**: Loads and validates configuration from files and CLI arguments
2. **Logger System**: Centralized logging with file and console output
3. **Validator Engine**: Validates extracted data against business rules
4. **Scraper Engine**: Handles HTTP requests, HTML parsing, and data extraction
5. **Deduplicator Engine**: Identifies and removes duplicate records
6. **Exporter Engine**: Generates Excel files with metadata
7. **Main Orchestration**: Coordinates all components and manages execution flow

## Components and Interfaces

### 1. Configuration Management Module

**Purpose**: Load, validate, and provide access to configuration settings

**Class: `ConfigManager`**

```python
class ConfigManager:
    def __init__(self, config_file: Optional[str] = None, cli_args: Optional[Dict] = None)
    def load_config(self) -> Dict[str, Any]
    def get(self, key: str, default: Any = None) -> Any
    def validate_config(self) -> bool
    def get_all() -> Dict[str, Any]
```

**Configuration Schema:**
```python
{
    "target_state": str,              # Default: "Maharashtra"
    "output_directory": str,          # Default: "./output"
    "request_timeout": int,           # Default: 30 (seconds)
    "rate_limit_delay": float,        # Default: 1.0 (seconds)
    "max_retries": int,               # Default: 3
    "log_file": str,                  # Default: "./logs/scraper.log"
    "log_level": str,                 # Default: "INFO"
}
```

### 2. Logger System Module

**Purpose**: Centralized logging with structured output

**Class: `LoggerSystem`**

```python
class LoggerSystem:
    def __init__(self, log_file: str, log_level: str = "INFO")
    def info(self, message: str, context: Optional[Dict] = None) -> None
    def error(self, message: str, exception: Optional[Exception] = None, context: Optional[Dict] = None) -> None
    def warning(self, message: str, context: Optional[Dict] = None) -> None
    def debug(self, message: str, context: Optional[Dict] = None) -> None
    def generate_summary(self, stats: Dict[str, int]) -> str
```

**Log Entry Format:**
```
[TIMESTAMP] [LEVEL] [COMPONENT] Message | Context: {...}
```

### 3. Data Validator Module

**Purpose**: Validate extracted data against business rules

**Class: `DataValidator`**

```python
class DataValidator:
    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]
    def validate_required_fields(self, record: Dict[str, Any]) -> bool
    def validate_email(self, email: str) -> bool
    def validate_phone(self, phone: str) -> bool
    def validate_state(self, state: str, expected_state: str) -> bool
```

**Validation Rules:**
- Required fields: Business Name, License Number, State
- Email: Must match standard email regex pattern
- Phone: Must contain only digits and standard formatting characters (+, -, space)
- State: Must match the configured target state

### 4. Scraper Engine Module

**Purpose**: Handle HTTP requests, HTML parsing, and data extraction

**Class: `ScraperEngine`**

```python
class ScraperEngine:
    def __init__(self, config: ConfigManager, logger: LoggerSystem)
    def fetch_page(self, url: str) -> Optional[str]
    def parse_html(self, html: str) -> List[Dict[str, Any]]
    def extract_records(self) -> List[Dict[str, Any]]
    def check_robots_txt(self) -> bool
    def set_user_agent(self) -> None
```

**Data Extraction Fields:**
```python
{
    "business_name": str,
    "license_number": str,
    "license_type": str,
    "business_type": str,
    "district": str,
    "city_town": str,
    "pin_code": str,
    "issue_date": str,
    "valid_till": str,
    "owner_contact": str,
    "mobile": str,
    "email": str,
    "address": str,
    "state": str,
}
```

**HTTP Request Strategy:**
- Respect robots.txt if present
- Include User-Agent header: `FSSAI-Restaurant-Scraper/1.0`
- Implement exponential backoff for retries
- Rate limiting: Minimum 1 second delay between requests
- Request timeout: Configurable (default 30 seconds)

### 5. Deduplicator Engine Module

**Purpose**: Identify and remove duplicate records

**Class: `DeduplicatorEngine`**

```python
class DeduplicatorEngine:
    def deduplicate(self, records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]
    def find_duplicates_by_license(self, records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]
    def keep_most_recent(self, duplicates: List[Dict[str, Any]]) -> Dict[str, Any]
```

**Deduplication Strategy:**
- Group records by License Number
- For each group with duplicates, keep the record with the most recent Issue Date
- Return deduplicated list and count of removed duplicates

### 6. Exporter Engine Module

**Purpose**: Generate Excel files with data and metadata

**Class: `ExporterEngine`**

```python
class ExporterEngine:
    def __init__(self, config: ConfigManager, logger: LoggerSystem)
    def export_to_excel(self, records: List[Dict[str, Any]], stats: Dict[str, int]) -> str
    def create_data_sheet(self, workbook, records: List[Dict[str, Any]]) -> None
    def create_metadata_sheet(self, workbook, stats: Dict[str, int]) -> None
    def format_columns(self, worksheet) -> None
    def generate_filename(self, state: str) -> str
```

**Excel Structure:**
- Sheet 1: "Data" - Contains extracted records with headers
- Sheet 2: "Metadata" - Contains extraction metadata
- Column widths: Auto-adjusted for readability
- Filename pattern: `FSSAI_Restaurants_[STATE]_[YYYYMMDD_HHMMSS].xlsx`

**Metadata Sheet Contents:**
```
Generation Date: [ISO 8601 timestamp]
Total Records Extracted: [count]
State Filter Applied: [state]
Extraction Status: [Success/Partial/Failed]
Records Validated: [count]
Records Rejected: [count]
Duplicates Removed: [count]
```

### 7. Main Orchestration Module

**Purpose**: Coordinate all components and manage execution flow

**Class: `ScraperOrchestrator`**

```python
class ScraperOrchestrator:
    def __init__(self, config_file: Optional[str] = None, cli_args: Optional[Dict] = None)
    def run(self) -> bool
    def execute_scraping_pipeline(self) -> List[Dict[str, Any]]
    def execute_validation_pipeline(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]
    def execute_deduplication_pipeline(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]
    def execute_export_pipeline(self, records: List[Dict[str, Any]]) -> str
    def generate_execution_summary(self) -> Dict[str, int]
```

**Execution Flow:**
1. Initialize configuration and logger
2. Check robots.txt compliance
3. Fetch and parse data from FSSAI portal
4. Validate extracted records
5. Deduplicate records by License Number
6. Export to Excel with metadata
7. Generate summary log

## Data Models

### Restaurant Record Model

```python
@dataclass
class RestaurantRecord:
    business_name: str
    license_number: str
    license_type: str
    business_type: str
    district: str
    city_town: str
    pin_code: str
    issue_date: str
    valid_till: str
    owner_contact: str
    mobile: str
    email: str
    address: str
    state: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RestaurantRecord':
        return cls(**data)
```

### Extraction Statistics Model

```python
@dataclass
class ExtractionStats:
    total_attempted: int = 0
    total_extracted: int = 0
    total_validated: int = 0
    total_rejected: int = 0
    total_duplicates_removed: int = 0
    extraction_status: str = "Pending"  # Pending, Success, Partial, Failed
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
```

## Data Flow and Processing Pipeline

### Scraping Pipeline

```
1. Load Configuration
   ↓
2. Initialize Logger
   ↓
3. Check robots.txt Compliance
   ↓
4. Fetch HTML from FSSAI Portal
   ├─ Retry up to 3 times on failure
   ├─ Apply rate limiting (1 second delay)
   └─ Handle network errors gracefully
   ↓
5. Parse HTML and Extract Records
   ├─ Extract 14 data fields
   └─ Handle missing fields (populate with null/empty)
   ↓
6. Return Raw Records List
```

### Validation Pipeline

```
1. For Each Record:
   ├─ Check Required Fields (Business Name, License Number, State)
   ├─ Validate Email Format (if present)
   ├─ Validate Phone Format (if present)
   ├─ Validate State Matches Filter
   └─ Log Validation Result
   ↓
2. Separate Valid and Invalid Records
   ↓
3. Return Valid Records + Validation Stats
```

### Deduplication Pipeline

```
1. Group Records by License Number
   ↓
2. For Each Group with Duplicates:
   ├─ Sort by Issue Date (descending)
   └─ Keep Most Recent Record
   ↓
3. Combine Unique Records
   ↓
4. Return Deduplicated Records + Duplicate Count
```

### Export Pipeline

```
1. Create Excel Workbook
   ↓
2. Create Data Sheet
   ├─ Add Column Headers
   ├─ Add Records (one per row)
   └─ Format Columns
   ↓
3. Create Metadata Sheet
   ├─ Add Generation Date
   ├─ Add Record Counts
   ├─ Add State Filter
   └─ Add Extraction Status
   ↓
4. Generate Filename with Timestamp
   ↓
5. Save to Output Directory
   ├─ Handle Filename Conflicts (append sequence number)
   └─ Return File Path
```

## Technology Stack

**Language**: Python 3.8+

**Core Libraries:**
- `requests`: HTTP requests with session management and retries
- `beautifulsoup4`: HTML parsing and data extraction
- `openpyxl`: Excel file generation and formatting
- `python-dotenv`: Configuration file loading
- `logging`: Built-in Python logging module

**Optional Libraries:**
- `urllib.robotparser`: robots.txt parsing and compliance checking
- `dataclasses`: Data model definitions (Python 3.7+)
- `typing`: Type hints for better code clarity

**Project Structure:**
```
fssai-restaurant-scraper/
├── src/
│   ├── __init__.py
│   ├── config.py              # ConfigManager
│   ├── logger.py              # LoggerSystem
│   ├── validator.py           # DataValidator
│   ├── scraper.py             # ScraperEngine
│   ├── deduplicator.py        # DeduplicatorEngine
│   ├── exporter.py            # ExporterEngine
│   ├── models.py              # Data models
│   └── orchestrator.py        # ScraperOrchestrator
├── config/
│   └── default_config.yaml    # Default configuration
├── output/                    # Generated Excel files
├── logs/                      # Log files
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
└── README.md                  # Documentation
```

## Error Handling

### Error Categories and Handling Strategies

**1. Network Errors**
- **Handling**: Retry up to 3 times with exponential backoff
- **Backoff Strategy**: 1s, 2s, 4s delays between retries
- **Logging**: Log each retry attempt with timestamp
- **Fallback**: Graceful termination with error message if all retries fail

**2. Parsing Errors**
- **Handling**: Log error with HTML snippet for debugging
- **Fallback**: Skip malformed record and continue processing
- **Logging**: Record error with record index and error details

**3. Validation Errors**
- **Handling**: Exclude invalid record from export
- **Logging**: Log validation failure with specific field that failed
- **Tracking**: Increment rejection counter for summary

**4. Configuration Errors**
- **Handling**: Use default values for missing configuration
- **Validation**: Validate all config values on startup
- **Logging**: Log warnings for missing config with defaults used

**5. File I/O Errors**
- **Handling**: Check directory permissions before writing
- **Fallback**: Use alternative output directory if primary fails
- **Logging**: Log file operation errors with full context

**6. Excel Export Errors**
- **Handling**: Catch workbook creation and write errors
- **Fallback**: Attempt to save with alternative filename
- **Logging**: Log export failure with error details

### Error Recovery Mechanisms

```python
# Retry with exponential backoff
def fetch_with_retry(url: str, max_retries: int = 3) -> Optional[str]:
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                delay = 2 ** attempt  # Exponential backoff
                logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s", 
                             context={"error": str(e)})
                time.sleep(delay)
            else:
                logger.error(f"Failed after {max_retries} retries", exception=e)
                return None
```

## Configuration Approach

### Configuration Sources (Priority Order)

1. **Command-Line Arguments** (highest priority)
2. **Configuration File** (YAML or JSON)
3. **Environment Variables**
4. **Default Values** (lowest priority)

### Configuration File Format (YAML)

```yaml
# config.yaml
target_state: "Maharashtra"
output_directory: "./output"
request_timeout: 30
rate_limit_delay: 1.0
max_retries: 3
log_file: "./logs/scraper.log"
log_level: "INFO"
```

### Command-Line Interface

```bash
python main.py \
  --state "Maharashtra" \
  --output "./output" \
  --timeout 30 \
  --rate-limit 1.0 \
  --max-retries 3 \
  --log-level INFO \
  --config config.yaml
```

### Configuration Validation

```python
VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
VALID_STATES = ["Maharashtra", "All"]  # Extensible for future states

def validate_config(config: Dict[str, Any]) -> bool:
    assert config["request_timeout"] > 0, "Timeout must be positive"
    assert config["rate_limit_delay"] > 0, "Rate limit must be positive"
    assert config["max_retries"] >= 0, "Max retries must be non-negative"
    assert config["log_level"] in VALID_LOG_LEVELS, "Invalid log level"
    assert os.path.isdir(config["output_directory"]), "Output directory must exist"
    return True
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Geographic Filtering Consistency

*For any* extracted restaurant record when Maharashtra state filter is active, the record's state field must equal "Maharashtra".

**Validates: Requirements 2.1, 2.2**

### Property 2: Data Field Extraction Completeness

*For any* extracted restaurant record, the record must contain all 14 required fields (Business Name, License Number, License Type, Business Type, District, City/Town, Pin Code, Issue Date, Valid Till, Owner/Contact, Mobile, Email, Address, State), with null/empty values for unavailable fields.

**Validates: Requirements 3.1, 3.2**

### Property 3: Date Format Preservation

*For any* extracted date field (Issue Date, Valid Till), the original date format from the source data must be preserved in the extracted record.

**Validates: Requirements 3.3**

### Property 4: Data Validation Correctness

*For any* record, if the record contains all required fields (Business Name, License Number, State) with non-empty values, valid email format (if present), and valid phone format (if present), then the record must pass validation and be included in the export; otherwise, it must be excluded and logged with error details.

**Validates: Requirements 4.1, 4.2, 4.3, 4.4**

### Property 5: Deduplication Correctness

*For any* set of extracted records, after deduplication by License Number, the result must contain no duplicate License Numbers, and for each group of duplicates, only the record with the most recent Issue Date must be retained.

**Validates: Requirements 10.1, 10.2**

### Property 6: Excel Export Record Completeness

*For any* set of validated and deduplicated records, the exported Excel file must contain exactly that many records in the data sheet (excluding the header row), with all 14 fields present as column headers.

**Validates: Requirements 5.1, 5.2**

### Property 7: Excel Metadata Accuracy

*For any* extraction execution, the metadata sheet in the exported Excel file must contain accurate counts matching the actual extraction statistics (total records extracted, total records validated, total records rejected, duplicates removed).

**Validates: Requirements 5.4**

### Property 8: Output Filename Pattern Compliance

*For any* exported Excel file, the filename must follow the pattern `FSSAI_Restaurants_[STATE]_[YYYYMMDD_HHMMSS].xlsx` where STATE is the configured state filter and timestamp is the current date/time.

**Validates: Requirements 6.1**

### Property 9: Output Directory Persistence

*For any* exported Excel file, the file must be saved to the configured output directory and be accessible for reading after export completes.

**Validates: Requirements 6.2**

### Property 10: Error Logging Completeness

*For any* error that occurs during scraping, the error must be logged with timestamp, error type, and relevant context information.

**Validates: Requirements 7.1**

### Property 11: Network Retry Mechanism

*For any* network error encountered during HTTP requests, the scraper must retry the request up to 3 times before failing, with exponential backoff delays between retries.

**Validates: Requirements 7.2**

### Property 12: Execution Summary Logging

*For any* completed scraping execution, a summary log must be generated containing total records attempted, successfully extracted, rejected due to validation, and any errors encountered.

**Validates: Requirements 7.3**

### Property 13: Robots.txt Compliance

*For any* execution of the scraper, if a robots.txt file exists on the FSSAI portal, the scraper must respect the disallowed paths specified in robots.txt and not request those paths.

**Validates: Requirements 8.1**

### Property 14: User-Agent Header Presence

*For any* HTTP request made by the scraper to the FSSAI portal, the request must include a User-Agent header identifying the scraper (e.g., "FSSAI-Restaurant-Scraper/1.0").

**Validates: Requirements 8.2**

### Property 15: Rate Limiting Compliance

*For any* sequence of HTTP requests to the FSSAI portal, the time interval between consecutive requests must be at least the configured rate limit delay (minimum 1 second).

**Validates: Requirements 8.3**

### Property 16: Configuration Management Correctness

*For any* configuration provided (file, CLI arguments, or environment variables), the scraper must validate all configuration values, use defaults for missing values, and apply CLI arguments with highest priority before beginning execution.

**Validates: Requirements 9.1, 9.2, 9.3**

### Property 17: Graceful Error Termination

*For any* fatal error encountered during execution (e.g., portal unavailable after all retries), the scraper must log the error with descriptive context and terminate gracefully without crashing or leaving partial files.

**Validates: Requirements 1.4**

## Testing Strategy

### Dual Testing Approach

The testing strategy combines unit tests and property-based tests for comprehensive coverage:

**Unit Tests**: Verify specific examples, edge cases, and error conditions
- Test individual component functionality in isolation
- Validate error handling and recovery mechanisms
- Test configuration loading and validation
- Test file I/O operations

**Property-Based Tests**: Verify universal properties across all inputs
- Use hypothesis library for Python
- Generate random valid and invalid data
- Test properties hold across diverse inputs
- Minimum 100 iterations per property test

### Unit Testing Focus Areas

1. **Configuration Management**
   - Load valid configuration file
   - Load configuration with missing values (use defaults)
   - Reject invalid configuration values
   - CLI argument override of config file values

2. **Data Validation**
   - Valid records pass validation
   - Records with missing required fields fail validation
   - Invalid email formats are rejected
   - Invalid phone formats are rejected
   - Records with non-matching state are rejected

3. **Deduplication**
   - Duplicate records with same License Number are identified
   - Most recent record is retained for duplicates
   - Non-duplicate records are preserved
   - Duplicate count is accurate

4. **Excel Export**
   - Excel file is created with correct filename pattern
   - Data sheet contains all records with headers
   - Metadata sheet contains accurate statistics
   - Column widths are properly formatted

5. **Error Handling**
   - Network errors trigger retries
   - Retry count is respected
   - Parsing errors are logged and skipped
   - File I/O errors are handled gracefully

### Property-Based Testing Configuration

Each property test will:
- Use hypothesis library with `@given` decorator
- Generate random valid and invalid inputs
- Run minimum 100 iterations (configurable)
- Include tag comment referencing design property
- Tag format: `# Feature: fssai-restaurant-scraper, Property {number}: {property_text}`

### Test Data Generators

```python
# Example generators for property-based testing
@st.composite
def restaurant_records(draw):
    """Generate valid restaurant records"""
    return {
        "business_name": draw(st.text(min_size=1)),
        "license_number": draw(st.text(min_size=1)),
        "license_type": draw(st.text()),
        "business_type": draw(st.text()),
        "district": draw(st.text()),
        "city_town": draw(st.text()),
        "pin_code": draw(st.text()),
        "issue_date": draw(st.text()),
        "valid_till": draw(st.text()),
        "owner_contact": draw(st.text()),
        "mobile": draw(st.text()),
        "email": draw(st.emails()),
        "address": draw(st.text()),
        "state": "Maharashtra",
    }

@st.composite
def invalid_emails(draw):
    """Generate invalid email addresses"""
    return draw(st.text().filter(lambda x: "@" not in x or "." not in x))
```

### Test Coverage Goals

- **Unit Tests**: 80%+ code coverage for core modules
- **Property Tests**: All 14 correctness properties implemented
- **Integration Tests**: End-to-end scraping pipeline with mock data
- **Error Scenarios**: Network failures, parsing errors, validation failures

### Continuous Testing

- Run unit tests on every commit
- Run property tests with 100+ iterations in CI/CD
- Generate coverage reports
- Monitor test execution time

