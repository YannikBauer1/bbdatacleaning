import pandas as pd
import numpy as np
from datetime import datetime
import os

def create_events_csv():
    """
    Create events.csv from all_clean.csv with the following columns:
    - competition_key: competition name
    - year: extracted from start_date
    - start_date
    - end_date
    - event_city: competition city
    - event_state: competition state
    - event_country: competition country
    
    Priority for data sources:
    1. scorecards (best location and date info)
    2. 2024 (good date info, some location)
    3. npcnews (good date info, limited location)
    4. musclememory (limited info, often Jan 1st dates)
    """
    
    # Read the all_clean.csv file
    print("Reading all_clean.csv...")
    df = pd.read_csv('data/all/all_clean.csv')
    
    # Define the priority order for sources
    source_priority = ['scorecards', '2024', 'npcnews', 'musclememory']
    
    # Group by competition and source to get the best data for each competition
    events_data = []
    
    # Get unique competition-year combinations
    # First, extract year from start date for all rows
    df['year'] = df['Start Date'].apply(lambda x: 
        str(x).split('-')[0] if pd.notna(x) and str(x) != '' and '-' in str(x) else '')
    
    # Create competition-year combinations
    competition_year_combinations = df[['Competition', 'year']].drop_duplicates()
    competition_year_combinations = competition_year_combinations[
        (competition_year_combinations['year'] != '') & 
        (competition_year_combinations['year'] != 'nan')
    ]
    
    print(f"Processing {len(competition_year_combinations)} unique competition-year combinations...")
    
    for _, row in competition_year_combinations.iterrows():
        competition = row['Competition']
        year = row['year']
        
        # Filter data for this specific competition and year
        competition_data = df[
            (df['Competition'] == competition) & 
            (df['year'] == year)
        ]
        
        # Find the best source for this competition-year combination
        best_source = None
        best_data = None
        
        for source in source_priority:
            source_data = competition_data[competition_data['Source'] == source]
            if not source_data.empty:
                best_source = source
                best_data = source_data.iloc[0]  # Take first row from this source
                break
        
        if best_data is not None:
            # Handle location data - use empty strings if not available
            event_city = best_data['Location City'] if pd.notna(best_data['Location City']) else ''
            event_state = best_data['Location State'] if pd.notna(best_data['Location State']) else ''
            event_country = best_data['Location Country'] if pd.notna(best_data['Location Country']) else ''
            
            # Handle dates - use empty strings if not available or if it's Jan 1st from musclememory
            start_date_str = ''
            end_date_str = ''
            
            if pd.notna(best_data['Start Date']) and best_data['Start Date'] != '':
                start_date_str = str(best_data['Start Date'])
                # If it's musclememory and the date is Jan 1st, make it empty
                if best_source == 'musclememory' and start_date_str.endswith('-01-01'):
                    start_date_str = ''
            
            if pd.notna(best_data['End Date']) and best_data['End Date'] != '':
                end_date_str = str(best_data['End Date'])
                # If it's musclememory and the date is Jan 1st, make it empty
                if best_source == 'musclememory' and end_date_str.endswith('-01-01'):
                    end_date_str = ''
            
            events_data.append({
                'competition_key': competition,
                'year': year,
                'start_date': start_date_str,
                'end_date': end_date_str,
                'event_city': event_city,
                'event_state': event_state,
                'event_country': event_country
            })
    
    # Create the events DataFrame
    events_df = pd.DataFrame(events_data)
    
    # Sort by year and competition name
    events_df = events_df.sort_values(['year', 'competition_key'])
    
    # Save to CSV
    output_path = 'data/all/events.csv'
    events_df.to_csv(output_path, index=False)
    
    print(f"Events CSV created successfully at {output_path}")
    print(f"Total events: {len(events_df)}")
    
    # Print some statistics
    print("\nStatistics:")
    print(f"Events with start_date: {len(events_df[events_df['start_date'] != ''])}")
    print(f"Events with end_date: {len(events_df[events_df['end_date'] != ''])}")
    print(f"Events with city: {len(events_df[events_df['event_city'] != ''])}")
    print(f"Events with state: {len(events_df[events_df['event_state'] != ''])}")
    print(f"Events with country: {len(events_df[events_df['event_country'] != ''])}")
    
    # Print year distribution
    print(f"\nYear range: {events_df['year'].min()} - {events_df['year'].max()}")
    print(f"Unique competitions: {events_df['competition_key'].nunique()}")
    
    return events_df

if __name__ == "__main__":
    events_df = create_events_csv()
