"""Data models for FSSAI Restaurant Scraper.

This module defines the core data structures used throughout the scraper:
- RestaurantRecord: Represents a single restaurant license record
- ExtractionStats: Tracks extraction statistics and status
"""

from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List


@dataclass
class RestaurantRecord:
    """Represents a single restaurant license record from FSSAI portal.
    
    Contains all 14 required fields for restaurant license information.
    Provides methods to convert to/from dictionary format for serialization.
    
    Attributes:
        business_name: Name of the restaurant business
        license_number: Unique FSSAI license identifier
        license_type: Type of license (e.g., Central License, State License)
        business_type: Classification of food business (e.g., Restaurant, Cafe)
        district: District where restaurant is located
        city_town: City or town name
        pin_code: Postal code
        issue_date: Date when license was issued
        valid_till: Date when license expires
        owner_contact: Contact person name
        mobile: Mobile phone number
        email: Email address
        address: Full business address
        state: State where restaurant is located
    """
    
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
        """Convert RestaurantRecord to dictionary.
        
        Returns:
            Dictionary representation of the record with all fields.
        """
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RestaurantRecord':
        """Create RestaurantRecord from dictionary.
        
        Args:
            data: Dictionary containing all required fields
            
        Returns:
            RestaurantRecord instance initialized with dictionary values
            
        Raises:
            TypeError: If required fields are missing from dictionary
            KeyError: If dictionary keys don't match field names
        """
        return cls(**data)


@dataclass
class ExtractionStats:
    """Tracks extraction statistics and status for a scraping execution.
    
    Records metrics about the scraping process including counts of attempted,
    extracted, validated, and rejected records, as well as any errors encountered.
    
    Attributes:
        total_attempted: Total number of records attempted to extract
        total_extracted: Total number of records successfully extracted
        total_validated: Total number of records that passed validation
        total_rejected: Total number of records rejected during validation
        total_duplicates_removed: Total number of duplicate records removed
        extraction_status: Overall status of extraction (Pending, Success, Partial, Failed)
        errors: List of error messages encountered during extraction
    """
    
    total_attempted: int = 0
    total_extracted: int = 0
    total_validated: int = 0
    total_rejected: int = 0
    total_duplicates_removed: int = 0
    extraction_status: str = "Pending"
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ExtractionStats to dictionary.
        
        Returns:
            Dictionary representation of the statistics with all fields.
        """
        return asdict(self)
