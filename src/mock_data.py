"""
Mock Data Generator for FSSAI Restaurant Scraper

Provides realistic test data for the scraper when the FSSAI portal is unavailable.
This allows end-to-end testing of the scraper pipeline.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import random


class MockDataGenerator:
    """Generate realistic mock restaurant data for testing"""
    
    # Sample restaurant names
    RESTAURANT_NAMES = [
        "Taj Mahal Restaurant",
        "Spice Garden",
        "Mumbai Masala",
        "Coastal Delights",
        "Maharaja's Kitchen",
        "Flavors of India",
        "The Golden Fork",
        "Curry House",
        "Tandoori Palace",
        "Bombay Bites",
        "Saffron Dreams",
        "Royal Feast",
        "Namaste Kitchen",
        "Spice Route",
        "Maharashtrian Cuisine",
    ]
    
    # Sample business types
    BUSINESS_TYPES = [
        "Restaurant",
        "Cafe",
        "Fast Food",
        "Bakery",
        "Cloud Kitchen",
        "Catering",
        "Food Truck",
        "Confectionery",
    ]
    
    # Sample districts in Maharashtra
    DISTRICTS = [
        "Mumbai",
        "Pune",
        "Nagpur",
        "Aurangabad",
        "Nashik",
        "Kolhapur",
        "Solapur",
        "Sangli",
        "Satara",
        "Ratnagiri",
    ]
    
    # Sample cities
    CITIES = {
        "Mumbai": ["Mumbai", "Thane", "Navi Mumbai"],
        "Pune": ["Pune", "Pimpri-Chinchwad"],
        "Nagpur": ["Nagpur", "Wardha"],
        "Aurangabad": ["Aurangabad", "Paithan"],
        "Nashik": ["Nashik", "Malegaon"],
        "Kolhapur": ["Kolhapur", "Ichalkaranji"],
        "Solapur": ["Solapur", "Pandharpur"],
        "Sangli": ["Sangli", "Miraj"],
        "Satara": ["Satara", "Karad"],
        "Ratnagiri": ["Ratnagiri", "Chiplun"],
    }
    
    # License types
    LICENSE_TYPES = [
        "Central License",
        "State License",
        "FSSAI Registration",
    ]
    
    @staticmethod
    def generate_license_number() -> str:
        """Generate a realistic FSSAI license number"""
        # Format: 10XXXXXXXXXXXXX (10 digits + 5 alphanumeric)
        return f"10{random.randint(10000000000, 99999999999)}"
    
    @staticmethod
    def generate_phone() -> str:
        """Generate a realistic Indian phone number"""
        return f"9{random.randint(100000000, 999999999)}"
    
    @staticmethod
    def generate_email(name: str) -> str:
        """Generate a realistic email address"""
        name_part = name.lower().replace(" ", "").replace("'", "")[:15]
        domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "restaurant.com"])
        return f"{name_part}{random.randint(1, 999)}@{domain}"
    
    @staticmethod
    def generate_pin_code(district: str) -> str:
        """Generate a realistic Maharashtra pin code"""
        # Maharashtra pin codes start with 4
        return f"4{random.randint(10000, 99999)}"
    
    @staticmethod
    def generate_date(days_ago: int = 365) -> str:
        """Generate a date in DD/MM/YYYY format"""
        date = datetime.now() - timedelta(days=random.randint(0, days_ago))
        return date.strftime("%d/%m/%Y")
    
    @staticmethod
    def generate_valid_till(issue_date_str: str) -> str:
        """Generate a valid till date (1 year after issue date)"""
        issue_date = datetime.strptime(issue_date_str, "%d/%m/%Y")
        valid_till = issue_date + timedelta(days=365)
        return valid_till.strftime("%d/%m/%Y")
    
    @classmethod
    def generate_restaurant_record(cls, state: str = "Maharashtra") -> Dict[str, Any]:
        """Generate a single realistic restaurant record"""
        
        district = random.choice(cls.DISTRICTS)
        city = random.choice(cls.CITIES.get(district, [district]))
        business_name = random.choice(cls.RESTAURANT_NAMES)
        
        issue_date = cls.generate_date(days_ago=730)  # Within last 2 years
        
        record = {
            "business_name": business_name,
            "license_number": cls.generate_license_number(),
            "license_type": random.choice(cls.LICENSE_TYPES),
            "business_type": random.choice(cls.BUSINESS_TYPES),
            "district": district,
            "city_town": city,
            "pin_code": cls.generate_pin_code(district),
            "issue_date": issue_date,
            "valid_till": cls.generate_valid_till(issue_date),
            "owner_contact": f"Owner {random.randint(1, 999)}",
            "mobile": cls.generate_phone(),
            "email": cls.generate_email(business_name),
            "address": f"{random.randint(1, 500)} {business_name} Street, {city}, {district}",
            "state": state,
        }
        
        return record
    
    @classmethod
    def generate_records(cls, count: int = 50, state: str = "Maharashtra") -> List[Dict[str, Any]]:
        """Generate multiple realistic restaurant records"""
        records = []
        for _ in range(count):
            records.append(cls.generate_restaurant_record(state))
        return records
    
    @classmethod
    def generate_with_duplicates(cls, count: int = 50, duplicate_count: int = 5, 
                                 state: str = "Maharashtra") -> List[Dict[str, Any]]:
        """Generate records with some duplicates for testing deduplication"""
        records = cls.generate_records(count - duplicate_count, state)
        
        # Add duplicates of existing records
        if records:
            for _ in range(duplicate_count):
                original = random.choice(records)
                # Create a duplicate with same license number but different issue date
                duplicate = original.copy()
                duplicate["issue_date"] = cls.generate_date(days_ago=365)
                duplicate["valid_till"] = cls.generate_valid_till(duplicate["issue_date"])
                records.append(duplicate)
        
        return records
    
    @classmethod
    def generate_with_invalid_records(cls, count: int = 50, invalid_count: int = 5,
                                      state: str = "Maharashtra") -> List[Dict[str, Any]]:
        """Generate records with some invalid data for testing validation"""
        records = cls.generate_records(count - invalid_count, state)
        
        # Add invalid records
        for _ in range(invalid_count):
            invalid_record = cls.generate_restaurant_record(state)
            
            # Make it invalid in different ways
            invalid_type = random.choice([
                "missing_name",
                "missing_license",
                "invalid_email",
                "invalid_phone",
                "wrong_state",
            ])
            
            if invalid_type == "missing_name":
                invalid_record["business_name"] = ""
            elif invalid_type == "missing_license":
                invalid_record["license_number"] = ""
            elif invalid_type == "invalid_email":
                invalid_record["email"] = "not-an-email"
            elif invalid_type == "invalid_phone":
                invalid_record["mobile"] = "abc123"
            elif invalid_type == "wrong_state":
                invalid_record["state"] = "Karnataka"
            
            records.append(invalid_record)
        
        return records
