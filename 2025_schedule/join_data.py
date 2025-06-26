import pandas as pd
import re
from datetime import datetime

def clean_competition_url(url):
    """Clean and normalize competition URLs for comparison"""
    if pd.isna(url) or url == '':
        return ''
    # Remove trailing slashes and normalize
    url = str(url).strip().rstrip('/')
    return url.lower()

def extract_date_from_string(date_str):
    """Extract date information from various date formats"""
    if pd.isna(date_str) or date_str == '':
        return None
    
    date_str = str(date_str).strip()
    
    # Check for 2024 in the date string
    if '2024' in date_str:
        return '2024'
    
    # Try to extract year from various formats
    year_patterns = [
        r'(\d{4})',  # Any 4-digit year
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})',  # Month Day
        r'(\d{1,2})[/-](\d{1,2})',  # MM/DD or MM-DD
    ]
    
    for pattern in year_patterns:
        match = re.search(pattern, date_str, re.IGNORECASE)
        if match:
            if len(match.groups()) == 1 and len(match.group(1)) == 4:
                return match.group(1)
            elif len(match.groups()) == 2:
                # If we find month/day but no year, assume 2025
                return '2025'
    
    return None

def main():
    # Read the updated schedule CSV file
    print("Reading schedule CSV file...")
    schedule_df = pd.read_csv('data/schedule.csv')
    
    print(f"Schedule CSV: {len(schedule_df)} entries")
    
    # Clean competition names by removing "2025" prefix
    print("\nCleaning competition names...")
    schedule_df['Competition Name'] = schedule_df['Competition Name'].str.replace(r'^2025\s*', '', regex=True, case=False)
    
    # Convert competition names to title case (first letter of each word capitalized)
    schedule_df['Competition Name'] = schedule_df['Competition Name'].str.title()
    
    # Filter out entries from schedule that have 2024 in Start Date
    print("\nFiltering out 2024 entries from schedule...")
    original_schedule_count = len(schedule_df)
    
    # Check Start Date column for 2024
    schedule_df['year_from_start_date'] = schedule_df['Start Date'].apply(extract_date_from_string)
    schedule_df_filtered = schedule_df[schedule_df['year_from_start_date'] != '2024'].copy()
    
    print(f"Removed {original_schedule_count - len(schedule_df_filtered)} entries with 2024 dates")
    print(f"Schedule after filtering: {len(schedule_df_filtered)} entries")
    
    # Remove the temporary column
    schedule_df_filtered = schedule_df_filtered.drop('year_from_start_date', axis=1)
    
    # Normalize competition names for better duplicate detection (remove extra spaces, normalize punctuation)
    schedule_df_filtered['Competition Name Normalized'] = schedule_df_filtered['Competition Name'].str.replace(r'\s+', ' ', regex=True).str.strip()
    schedule_df_filtered['Competition Name Normalized'] = schedule_df_filtered['Competition Name Normalized'].str.replace(r'[.,]', '', regex=True)
    
    # Check for duplicated competition names BEFORE reordering columns
    print(f"\nDuplicate Competition Names Check:")
    duplicates = schedule_df_filtered[schedule_df_filtered.duplicated(subset=['Competition Name Normalized'], keep=False)]
    if len(duplicates) > 0:
        print(f"- Found {len(duplicates)} entries with duplicate competition names:")
        duplicate_names = duplicates['Competition Name Normalized'].value_counts()
        for name, count in duplicate_names.items():
            print(f"  * '{name}' appears {count} times")
        
        # Consolidate duplicates by combining divisions and keeping best data
        print(f"\nConsolidating duplicate competitions...")
        consolidated_df = schedule_df_filtered.copy()
        
        # Group by normalized competition name and consolidate
        for comp_name in duplicate_names.index:
            comp_entries = consolidated_df[consolidated_df['Competition Name Normalized'] == comp_name]
            
            if len(comp_entries) > 1:
                # Combine divisions
                all_divisions = comp_entries['Division'].dropna().unique()
                combined_divisions = ', '.join(all_divisions)
                
                # Keep the first entry and update it with combined data
                first_idx = comp_entries.index[0]
                
                # Update division with combined divisions
                consolidated_df.loc[first_idx, 'Division'] = combined_divisions
                
                # For other fields, keep the first non-empty value
                for col in consolidated_df.columns:
                    if col not in ['Division', 'Competition Name Normalized']:
                        non_empty_values = comp_entries[col].dropna()
                        if len(non_empty_values) > 0:
                            consolidated_df.loc[first_idx, col] = non_empty_values.iloc[0]
                
                # Remove the duplicate entries
                duplicate_indices = comp_entries.index[1:]
                consolidated_df = consolidated_df.drop(duplicate_indices)
        
        schedule_df_filtered = consolidated_df
        print(f"- Consolidated {len(duplicates) - len(duplicate_names)} duplicate entries")
        print(f"- Final dataset after consolidation: {len(schedule_df_filtered)} entries")
    else:
        print("- No duplicate competition names found")
    
    # Remove the temporary normalized column
    schedule_df_filtered = schedule_df_filtered.drop('Competition Name Normalized', axis=1)
    
    # Add missing columns with default values
    schedule_df_filtered['Competition Level'] = 'IFBB Pro'  # Default value
    schedule_df_filtered['Promoter Email'] = ''  # Empty string for missing data
    schedule_df_filtered['Promoter Website'] = ''  # Empty string for missing data
    schedule_df_filtered['Description'] = ''  # Empty string for missing data
    schedule_df_filtered['Source'] = 'schedule'
    
    # Reorder columns as requested
    column_order = [
        'Start Date',
        'End Date', 
        'Competition Name',
        'Competition URL',
        'Division',
        'Division Type',
        'Competition Level',
        'Description',
        'Location City',
        'Location State', 
        'Location Country',
        'Promoter Name',
        'Promoter Email',
        'Promoter Website'
    ]
    
    # Reorder the columns
    schedule_df_filtered = schedule_df_filtered[column_order]
    
    # Sort by Start Date for better organization (earliest dates first)
    schedule_df_filtered = schedule_df_filtered.sort_values('Start Date', ascending=True, na_position='last')
    
    print(f"Final processed dataset: {len(schedule_df_filtered)} entries")
    
    # Save the processed data (after consolidation)
    output_file = 'data/all_competitions.csv'
    schedule_df_filtered.to_csv(output_file, index=False)
    print(f"\nProcessed data saved to: {output_file}")
    
    # Print summary
    print("\nSummary:")
    print(f"- Original schedule entries: {original_schedule_count}")
    print(f"- Schedule entries after filtering 2024: {len(schedule_df_filtered)}")
    print(f"- Total processed entries: {len(schedule_df_filtered)}")
    
    # Print some statistics about the data
    print(f"\nData Statistics:")
    print(f"- Competitions with URLs: {schedule_df_filtered['Competition URL'].notna().sum()}")
    print(f"- Competitions with promoters: {schedule_df_filtered['Promoter Name'].notna().sum()}")
    print(f"- Competitions with locations: {schedule_df_filtered['Location City'].notna().sum()}")
    print(f"- Unique divisions: {schedule_df_filtered['Division'].nunique()}")
    print(f"- Unique division types: {schedule_df_filtered['Division Type'].nunique()}")

if __name__ == "__main__":
    main()
