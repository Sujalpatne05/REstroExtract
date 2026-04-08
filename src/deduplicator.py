"""
Deduplicator Engine Module

This module provides deduplication functionality for restaurant records.
It identifies and removes duplicate records based on License Number,
keeping only the most recent record for each license.

Requirements: 10.1, 10.2
"""

from typing import Dict, List, Tuple, Any
from datetime import datetime


class DeduplicatorEngine:
    """
    Engine for deduplicating restaurant records.
    
    Deduplication is based on License Number, with the most recent
    record (by Issue Date) retained for each license.
    """
    
    def __init__(self):
        """Initialize the DeduplicatorEngine."""
        pass
    
    def deduplicate(
        self, records: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Remove duplicate records by License Number.
        
        For each group of records with the same License Number,
        keeps only the record with the most recent Issue Date.
        
        Args:
            records: List of restaurant records to deduplicate
            
        Returns:
            Tuple of (deduplicated_records, duplicate_count)
            - deduplicated_records: List of unique records
            - duplicate_count: Number of duplicate records removed
            
        Requirements: 10.1, 10.2
        """
        if not records:
            return [], 0
        
        # Group records by License Number
        grouped = self.find_duplicates_by_license(records)
        
        deduplicated = []
        duplicate_count = 0
        
        # For each group, keep only the most recent record
        for license_number, group in grouped.items():
            if len(group) > 1:
                # This is a duplicate group
                most_recent = self.keep_most_recent(group)
                deduplicated.append(most_recent)
                duplicate_count += len(group) - 1
            else:
                # Single record, no duplicates
                deduplicated.append(group[0])
        
        return deduplicated, duplicate_count
    
    def find_duplicates_by_license(
        self, records: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group records by License Number.
        
        Args:
            records: List of restaurant records
            
        Returns:
            Dictionary mapping License Number to list of records
            
        Requirements: 10.1
        """
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        
        for record in records:
            license_number = record.get("license_number", "")
            if license_number not in grouped:
                grouped[license_number] = []
            grouped[license_number].append(record)
        
        return grouped
    
    def keep_most_recent(
        self, duplicates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Select the record with the most recent Issue Date.
        
        Args:
            duplicates: List of duplicate records with same License Number
            
        Returns:
            The record with the most recent Issue Date
            
        Requirements: 10.2
        """
        if not duplicates:
            return {}
        
        if len(duplicates) == 1:
            return duplicates[0]
        
        # Sort by Issue Date (most recent first)
        # Handle various date formats gracefully
        def parse_date(record: Dict[str, Any]) -> datetime:
            """Parse issue date from record, return min date if parsing fails."""
            issue_date_str = record.get("issue_date", "")
            if not issue_date_str:
                return datetime.min
            
            # Try common date formats
            formats = [
                "%d-%m-%Y",
                "%d/%m/%Y",
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%d-%b-%Y",
                "%d %b %Y",
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(issue_date_str, fmt)
                except ValueError:
                    continue
            
            # If no format matches, return min date
            return datetime.min
        
        most_recent = max(duplicates, key=parse_date)
        return most_recent
