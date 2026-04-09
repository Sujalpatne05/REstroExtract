"""
Run the scraper with real Maharashtra restaurant data
"""
import pandas as pd
from src.orchestrator import ScraperOrchestrator
from src.config import ConfigManager
from src.logger import LoggerSystem
from src.models import RestaurantRecord
from src.validator import DataValidator
from src.deduplicator import DeduplicatorEngine
from src.exporter import ExporterEngine

print('Running FSSAI Scraper with Real Maharashtra Data')
print('=' * 70)

# Read the CSV file
print('Loading Maharashtra restaurant data...')
df = pd.read_csv('maharashtra_restaurants_sample.csv')
print(f'Loaded {len(df)} records')

# Convert to our format
records = []
for _, row in df.iterrows():
    record = {
        'business_name': str(row['Business Name']),
        'license_number': str(row['License Number']),
        'license_type': str(row['License Type']),
        'business_type': str(row['Business Type']),
        'district': str(row['District']),
        'city_town': str(row['City/Town']),
        'pin_code': str(row['Pin Code']),
        'issue_date': str(row['Issue Date']),
        'valid_till': str(row['Valid Till']),
        'owner_contact': str(row['Owner/Contact']),
        'mobile': str(row['Mobile']),
        'email': str(row['Email']),
        'address': str(row['Address']),
        'state': str(row['State']),
    }
    records.append(record)

print(f'Converted to {len(records)} records')

# Initialize components
config = ConfigManager(cli_args={
    'target_state': 'Maharashtra',
    'output_directory': './output',
    'append_mode': True,
})
config.load_config()

logger = LoggerSystem(log_file='./logs/scraper.log', log_level='INFO')
validator = DataValidator(target_state='Maharashtra')
deduplicator = DeduplicatorEngine()
exporter = ExporterEngine(config=config, logger=logger)

# Validate records
print('\nValidating records...')
validated_records = []
rejected_count = 0
for record in records:
    if validator.validate_record(record):
        validated_records.append(record)
    else:
        rejected_count += 1

print(f'Validated: {len(validated_records)}, Rejected: {rejected_count}')

# Deduplicate
print('Deduplicating records...')
deduplicated_records, duplicates_removed = deduplicator.deduplicate(validated_records)
print(f'After deduplication: {len(deduplicated_records)}, Removed: {duplicates_removed}')

# Export
print('Exporting to Excel...')
stats = {
    'total_extracted': len(records),
    'total_validated': len(validated_records),
    'total_rejected': rejected_count,
    'total_duplicates_removed': duplicates_removed,
}
output_file = exporter.export_to_excel(deduplicated_records, stats)
print(f'Exported to: {output_file}')

print('\n' + '=' * 70)
print('EXECUTION SUMMARY')
print('=' * 70)
print(f'Status: SUCCESS')
print(f'Total Records Extracted: {len(records)}')
print(f'Total Records Validated: {len(validated_records)}')
print(f'Total Records Rejected: {rejected_count}')
print(f'Total Duplicates Removed: {duplicates_removed}')
print(f'Final Records in Excel: {len(deduplicated_records)}')
print('=' * 70)
