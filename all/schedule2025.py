import csv
import json
import os
from datetime import datetime

def get_full_state_name(state_abbr):
    """
    Convert state abbreviations to full state names.
    Returns the full name if found, otherwise returns the original abbreviation.
    """
    state_mapping = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
        'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
        'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
        'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
        'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
        'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
        'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
    }
    
    if state_abbr and state_abbr.strip():
        return state_mapping.get(state_abbr.strip().upper(), state_abbr)
    return state_abbr

def find_competition_key(competition_name, competitions_data):
    """
    Find the competition key from the competitions.json file based on the competition name.
    Returns the key if found, otherwise returns the original name.
    """
    # Flatten the nested structure to search through all competition names
    for region, region_data in competitions_data.items():
        if isinstance(region_data, dict):
            for sub_region, sub_region_data in region_data.items():
                if isinstance(sub_region_data, dict):
                    for key, names in sub_region_data.items():
                        if isinstance(names, list) and competition_name in names:
                            return key
                elif isinstance(sub_region_data, list) and competition_name in sub_region_data:
                    return sub_region
        elif isinstance(region_data, list) and competition_name in region_data:
            return region
    
    # If not found, return the original name
    return competition_name

def clean_division_type(division_type):
    """
    Check if the division type contains 'OPEN' but not 'NATURAL OPEN'.
    Returns True if it's a valid OPEN competition, False otherwise.
    """
    if not division_type:
        return False
    
    # Convert to string and uppercase for comparison
    division_type_str = str(division_type).upper()
    
    # Check if it contains 'OPEN' but not 'NATURAL OPEN'
    if 'OPEN' in division_type_str and 'NATURAL OPEN' not in division_type_str:
        return True
    
    return False

def merge_competitions(competitions_list):
    """
    Merge competitions with the same key and location into single rows.
    When dates differ, use earliest start date and latest end date.
    """
    merged = {}
    
    for comp in competitions_list:
        # Create a unique key based on competition_key and location
        # For location matching, if one has empty city and other has city, treat as same
        location_city = comp['location_city'] if comp['location_city'] else ''
        location_state = comp['location_state'] if comp['location_state'] else ''
        location_country = comp['location_country'] if comp['location_country'] else ''
        
        merge_key = (
            comp['competition_key'],
            location_country,  # Use country as primary location identifier
            comp['division_level'],
            comp['division_type']
        )
        
        if merge_key in merged:
            # Merge with existing competition
            existing = merged[merge_key]
            
            # Combine names with comma
            if comp['name'] not in existing['name']:
                existing['name'] += f", {comp['name']}"
            
            # Combine divisions with comma
            if comp['division'] not in existing['division']:
                existing['division'] += f", {comp['division']}"
            
            # Use the earliest start date and latest end date
            if comp['start_date'] < existing['start_date']:
                existing['start_date'] = comp['start_date']
            if comp['end_date'] > existing['end_date']:
                existing['end_date'] = comp['end_date']
            
            # Use the first non-empty URL if available
            if not existing['url'] and comp['url']:
                existing['url'] = comp['url']
            
            # Use the first non-empty city if available
            if not existing['location_city'] and comp['location_city']:
                existing['location_city'] = comp['location_city']
            
            # Use the first non-empty state if available
            if not existing['location_state'] and comp['location_state']:
                existing['location_state'] = comp['location_state']
                
        else:
            # Add new competition
            merged[merge_key] = comp.copy()
    
    return list(merged.values())

def process_schedule_2025():
    """
    Process the all_competitions.csv file and create a cleaned schedule2025.csv file.
    """
    # Load the competitions.json file
    competitions_file = 'keys/competitions.json'
    with open(competitions_file, 'r', encoding='utf-8') as f:
        competitions_data = json.load(f)
    
    # Input and output file paths
    input_file = 'data/schedule_2025/all_competitions.csv'
    output_file = 'data/clean/schedule2025.csv'
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Process the CSV file
    cleaned_competitions = []
    
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Check if competition level is Pro
            if row['Competition Level'] != 'IFBB Pro':
                continue
            
            # Check if division type contains OPEN but not NATURAL OPEN
            if not clean_division_type(row['Division Type']):
                continue
            
            # Skip Portugal Natural Pro competition
            if 'Portugal Natural Pro' in row['Competition Name']:
                continue
            
            # Get start and end dates
            start_date = row['Start Date']
            end_date = row['End Date']
            
            # If no end date, set it equal to start date
            if not end_date or end_date.strip() == '':
                end_date = start_date
            
            # Find the competition key
            competition_key = find_competition_key(row['Competition Name'], competitions_data)
            
            # Create cleaned row
            cleaned_row = {
                'start_date': start_date,
                'end_date': end_date,
                'year': '2025',
                'competition_key': competition_key,
                'name': row['Competition Name'],
                'division': row['Division'],
                'division_type': row['Division Type'],
                'division_level': row['Competition Level'],
                'location_city': row['Location City'],
                'location_state': get_full_state_name(row['Location State']),
                'location_country': row['Location Country'],
                'promoter_name': row['Promoter Name'],
                'promoter_email': row['Promoter Email'],
                'promoter_website': row['Promoter Website'],
                'url': row['Competition URL']
            }
            
            cleaned_competitions.append(cleaned_row)
    
    # Merge competitions with the same key, date, and location
    merged_competitions = merge_competitions(cleaned_competitions)
    
    # Sort by start date
    merged_competitions.sort(key=lambda x: x['start_date'])
    
    # Write to output file
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'start_date', 'end_date', 'year', 'competition_key', 'name', 'division', 
            'division_type', 'division_level', 'location_city', 
            'location_state', 'location_country', 'promoter_name',
            'promoter_email', 'promoter_website', 'url'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in merged_competitions:
            writer.writerow(row)
    
    print(f"Processed {len(cleaned_competitions)} original competitions")
    print(f"Merged into {len(merged_competitions)} unique competitions")
    print(f"Output saved to: {output_file}")
    
    # Print some statistics
    print(f"\nStatistics:")
    print(f"Original competitions: {len(cleaned_competitions)}")
    print(f"Merged competitions: {len(merged_competitions)}")
    print(f"Reduction: {len(cleaned_competitions) - len(merged_competitions)} rows merged")
    
    # Count competitions by country
    country_counts = {}
    for comp in merged_competitions:
        country = comp['location_country']
        country_counts[country] = country_counts.get(country, 0) + 1
    
    print(f"\nCompetitions by country:")
    for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {country}: {count}")

if __name__ == "__main__":
    process_schedule_2025()
