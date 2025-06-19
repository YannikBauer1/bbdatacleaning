import pandas as pd
import json
from collections import defaultdict
from datetime import datetime

# Read the competition names from the JSON file
with open('all/comp_name_dir.json', 'r') as f:
    competition_names = json.load(f)

# Create a set of all competition names (including variations)
all_competition_names = set()
for variations in competition_names.values():
    all_competition_names.update(variations)

# Read the CSV file in chunks
chunk_size = 10000
competition_data = defaultdict(lambda: defaultdict(lambda: {'divisions': set(), 'location': ''}))

def clean_year(year_val):
    if pd.isna(year_val):
        return 0
    # Convert to string, remove decimal part if it exists, and strip whitespace
    return str(year_val).split('.')[0].strip()

def year_to_int(year):
    try:
        return int(year)
    except (ValueError, TypeError):
        return 0

# Process the CSV file in chunks
for chunk in pd.read_csv('all/all_clean.csv', chunksize=chunk_size):
    # Filter rows where the competition name is in our set
    mask = chunk['Competition'].isin(all_competition_names)
    filtered_chunk = chunk[mask]
    
    # For each matching row, add the data to our dictionary
    for _, row in filtered_chunk.iterrows():
        competition = row['Competition']
        date = row.get('Date', '')
        year = clean_year(row.get('Year', ''))
        location = row.get('Location', '')
        source = row.get('Source', '')
        division = row.get('Division', '')
        
        # Create a unique key for this appearance
        appearance_key = (year, date, source)
        
        # Store the location if it exists
        if pd.notna(location) and location:
            competition_data[competition][appearance_key]['location'] = location
        
        # Add division to the set if it exists
        if pd.notna(division) and division:
            competition_data[competition][appearance_key]['divisions'].add(division)

# Create the final JSON structure
final_data = {}
for main_name, variations in competition_names.items():
    final_data[main_name] = {
        'variations': variations,
        'appearances': []
    }
    
    # Add all appearances for each variation
    for variation in variations:
        if variation in competition_data:
            for (year, date, source), data in competition_data[variation].items():
                final_data[main_name]['appearances'].append({
                    'year': year,
                    'date': date,
                    'location': data['location'],
                    'source': source,
                    'divisions': sorted(list(data['divisions']))  # Convert set to sorted list
                })
    
    # Sort appearances by year
    final_data[main_name]['appearances'].sort(key=lambda x: year_to_int(x['year']))

# Write the results to a new JSON file
with open('all/competition_details.json', 'w') as f:
    json.dump(final_data, f, indent=2)