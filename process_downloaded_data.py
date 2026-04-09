"""
Process downloaded FSSAI restaurant data and convert to our Excel format
"""
import pandas as pd
import argparse
import sys
from datetime import datetime
from pathlib import Path

def process_csv_data(filepath, state='Maharashtra'):
    """
    Process downloaded CSV/Excel data and convert to our format
    """
    print(f'Processing file: {filepath}')
    print('=' * 70)
    
    try:
        # Read the file
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filepath)
        else:
            print('Error: File must be CSV or Excel')
            return False
        
        print(f'Loaded {len(df)} records')
        print(f'Columns: {list(df.columns)}')
        
        # Map common column names to our format
        column_mapping = {
            'business_name': ['Business Name', 'Restaurant Name', 'Name', 'business_name'],
            'license_number': ['License Number', 'License No', 'License', 'license_number'],
            'license_type': ['License Type', 'Type', 'license_type'],
            'business_type': ['Business Type', 'Category', 'business_type'],
            'district': ['District', 'district'],
            'city_town': ['City', 'Town', 'City/Town', 'city_town'],
            'pin_code': ['Pin Code', 'Pincode', 'PIN', 'pin_code'],
            'issue_date': ['Issue Date', 'Issued Date', 'issue_date'],
            'valid_till': ['Valid Till', 'Expiry Date', 'valid_till'],
            'owner_contact': ['Owner', 'Contact Person', 'owner_contact'],
            'mobile': ['Mobile', 'Phone', 'Contact', 'mobile'],
            'email': ['Email', 'Email Address', 'email'],
            'address': ['Address', 'Full Address', 'address'],
            'state': ['State', 'state'],
        }
        
        # Try to map columns
        mapped_df = pd.DataFrame()
        for our_col, possible_names in column_mapping.items():
            for possible_name in possible_names:
                if possible_name in df.columns:
                    mapped_df[our_col] = df[possible_name]
                    print(f'Mapped: {our_col} <- {possible_name}')
                    break
            if our_col not in mapped_df.columns:
                # Try case-insensitive match
                for col in df.columns:
                    if col.lower() == our_col.lower():
                        mapped_df[our_col] = df[col]
                        print(f'Mapped: {our_col} <- {col} (case-insensitive)')
                        break
        
        # Fill missing state
        if 'state' not in mapped_df.columns or mapped_df['state'].isna().all():
            mapped_df['state'] = state
        
        # Save to Excel in our format
        output_file = f'output/FSSAI_Restaurants_{state}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        # Create output directory if needed
        Path('output').mkdir(exist_ok=True)
        
        # Write to Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            mapped_df.to_excel(writer, sheet_name='Data', index=False)
        
        print(f'\nSuccess! Saved {len(mapped_df)} records to:')
        print(f'{output_file}')
        
        return True
        
    except Exception as e:
        print(f'Error: {str(e)}')
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Process downloaded FSSAI restaurant data'
    )
    parser.add_argument('--file', required=True, help='Path to CSV or Excel file')
    parser.add_argument('--state', default='Maharashtra', help='State name')
    
    args = parser.parse_args()
    
    success = process_csv_data(args.file, args.state)
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
