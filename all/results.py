import pandas as pd
import numpy as np
from datetime import datetime

def extract_year_from_date(date_str):
    """Extract year from date string, handling various formats"""
    if pd.isna(date_str) or date_str == '':
        return None
    
    try:
        # Try to parse the date
        if isinstance(date_str, str):
            # Handle different date formats
            if '-' in date_str:
                return int(date_str.split('-')[0])
            elif '/' in date_str:
                return int(date_str.split('/')[-1])  # Assume year is last part
        return None
    except:
        return None

def get_source_priority(source):
    """Return priority number for source (lower number = higher priority)"""
    source_priorities = {
        '2024': 1,
        'scorecards': 2,
        'npcnews': 3,
        'musclememory': 4
    }
    return source_priorities.get(source.lower(), 999)  # Default low priority for unknown sources

def main():
    print("Reading data files...")
    
    # Read the data files
    try:
        all_clean_df = pd.read_csv('data/all/all_clean.csv')
        events_df = pd.read_csv('data/all/events.csv')
    except Exception as e:
        print(f"Error reading files: {e}")
        return
    
    print(f"Loaded {len(all_clean_df)} rows from all_clean.csv")
    print(f"Loaded {len(events_df)} rows from events.csv")
    
    # Create a mapping from competition name to competition_key
    competition_mapping = {}
    for _, row in events_df.iterrows():
        competition_key = row['competition_key']
        year = row['year']
        key = (competition_key, year)
        competition_mapping[key] = competition_key
    
    print(f"Created competition mapping with {len(competition_mapping)} entries")
    
    # Extract year from start date
    print("Extracting years from start dates...")
    all_clean_df['year'] = all_clean_df['Start Date'].apply(extract_year_from_date)
    
    # Create competition_key column
    print("Creating competition keys...")
    def get_competition_key(row):
        competition = row['Competition']
        year = row['year']
        if pd.isna(competition) or pd.isna(year):
            return competition  # Return original if we can't map
        return competition  # For now, use competition name as key
    
    all_clean_df['competition_name_key'] = all_clean_df.apply(get_competition_key, axis=1)
    
    # Rename competitor name column
    all_clean_df['athlete_name_key'] = all_clean_df['Competitor Name']
    
    # Add source priority for deduplication
    all_clean_df['source_priority'] = all_clean_df['Source'].apply(get_source_priority)
    
    # Select and rename columns
    print("Selecting and ordering columns...")
    results_df = all_clean_df[[
        'year',
        'competition_name_key', 
        'athlete_name_key',
        'Judging 1',
        'Judging 2', 
        'Judging 3',
        'Judging 4',
        'Routine',
        'Total',
        'Place',
        'Division',
        'Division Subtype',
        'Division Level',
        'Source',
        'source_priority'
    ]].copy()
    
    # Remove rows with missing year
    results_df = results_df.dropna(subset=['year'])
    print(f"After removing rows with missing year: {len(results_df)} rows")
    
    # Handle duplicates based on source priority
    print("Handling duplicates based on source priority...")
    
    # Define the columns to check for duplicates
    duplicate_columns = [
        'year', 'competition_name_key', 'athlete_name_key', 
        'Place', 'Division', 'Division Subtype'
    ]
    
    # Sort by source priority (ascending) so higher priority sources come first
    results_df = results_df.sort_values('source_priority')
    
    # Remove duplicates keeping the first occurrence (highest priority source)
    results_df = results_df.drop_duplicates(
        subset=duplicate_columns, 
        keep='first'
    )
    
    print(f"After removing duplicates: {len(results_df)} rows")
    
    # Remove the source_priority column as it was only used for deduplication
    results_df = results_df.drop('source_priority', axis=1)
    
    # Sort by year, competition name, division, and place
    print("Sorting by year, competition name, division, and place...")
    results_df = results_df.sort_values(['year', 'competition_name_key', 'Division', 'Place'])
    
    # Convert numeric columns to integers
    print("Converting numeric columns to integers...")
    numeric_columns = ['year', 'Judging 1', 'Judging 2', 'Judging 3', 'Judging 4', 'Routine', 'Total', 'Place']
    
    for col in numeric_columns:
        if col in results_df.columns:
            # Fill NaN values with 0 for integer conversion
            results_df[col] = results_df[col].fillna(0)
            # Convert to integer, handling any remaining non-numeric values
            try:
                results_df[col] = pd.to_numeric(results_df[col], errors='coerce').fillna(0).astype(int)
            except:
                print(f"Warning: Could not convert column {col} to integers")
    
    print("Numeric conversion completed")
    
    # Save the results
    output_file = 'data/all/results.csv'
    print(f"Saving results to {output_file}...")
    results_df.to_csv(output_file, index=False)
    
    print(f"Successfully created {output_file} with {len(results_df)} rows")
    
    # Print some statistics
    print("\nStatistics:")
    print(f"Year range: {results_df['year'].min()} - {results_df['year'].max()}")
    print(f"Number of competitions: {results_df['competition_name_key'].nunique()}")
    print(f"Number of athletes: {results_df['athlete_name_key'].nunique()}")
    print(f"Number of divisions: {results_df['Division'].nunique()}")
    
    # Show source distribution
    print("\nSource distribution:")
    source_counts = results_df['Source'].value_counts()
    for source, count in source_counts.items():
        print(f"  {source}: {count}")

if __name__ == "__main__":
    main()
