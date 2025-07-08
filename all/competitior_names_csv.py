import json
import pandas as pd
import csv
from collections import defaultdict

def load_competitor_names():
    """Load the competitor names from JSON file"""
    # Try different possible paths
    possible_paths = [
        '../keys/competitor_names.json',  # From all/ directory
        'keys/competitor_names.json',     # From root directory
        'all/keys/competitor_names.json'  # Alternative path
    ]
    
    for path in possible_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            continue
    
    raise FileNotFoundError("Could not find competitor_names.json in any expected location")

def load_all_clean_data():
    """Load the all_clean.csv data"""
    # Try different possible paths
    possible_paths = [
        '../data/all/all_clean.csv',  # From all/ directory
        'data/all/all_clean.csv',     # From root directory
        'all/data/all/all_clean.csv'  # Alternative path
    ]
    
    for path in possible_paths:
        try:
            return pd.read_csv(path)
        except FileNotFoundError:
            continue
    
    raise FileNotFoundError("Could not find all_clean.csv in any expected location")

def get_shortest_and_longest_names(names_array):
    """Get the shortest and longest names from an array of names"""
    if not names_array:
        return "", ""
    
    # Sort by length to get shortest and longest
    sorted_names = sorted(names_array, key=len)
    return sorted_names[0], sorted_names[-1]

def consolidate_locations(locations):
    """Consolidate location objects, keeping only the most complete ones and removing duplicates"""
    if not locations:
        return []
    
    # First, remove exact duplicates by converting to tuples for hashing
    seen = set()
    unique_locations = []
    for loc in locations:
        # Create a tuple representation for hashing
        loc_tuple = (loc.get('city', ''), loc.get('state', ''), loc.get('country', ''))
        if loc_tuple not in seen:
            seen.add(loc_tuple)
            unique_locations.append(loc)
    
    # Group by country and find the most complete entries
    consolidated = []
    
    # Group by country
    by_country = defaultdict(list)
    for loc in unique_locations:
        country = loc.get('country', '')
        by_country[country].append(loc)
    
    for country, country_locs in by_country.items():
        if not country:
            # If no country, keep all as separate entries
            consolidated.extend(country_locs)
            continue
        
        # For each country, find the most complete entries
        # Group by state within the country
        by_state = defaultdict(list)
        for loc in country_locs:
            state = loc.get('state', '')
            by_state[state].append(loc)
        
        # For each state group, find the most complete entries
        for state, state_locs in by_state.items():
            if not state:
                # If no state, check if we have more complete entries for this country
                # Only keep country-only entries if there are no state entries for this country
                has_state_entries = any(loc.get('state', '') for loc in country_locs)
                if not has_state_entries:
                    consolidated.extend(state_locs)
                continue
            
            # Group by city within the state
            by_city = defaultdict(list)
            for loc in state_locs:
                city = loc.get('city', '')
                by_city[city].append(loc)
            
            # For each city group, find the most complete entries
            for city, city_locs in by_city.items():
                if not city:
                    # If no city, check if we have more complete entries for this state
                    # Only keep state-only entries if there are no city entries for this state
                    has_city_entries = any(loc.get('city', '') for loc in state_locs)
                    if not has_city_entries:
                        consolidated.extend(city_locs)
                    continue
                
                # For each city, keep only the most complete entry
                best_loc = max(city_locs, key=lambda x: sum(1 for v in x.values() if v))
                consolidated.append(best_loc)
    
    return consolidated

def create_competitor_csv():
    """Create the CSV file with competitor data"""
    
    # Load data
    competitor_names = load_competitor_names()
    all_clean_df = load_all_clean_data()
    
    # Create a mapping of competitor names to their location data
    competitor_locations = defaultdict(list)
    
    # Process all_clean.csv to extract location data for each competitor
    for _, row in all_clean_df.iterrows():
        competitor_name = row['Competitor Name']
        if pd.isna(competitor_name) or competitor_name == '':
            continue
            
        # Create location object
        location = {
            'city': row['Competitor City'] if pd.notna(row['Competitor City']) else '',
            'state': row['Competitor State'] if pd.notna(row['Competitor State']) else '',
            'country': row['Competitor Country'] if pd.notna(row['Competitor Country']) else ''
        }
        
        # Only add if at least one location field is not empty
        if any(location.values()):
            competitor_locations[competitor_name].append(location)
    
    # Create the CSV data
    csv_data = []
    
    for name_key, names_array in competitor_names.items():
        # Get shortest and longest names
        name_short, name_long = get_shortest_and_longest_names(names_array)
        
        # Get location data for this competitor
        locations = []
        # First try to match by the key (name_key)
        if name_key in competitor_locations:
            locations.extend(competitor_locations[name_key])
        # Then try to match by any of the actual names
        for name in names_array:
            if name in competitor_locations:
                locations.extend(competitor_locations[name])
        
        # Consolidate locations
        consolidated_locations = consolidate_locations(locations)
        
        # Convert to JSON string
        location_json = json.dumps(consolidated_locations) if consolidated_locations else ''
        
        # Add to CSV data
        csv_data.append({
            'name_key': name_key,
            'name_short': name_short,
            'name_long': name_long,
            'nickname': '',  # Empty as requested
            'location': location_json
        })
    
    # Write to CSV
    # Try to determine the correct output path
    try:
        # Test if we can write to the relative path from all/ directory
        test_path = '../data/all/competitor_names_processed.csv'
        with open(test_path, 'w') as f:
            pass
        output_file = test_path
    except:
        try:
            # Test if we can write to the path from root directory
            test_path = 'data/all/competitor_names_processed.csv'
            with open(test_path, 'w') as f:
                pass
            output_file = test_path
        except:
            # Fallback to current directory
            output_file = 'competitor_names_processed.csv'
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name_key', 'name_short', 'name_long', 'nickname', 'location']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in csv_data:
            writer.writerow(row)
    
    print(f"CSV file created: {output_file}")
    print(f"Total competitors processed: {len(csv_data)}")

if __name__ == "__main__":
    create_competitor_csv()
