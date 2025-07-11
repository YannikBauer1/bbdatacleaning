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

def get_place_dedup_priority(source):
    """Return priority number for place deduplication (lower number = higher priority)"""
    place_priorities = {
        'npcnews': 1,
        '2024': 2,
        'scorecards': 3,
        'musclememory': 4
    }
    return place_priorities.get(source.lower(), 999)  # Default low priority for unknown sources

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
    
    # Add place deduplication priority
    all_clean_df['place_dedup_priority'] = all_clean_df['Source'].apply(get_place_dedup_priority)
    
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
        'source_priority',
        'place_dedup_priority'
    ]].copy()
    
    # Remove rows with missing year
    results_df = results_df.dropna(subset=['year'])
    print(f"After removing rows with missing year: {len(results_df)} rows")
    
    # Fix rows with place 0 by setting them to the last place of that division in that competition
    print("Fixing rows with place 0...")
    
    # First, ensure Place column is numeric
    results_df['Place'] = pd.to_numeric(results_df['Place'], errors='coerce').fillna(0)
    
    # First, sort by year, competition, division, and place to ensure proper ordering
    results_df = results_df.sort_values(['year', 'competition_name_key', 'Division', 'Division Subtype', 'Place'])
    
    # Group by year, competition, division, and division subtype to find the last place for each group
    def fix_zero_places(group):
        # Find the maximum place in this group (excluding 0)
        max_place = group[group['Place'] > 0]['Place'].max()
        if pd.notna(max_place):
            # Set all places that are 0 to the max place (tied for last place)
            group.loc[group['Place'] == 0, 'Place'] = max_place
        else:
            # If all places are 0, assign sequential places starting from 1
            zero_count = (group['Place'] == 0).sum()
            if zero_count > 0:
                group.loc[group['Place'] == 0, 'Place'] = range(1, zero_count + 1)
        return group
    
    # Apply the fix to each group - include Division Subtype in grouping
    results_df = results_df.groupby(['year', 'competition_name_key', 'Division', 'Division Subtype']).apply(fix_zero_places).reset_index(drop=True)
    
    print(f"Fixed {len(results_df[results_df['Place'] == 0])} rows with place 0")
    
    # Handle duplicates based on source priority
    print("Handling duplicates based on source priority...")
    
    # Define the columns to check for duplicates (INCLUDING Place so we only deduplicate same athlete in same place)
    duplicate_columns = [
        'year', 'competition_name_key', 'athlete_name_key', 
        'Division', 'Division Subtype', 'Place'
    ]
    
    # Sort by source priority (ascending) so higher priority sources come first
    results_df = results_df.sort_values('source_priority')
    
    # Remove duplicates keeping the first occurrence (highest priority source)
    # This will only remove duplicates when the same athlete appears in the same place from different sources
    results_df = results_df.drop_duplicates(
        subset=duplicate_columns, 
        keep='first'
    )
    
    print(f"After removing duplicates: {len(results_df)} rows")
    
    # Store the deduplicated data for later comparison
    deduplicated_df = results_df.copy()
    
    # SECOND DEDUPLICATION: Check for duplicate places within each competition/year/division group
    print("Checking for duplicate places within competition/year/division groups...")
    
    # Work with the dataframe that results from Step 1 (deduplicated_df)
    # Add place deduplication priority to the deduplicated dataframe
    deduplicated_df['place_dedup_priority'] = deduplicated_df['Source'].apply(get_place_dedup_priority)
    
    # Sort by place deduplication priority (ascending) so higher priority sources come first
    deduplicated_df = deduplicated_df.sort_values('place_dedup_priority')
    
    # Group by year, competition, division, division subtype, and place
    def remove_duplicate_places(group):
        if len(group) == 1:
            return group
        
        # Check if all sources are the same
        unique_sources = group['Source'].nunique()
        if unique_sources == 1:
            # All sources are the same, keep all rows
            return group
        else:
            # Different sources, keep only the first (highest priority)
            return group.head(1)
    
    # Apply the place deduplication to each group
    place_deduplicated_df = deduplicated_df.groupby(['year', 'competition_name_key', 'Division', 'Division Subtype', 'Place']).apply(remove_duplicate_places).reset_index(drop=True)
    
    # Handle athlete place conflicts between sources
    # This happens when the same athlete appears in different places in different sources
    # For example, ashley_kaitwasser is 1st in npcnews but 2nd in scorecards
    # print("Handling athlete place conflicts between sources...")
    
    # For each competition/year/division group, determine the best source to use
    # def get_best_source_for_competition(group):
    #     if len(group) == 0:
    #         return group
        
    #     # Find the highest priority source that has data for this competition
    #     available_sources = group['Source'].unique()
    #     source_priorities = {}
        
    #     for source in available_sources:
    #         source_priority = group[group['Source'] == source]['place_dedup_priority'].iloc[0]
    #         source_priorities[source] = source_priority
        
    #     # Get the source with the highest priority (lowest number)
    #     best_source = min(source_priorities, key=source_priorities.get)
        
    #     # Get all athletes from the best source for this competition
    #     best_source_data = original_df[
    #         (original_df['year'] == group['year'].iloc[0]) &
    #         (original_df['competition_name_key'] == group['competition_name_key'].iloc[0]) &
    #         (original_df['Division'] == group['Division'].iloc[0]) &
    #         (original_df['Division Subtype'] == group['Division Subtype'].iloc[0]) &
    #         (original_df['Source'] == best_source)
    #     ]
        
    #     return best_source_data
    
    # Apply the source selection to each competition/year/division group
    # final_results_df = place_deduplicated_df.groupby(['year', 'competition_name_key', 'Division', 'Division Subtype']).apply(get_best_source_for_competition).reset_index(drop=True)
    
    # print(f"After resolving athlete place conflicts: {len(final_results_df)} rows")
    
    # Use the final results as the output
    # results_df = final_results_df.copy()
    
    # Use the place deduplicated data as the final result
    print("Using place deduplicated results as final output...")
    results_df = place_deduplicated_df.copy()
    
    print(f"After combining results: {len(results_df)} rows")
    
    # Remove the priority columns as they were only used for deduplication
    results_df = results_df.drop(['source_priority', 'place_dedup_priority'], axis=1)

    # Remove row with 2010,europa_dallas_pro,julia_ann_kulla,0,0,0,0,0,0,10,figure,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2010) & 
          (results_df['competition_name_key'] == 'europa_dallas_pro') & 
          (results_df['athlete_name_key'] == 'julia_ann_kulla') & 
          (results_df['Place'] == 10))
    ]
    # 2010,europa_phoenix_pro,antoinette_tonie_thompson,0,0,0,0,0,0,7,womensbb,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2010) & 
          (results_df['competition_name_key'] == 'europa_phoenix_pro') & 
          (results_df['athlete_name_key'] == 'antoinette_tonie_thompson') & 
          (results_df['Place'] == 7))
    ]
    # 2010,jacksonville_pro,joanne_murphy,0,0,0,0,0,0,17,figure,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2010) & 
          (results_df['competition_name_key'] == 'jacksonville_pro') & 
          (results_df['athlete_name_key'] == 'joanne_murphy') & 
          (results_df['Place'] == 17))
    ]
    # 2011,jacksonville_pro,angel_manuel_rangel_vargas,0,0,0,0,0,0,6,202_212,202,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2011) & 
          (results_df['competition_name_key'] == 'jacksonville_pro') & 
          (results_df['athlete_name_key'] == 'angel_manuel_rangel_vargas') & 
          (results_df['Place'] == 6))
    ]


    
    # Sort by year, competition name, division, division subtype, and place
    print("Sorting by year, competition name, division, division subtype, and place...")
    results_df = results_df.sort_values(['year', 'competition_name_key', 'Division', 'Division Subtype', 'Place'])
    
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
