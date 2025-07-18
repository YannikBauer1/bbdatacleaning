import pandas as pd
import os
import json
from difflib import SequenceMatcher
from collections import defaultdict
import sys
import tty
import termios  # For Unix-like systems
from datetime import datetime

def load_existing_divisions():
    """
    Load existing division names from division_names.json file.
    
    Returns:
        set: A set of all division names that are already in the file
    """
    existing_divisions_path = "keys/division_names.json"
    
    if not os.path.exists(existing_divisions_path):
        print(f"Warning: {existing_divisions_path} not found. Will treat all divisions as new.")
        return set()
    
    try:
        with open(existing_divisions_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        # Extract all division names from all arrays
        existing_divisions = set()
        for division_array in existing_data.values():
            existing_divisions.update(division_array)
        
        return existing_divisions
        
    except Exception as e:
        print(f"Error reading existing divisions file: {e}")
        return set()

def get_unique_divisions():
    """
    Read the all_clean.csv file and return all unique division names.
    
    Returns:
        list: A list of unique division names sorted alphabetically
    """
    # Path to the CSV file - adjust based on current working directory
    csv_path = "data/all/all_clean.csv"
    
    # Check if file exists
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at: {csv_path}")
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Get unique values from the Division column
        unique_divisions = df['Division'].unique()
        
        # Remove any NaN values and sort alphabetically
        unique_divisions = sorted([div for div in unique_divisions if pd.notna(div)])
        
        return unique_divisions
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def get_new_divisions():
    """
    Get divisions that are not already in the division_names.json file.
    
    Returns:
        list: A list of new division names sorted alphabetically
    """
    all_divisions = get_unique_divisions()
    existing_divisions = load_existing_divisions()
    
    # Find divisions that are not in the existing set
    new_divisions = [div for div in all_divisions if div not in existing_divisions]
    
    return sorted(new_divisions)

def find_empty_divisions():
    """
    Find all rows where the division column is empty or contains only whitespace.
    """
    csv_path = "data/all/all_clean.csv"
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found at: {csv_path}")
        return
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Search for rows with empty or whitespace-only division
        empty_divisions = df[df['Division'].str.strip().eq('') | df['Division'].isna()]
        
        if empty_divisions.empty:
            print("No rows found with empty division column.")
            return
        
        print(f"Found {len(empty_divisions)} rows with empty division column:")
        print("=" * 80)
        
        # Display all rows
        for idx, row in empty_divisions.iterrows():
            print(f"Row {idx + 1}:")
            for column in df.columns:
                value = row[column]
                if pd.notna(value):  # Only print non-null values
                    print(f"  {column}: {value}")
            print("-" * 40)
        
        # Also show a summary table
        print("\nSummary table of rows with empty divisions:")
        print(empty_divisions[['Division', 'Competition', 'Year']].to_string(index=False))
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")

def find_olympia_divisions():
    """
    Find all rows that have "olympia" in the division column and display their information.
    """
    csv_path = "data/all/all_clean.csv"
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found at: {csv_path}")
        return
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Search for rows with "olympia" in the Division column (case insensitive)
        olympia_rows = df[df['Division'].str.contains('olympia', case=False, na=False)]
        
        if olympia_rows.empty:
            print("No rows found with 'olympia' in the Division column.")
            return
        
        print(f"Found {len(olympia_rows)} rows with 'olympia' in the Division column:")
        print("=" * 80)
        
        # Display unique division names first
        unique_olympia_divisions = olympia_rows['Division'].unique()
        print(f"Unique Division names containing 'olympia': {list(unique_olympia_divisions)}")
        print("-" * 80)
        
        # Display all rows
        for idx, row in olympia_rows.iterrows():
            print(f"Row {idx + 1}:")
            for column in df.columns:
                value = row[column]
                if pd.notna(value):  # Only print non-null values
                    print(f"  {column}: {value}")
            print("-" * 40)
        
        # Also show a summary table
        print("\nSummary table of Olympia divisions:")
        print(olympia_rows[['Division', 'Competition', 'Year']].to_string(index=False))
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")

def find_round_2_3_entries():
    """
    Find all rows that have entries in Round 2 or Round 3 columns.
    """
    csv_path = "data/all/all_clean.csv"
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found at: {csv_path}")
        return
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Search for rows with non-empty values in Round 2 or Round 3
        round_2_3_rows = df[
            (df['Round 2'].notna() & (df['Round 2'].astype(str).str.strip() != '')) |
            (df['Round 3'].notna() & (df['Round 3'].astype(str).str.strip() != ''))
        ]
        
        if round_2_3_rows.empty:
            print("No rows found with entries in Round 2 or Round 3.")
            return
        
        print(f"Found {len(round_2_3_rows)} rows with entries in Round 2 or Round 3:")
        print("=" * 80)
        
        # Display unique competitions and divisions first
        unique_competitions = round_2_3_rows['Competition'].unique()
        unique_divisions = round_2_3_rows['Division'].unique()
        
        print(f"Unique Competitions: {list(unique_competitions)}")
        print(f"Unique Divisions: {list(unique_divisions)}")
        print("-" * 80)
        
        # Display all rows
        for idx, row in round_2_3_rows.iterrows():
            print(f"Row {idx + 1}:")
            for column in df.columns:
                value = row[column]
                if pd.notna(value) and str(value).strip() != '':  # Only print non-null, non-empty values
                    print(f"  {column}: {value}")
            print("-" * 40)
        
        # Also show a summary table
        print("\nSummary table of Round 2/3 entries:")
        summary_columns = ['Competition', 'Division', 'Competitor Name', 'Round 2', 'Round 3', 'Year']
        print(round_2_3_rows[summary_columns].to_string(index=False))
        
        # Show statistics
        print(f"\nStatistics:")
        print(f"  Rows with Round 2 entries: {len(round_2_3_rows[round_2_3_rows['Round 2'].notna() & (round_2_3_rows['Round 2'].astype(str).str.strip() != '')])}")
        print(f"  Rows with Round 3 entries: {len(round_2_3_rows[round_2_3_rows['Round 3'].notna() & (round_2_3_rows['Round 3'].astype(str).str.strip() != '')])}")
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")

def create_divisions_json():
    """
    Create a JSON file with only new divisions that are not already in division_names.json.
    
    Returns:
        str: Path to the created JSON file
    """
    new_divisions = get_new_divisions()
    
    if not new_divisions:
        print("No new divisions found. All divisions are already in division_names.json")
        return None
    
    # Create dictionary where each new division is a key with an array containing the division name
    divisions_dict = {division: [division] for division in new_divisions}
    
    # Define output file path
    output_path = "all/divisions.json"
    
    try:
        # Write to JSON file with nice formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(divisions_dict, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully created JSON file: {output_path}")
        print(f"Contains {len(divisions_dict)} new divisions")
        return output_path
        
    except Exception as e:
        print(f"Error writing JSON file: {e}")
        return None

def print_new_divisions():
    """
    Print only new division names that are not already in division_names.json.
    """
    new_divisions = get_new_divisions()
    
    if new_divisions:
        print(f"Found {len(new_divisions)} new divisions not in division_names.json:")
        print("-" * 50)
        for i, division in enumerate(new_divisions, 1):
            print(f"{i:3d}. {division}")
    else:
        print("No new divisions found. All divisions are already in division_names.json")

def get_unique_locations_countries():
    """
    Extract unique location data from the CSV file by parsing Location and Competitor location columns
    to extract city, state, country combinations.
    
    Creates a JSON where keys are unique city-state-country combinations extracted from
    Location/Competitor location data, and values are arrays of the original Location/Country column values
    that map to those extracted city-state-country combinations.
    
    Returns:
        str: Path to the created JSON file, or None if error
    """
    csv_path = "data/all/all_clean.csv"
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found at: {csv_path}")
        return None
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path, low_memory=False)
        
        # Dictionary to store the mapping: extracted city-state-country -> [original Location/Country values]
        location_mapping = {}
        
        # Process each row to extract location information
        for _, row in df.iterrows():
            # Process Location columns (competition location)
            location_city = ""
            location_state = ""
            location_country = ""
            
            if 'Location City' in df.columns and pd.notna(row['Location City']):
                location_city = str(row['Location City']).strip()
            
            if 'Location State' in df.columns and pd.notna(row['Location State']):
                location_state = str(row['Location State']).strip()
            
            if 'Location Country' in df.columns and pd.notna(row['Location Country']):
                location_country = str(row['Location Country']).strip()
            
            # Create location key for competition location
            loc_parts = []
            if location_city:
                loc_parts.append(location_city)
            if location_state:
                loc_parts.append(location_state)
            if location_country:
                loc_parts.append(location_country)
            
            location_key = ", ".join(loc_parts) if loc_parts else None
            
            if location_key:
                # Initialize the key if it doesn't exist
                if location_key not in location_mapping:
                    location_mapping[location_key] = []
                
                # Add the original Location column value if it exists and is not already there
                if 'Location' in df.columns and pd.notna(row['Location']):
                    original_location = str(row['Location']).strip()
                    if original_location and original_location not in location_mapping[location_key]:
                        location_mapping[location_key].append(original_location)
            
            # Process Competitor location columns
            competitor_city = ""
            competitor_state = ""
            competitor_country = ""
            
            if 'Competitor City' in df.columns and pd.notna(row['Competitor City']):
                competitor_city = str(row['Competitor City']).strip()
            
            if 'Competitor State' in df.columns and pd.notna(row['Competitor State']):
                competitor_state = str(row['Competitor State']).strip()
            
            if 'Competitor Country' in df.columns and pd.notna(row['Competitor Country']):
                competitor_country = str(row['Competitor Country']).strip()
            
            # Create location key for competitor location
            comp_parts = []
            if competitor_city:
                comp_parts.append(competitor_city)
            if competitor_state:
                comp_parts.append(competitor_state)
            if competitor_country:
                comp_parts.append(competitor_country)
            
            competitor_key = ", ".join(comp_parts) if comp_parts else None
            
            if competitor_key:
                # Initialize the key if it doesn't exist
                if competitor_key not in location_mapping:
                    location_mapping[competitor_key] = []
                
                # Add the original Country column value if it exists and is not already there
                if 'Country' in df.columns and pd.notna(row['Country']):
                    original_country = str(row['Country']).strip()
                    if original_country and original_country not in location_mapping[competitor_key]:
                        location_mapping[competitor_key].append(original_country)
        
        # Sort the arrays for each key
        for key in location_mapping:
            location_mapping[key].sort()
        
        # Sort the dictionary by keys
        sorted_location_mapping = dict(sorted(location_mapping.items()))
        
        # Define output file path
        output_path = "all/locations_countries.json"
        
        # Write to JSON file with nice formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sorted_location_mapping, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully created JSON file: {output_path}")
        print(f"Contains {len(sorted_location_mapping)} unique extracted city-state-country combinations")
        
        # Calculate total original combinations
        total_combinations = sum(len(combinations) for combinations in sorted_location_mapping.values())
        print(f"Total original Location/Country values: {total_combinations}")
        
        # Show some statistics
        if sorted_location_mapping:
            # Find the key with most combinations
            max_key = max(sorted_location_mapping.items(), key=lambda x: len(x[1]))
            min_key = min(sorted_location_mapping.items(), key=lambda x: len(x[1]))
            
            print(f"\nExtracted city-state-country with most original combinations: {max_key[0]}")
            print(f"  Number of original combinations: {len(max_key[1])}")
            print(f"  Original combinations: {max_key[1][:3]}{'...' if len(max_key[1]) > 3 else ''}")
            
            print(f"\nExtracted city-state-country with least original combinations: {min_key[0]}")
            print(f"  Number of original combinations: {len(min_key[1])}")
            print(f"  Original combinations: {min_key[1]}")
            
            # Show first few entries as examples
            print(f"\nFirst few entries:")
            for i, (key, combinations) in enumerate(list(sorted_location_mapping.items())[:3]):
                print(f"{i+1}. {key}: {combinations}")
        
        return output_path
        
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_unique_competitor_names_detailed():
    """
    Extract unique competitor names from the CSV file, count their occurrences,
    and include additional information: first/last year, unique divisions, and unique locations.
    
    Returns:
        str: Path to the created JSON file, or None if error
    """
    csv_path = "data/all/all_clean.csv"
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found at: {csv_path}")
        return None
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path, low_memory=False)
        
        # Check if 'Competitor Name' column exists
        if 'Competitor Name' not in df.columns:
            print("Error: 'Competitor Name' column not found in CSV file")
            return None
        
        # Get competitor names (non-null, non-empty)
        competitor_names = df['Competitor Name'].dropna()
        competitor_names = competitor_names[competitor_names.astype(str).str.strip() != '']
        
        # Create a dictionary to store detailed information for each competitor
        competitor_details = {}
        
        # Group by competitor name to get detailed information
        for competitor_name in competitor_names.unique():
            # Get all rows for this competitor
            competitor_rows = df[df['Competitor Name'] == competitor_name]
            
            # Get years from Start Date column (non-null)
            years = []
            if 'Start Date' in df.columns:
                start_dates = competitor_rows['Start Date'].dropna()
                for date_str in start_dates:
                    try:
                        # Try to extract year from date string
                        if pd.notna(date_str) and str(date_str).strip() != '':
                            # Handle different date formats
                            date_str = str(date_str).strip()
                            if '/' in date_str:
                                # Format like MM/DD/YYYY or YYYY/MM/DD
                                parts = date_str.split('/')
                                if len(parts) == 3:
                                    # Try to identify which part is the year
                                    for part in parts:
                                        if len(part) == 4 and part.isdigit():
                                            years.append(int(part))
                                            break
                            elif '-' in date_str:
                                # Format like YYYY-MM-DD
                                parts = date_str.split('-')
                                if len(parts) >= 1 and parts[0].isdigit() and len(parts[0]) == 4:
                                    years.append(int(parts[0]))
                    except:
                        continue
            
            first_year = min(years) if years else None
            last_year = max(years) if years else None
            
            # Get unique divisions (non-null, non-empty)
            divisions = competitor_rows['Division'].dropna()
            divisions = divisions[divisions.astype(str).str.strip() != '']
            unique_divisions = sorted(list(divisions.unique()))
            
            # Get unique location combinations
            location_combinations = set()
            
            # Check which location columns exist
            location_columns = []
            if 'Competitor City' in df.columns:
                location_columns.append('Competitor City')
            if 'Competitor State' in df.columns:
                location_columns.append('Competitor State')
            if 'Competitor Country' in df.columns:
                location_columns.append('Competitor Country')
            
            # Create location combinations
            for _, row in competitor_rows.iterrows():
                location_parts = []
                for col in location_columns:
                    value = row[col]
                    if pd.notna(value) and str(value).strip() != '':
                        location_parts.append(str(value).strip())
                
                if location_parts:  # Only add if we have at least one location part
                    location_combinations.add(', '.join(location_parts))
            
            # Sort location combinations
            unique_locations = sorted(list(location_combinations))
            
            # Store all information
            competitor_details[competitor_name] = {
                'appearances': len(competitor_rows),
                'first_year': first_year,
                'last_year': last_year,
                'unique_divisions': unique_divisions,
                'unique_locations': unique_locations
            }
        
        # Sort alphabetically by competitor name
        sorted_competitors = dict(sorted(competitor_details.items()))
        
        # Define output file path
        output_path = "all/competitor_names_detailed.json"
        
        # Write to JSON file with nice formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sorted_competitors, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully created JSON file: {output_path}")
        print(f"Contains {len(sorted_competitors)} unique competitor names")
        print(f"Total competitor entries: {sum(comp['appearances'] for comp in sorted_competitors.values())}")
        
        # Show some statistics and examples
        if sorted_competitors:
            # Find competitor with most appearances
            max_competitor = max(sorted_competitors.items(), key=lambda x: x[1]['appearances'])
            min_competitor = min(sorted_competitors.items(), key=lambda x: x[1]['appearances'])
            
            print(f"\nMost frequent competitor: {max_competitor[0]}")
            print(f"  Appearances: {max_competitor[1]['appearances']}")
            print(f"  Years: {max_competitor[1]['first_year']} - {max_competitor[1]['last_year']}")
            print(f"  Divisions: {max_competitor[1]['unique_divisions']}")
            print(f"  Locations: {max_competitor[1]['unique_locations'][:3]}{'...' if len(max_competitor[1]['unique_locations']) > 3 else ''}")
            
            print(f"\nLeast frequent competitor: {min_competitor[0]}")
            print(f"  Appearances: {min_competitor[1]['appearances']}")
            print(f"  Years: {min_competitor[1]['first_year']} - {min_competitor[1]['last_year']}")
            print(f"  Divisions: {min_competitor[1]['unique_divisions']}")
            print(f"  Locations: {min_competitor[1]['unique_locations']}")
            
            # Show first few entries as examples
            print(f"\nFirst few entries:")
            for i, (name, details) in enumerate(list(sorted_competitors.items())[:3]):
                print(f"{i+1}. {name}")
                print(f"   Appearances: {details['appearances']}")
                print(f"   Years: {details['first_year']} - {details['last_year']}")
                print(f"   Divisions: {details['unique_divisions']}")
                print(f"   Locations: {details['unique_locations'][:2]}{'...' if len(details['unique_locations']) > 2 else ''}")
        
        return output_path
        
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return None

def get_unique_competitor_names():
    """
    Extract unique competitor names from the CSV file and create a simple JSON
    where each competitor name is a key with an array containing the name.
    
    Returns:
        str: Path to the created JSON file, or None if error
    """
    csv_path = "data/all/all_clean.csv"
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found at: {csv_path}")
        return None
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path, low_memory=False)
        
        # Check if 'Competitor Name' column exists
        if 'Competitor Name' not in df.columns:
            print("Error: 'Competitor Name' column not found in CSV file")
            return None
        
        # Get unique competitor names (non-null, non-empty)
        competitor_names = df['Competitor Name'].dropna()
        competitor_names = competitor_names[competitor_names.astype(str).str.strip() != '']
        unique_competitors = sorted(competitor_names.unique())
        
        # Create dictionary where each competitor name is a key with an array containing the name
        competitors_dict = {name: [name] for name in unique_competitors}
        
        # Define output file path
        output_path = "all/competitor_names.json"
        
        # Write to JSON file with nice formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(competitors_dict, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully created JSON file: {output_path}")
        print(f"Contains {len(competitors_dict)} unique competitor names")
        
        # Show first few entries as examples
        print(f"\nFirst few entries:")
        for i, (name, name_array) in enumerate(list(competitors_dict.items())[:5]):
            print(f"{i+1}. {name}: {name_array}")
        
        return output_path
        
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return None

def analyze_and_merge_competitor_names():
    """
    Analyze competitor names across different sources, find similar names that are likely the same person,
    and update the competitor_names.json file to group them together.
    
    This version groups names based on similar competitors who achieved the same place 
    in different sources for the same competition.
    """
    csv_path = "data/all/all_clean.csv"
    competitor_names_path = "all/competitor_names.json"
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found at: {csv_path}")
        return None
    
    if not os.path.exists(competitor_names_path):
        print(f"Competitor names file not found at: {competitor_names_path}")
        return None
    
    try:
        # Read the CSV file
        print("Reading CSV file...")
        df = pd.read_csv(csv_path, low_memory=False)
        
        # Read existing competitor names
        print("Reading existing competitor names...")
        with open(competitor_names_path, 'r', encoding='utf-8') as f:
            competitor_names = json.load(f)
        
        # Get unique competitor names from CSV
        unique_names = df['Competitor Name'].dropna().unique()
        unique_names = [name.strip() for name in unique_names if name.strip()]
        
        print(f"Found {len(unique_names)} unique competitor names in CSV")
        print(f"Found {len(competitor_names)} entries in competitor_names.json")
        
        # Function to calculate similarity between two names
        def name_similarity(name1, name2):
            """Calculate similarity between two names, handling common variations."""
            # Normalize names for comparison
            def normalize_name(name):
                # Remove extra spaces, convert to lowercase
                return ' '.join(name.lower().split())
            
            norm1 = normalize_name(name1)
            norm2 = normalize_name(name2)
            
            # If exactly the same after normalization, return 1.0
            if norm1 == norm2:
                return 1.0
            
            # Check if one is a subset of the other (missing middle name, etc.)
            words1 = set(norm1.split())
            words2 = set(norm2.split())
            
            # If one name is completely contained in the other
            if words1.issubset(words2) or words2.issubset(words1):
                return 0.9
            
            # Calculate sequence similarity
            similarity = SequenceMatcher(None, norm1, norm2).ratio()
            
            # Boost similarity for names that share common words
            common_words = words1.intersection(words2)
            if common_words:
                # If they share at least 2 words, boost similarity
                if len(common_words) >= 2:
                    similarity += 0.2
                elif len(common_words) >= 1:
                    similarity += 0.1
            
            return min(similarity, 1.0)
        
        # Group by competition, division, year, and place to find similar names
        print("Analyzing competitions by place and source...")
        
        # Create a mapping of competition-place combinations
        competition_place_groups = defaultdict(list)
        
        for _, row in df.iterrows():
            if (pd.notna(row['Competitor Name']) and row['Competitor Name'].strip() and
                pd.notna(row['Competition']) and row['Competition'].strip() and
                pd.notna(row['Place']) and str(row['Place']).strip() and
                pd.notna(row['Division']) and row['Division'].strip()):
                
                # Create a key for the competition-place combination
                competition = row['Competition'].strip()
                place = str(row['Place']).strip()
                division = row['Division'].strip()
                year = None
                
                # Try to extract year from Start Date
                if pd.notna(row['Start Date']) and str(row['Start Date']).strip():
                    try:
                        date_str = str(row['Start Date']).strip()
                        if '/' in date_str:
                            parts = date_str.split('/')
                            if len(parts) == 3:
                                for part in parts:
                                    if len(part) == 4 and part.isdigit():
                                        year = part
                                        break
                        elif '-' in date_str:
                            parts = date_str.split('-')
                            if len(parts) >= 1 and parts[0].isdigit() and len(parts[0]) == 4:
                                year = parts[0]
                    except:
                        pass
                
                # Create a unique key for this competition-place combination
                if year:
                    key = f"{competition}_{year}_{division}_{place}"
                else:
                    key = f"{competition}_{division}_{place}"
                
                competitor_name = row['Competitor Name'].strip()
                source = row.get('Source', 'Unknown')
                
                competition_place_groups[key].append({
                    'name': competitor_name,
                    'source': source,
                    'competition': competition,
                    'division': division,
                    'place': place,
                    'year': year
                })
        
        print(f"Found {len(competition_place_groups)} competition-place combinations")
        
        # Find groups where the same place has different names from different sources
        similar_name_groups = []
        
        for key, entries in competition_place_groups.items():
            if len(entries) > 1:
                # Check if there are different names for the same place
                unique_names_in_group = set(entry['name'] for entry in entries)
                unique_sources = set(entry['source'] for entry in entries)
                
                # Only consider if we have different names from different sources
                if len(unique_names_in_group) > 1 and len(unique_sources) > 1:
                    # Find similar names within this group
                    names_in_group = list(unique_names_in_group)
                    
                    for i, name1 in enumerate(names_in_group):
                        for j, name2 in enumerate(names_in_group[i+1:], i+1):
                            similarity = name_similarity(name1, name2)
                            
                            # If names are similar enough, group them
                            if similarity >= 0.7:  # Adjust threshold as needed
                                # Check if these names are already in a group
                                found_group = None
                                for group in similar_name_groups:
                                    if name1 in group or name2 in group:
                                        found_group = group
                                        break
                                
                                if found_group:
                                    # Add names to existing group
                                    if name1 not in found_group:
                                        found_group.append(name1)
                                    if name2 not in found_group:
                                        found_group.append(name2)
                                else:
                                    # Create new group
                                    similar_name_groups.append([name1, name2])
        
        print(f"Found {len(similar_name_groups)} groups of similar names based on competition-place matching")
        
        # Merge overlapping groups
        print("Merging overlapping groups...")
        merged_groups = []
        processed_names = set()
        
        for group in similar_name_groups:
            # Check if any name in this group is already processed
            if any(name in processed_names for name in group):
                # Find all groups that contain any of these names
                related_groups = [group]
                for existing_group in merged_groups:
                    if any(name in existing_group for name in group):
                        related_groups.append(existing_group)
                
                # Merge all related groups
                merged_group = list(set([name for g in related_groups for name in g]))
                
                # Remove old groups and add merged group
                merged_groups = [g for g in merged_groups if not any(name in g for name in merged_group)]
                merged_groups.append(merged_group)
                
                # Mark all names as processed
                processed_names.update(merged_group)
            else:
                # This is a new group
                merged_groups.append(group)
                processed_names.update(group)
        
        print(f"After merging: {len(merged_groups)} groups")
        
        # Show some examples
        print("\nExample groups of similar names based on competition-place matching:")
        for i, group in enumerate(merged_groups[:10]):
            print(f"{i+1}. {group}")
        
        # Update competitor_names.json
        print("\nUpdating competitor_names.json...")
        
        # Create new competitor names dictionary
        updated_competitor_names = {}
        
        # Add all names that are not in similar groups
        for name in unique_names:
            if not any(name in group for group in merged_groups):
                updated_competitor_names[name] = [name]
        
        # Add grouped names
        for group in merged_groups:
            # Use the longest name as the primary name
            primary_name = max(group, key=len)
            updated_competitor_names[primary_name] = sorted(group)
        
        # Sort alphabetically
        updated_competitor_names = dict(sorted(updated_competitor_names.items()))
        
        # Write updated file
        with open(competitor_names_path, 'w', encoding='utf-8') as f:
            json.dump(updated_competitor_names, f, indent=2, ensure_ascii=False)
        
        print(f"Updated competitor_names.json")
        print(f"Original entries: {len(competitor_names)}")
        print(f"Updated entries: {len(updated_competitor_names)}")
        print(f"Reduced by: {len(competitor_names) - len(updated_competitor_names)} entries")
        
        # Show some statistics
        total_names = sum(len(names) for names in updated_competitor_names.values())
        print(f"Total unique names: {total_names}")
        
        # Show groups with most variations
        print("\nGroups with most name variations:")
        sorted_groups = sorted(updated_competitor_names.items(), key=lambda x: len(x[1]), reverse=True)
        for i, (primary, variations) in enumerate(sorted_groups[:5]):
            if len(variations) > 1:
                print(f"{i+1}. {primary}: {variations}")
        
        # Show some examples of competition-place matches that led to groupings
        print("\nExample competition-place matches that led to groupings:")
        example_count = 0
        for key, entries in competition_place_groups.items():
            if example_count >= 5:
                break
            unique_names_in_group = set(entry['name'] for entry in entries)
            unique_sources = set(entry['source'] for entry in entries)
            
            if len(unique_names_in_group) > 1 and len(unique_sources) > 1:
                print(f"Competition: {entries[0]['competition']}")
                print(f"Division: {entries[0]['division']}")
                print(f"Place: {entries[0]['place']}")
                print(f"Names: {list(unique_names_in_group)}")
                print(f"Sources: {list(unique_sources)}")
                print("-" * 40)
                example_count += 1
        
        return competitor_names_path
        
    except Exception as e:
        print(f"Error processing competitor names: {e}")
        import traceback
        traceback.print_exc()
        return None

def find_similar_names_to_file():
    """
    Find similar competitor names and write them to a file for later processing.
    This is much faster than the interactive approach.
    """
    competitor_names_path = "keys/competitor_names.json"
    csv_path = "data/all/all_clean.csv"
    output_path = "all/similar_names_to_merge.json"
    
    if not os.path.exists(competitor_names_path):
        print(f"Competitor names file not found at: {competitor_names_path}")
        return
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found at: {csv_path}")
        return
    
    try:
        # Load competitor names
        print("Loading competitor names...")
        with open(competitor_names_path, 'r', encoding='utf-8') as f:
            competitor_names = json.load(f)
        
        # Load CSV data
        print("Loading CSV data...")
        df = pd.read_csv(csv_path, low_memory=False)
        
        print(f"Loaded {len(competitor_names)} competitor entries")
        print(f"Loaded {len(df)} CSV rows")
        
        # Pre-compute all competitor info (MUCH FASTER)
        print("Pre-computing competitor information...")
        all_competitor_info = {}
        
        for competitor_name in competitor_names.keys():
            all_competitor_info[competitor_name] = get_competitor_info(df, competitor_name)
        
        print("Finished pre-computing competitor info")
        
        # Get all unique competitor names
        all_names = list(competitor_names.keys())
        
        # Initialize or load existing similar groups
        similar_groups = []
        if os.path.exists(output_path):
            print(f"Loading existing similar groups from {output_path}...")
            with open(output_path, 'r', encoding='utf-8') as f:
                similar_groups = json.load(f)
            print(f"Loaded {len(similar_groups)} existing groups")
        
        # Keep track of processed names to avoid re-checking
        processed_names = set()
        for group in similar_groups:
            processed_names.update(group['names'])
        
        # Keep track of displayed similarities to avoid showing duplicates
        displayed_similarities = set()
        
        print(f"Already processed {len(processed_names)} names in existing groups")
        
        # Find similar name groups
        print("Finding similar names...")
        total_found = len(similar_groups)
        new_groups_found = 0
        
        for i, name1 in enumerate(all_names):
            if i % 100 == 0:  # Progress indicator (more frequent now)
                print(f"Processing name {i+1}/{len(all_names)}")
                
                # Write current results to file every 100 names (append new groups)
                if new_groups_found > 0:
                    print(f"Writing {len(similar_groups)} total groups to file (including {new_groups_found} new ones)...")
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(similar_groups, f, indent=2, ensure_ascii=False)
                    print(f"✅ Saved {len(similar_groups)} groups to {output_path}")
            
            # Find all names similar to name1 (including subnames)
            similar_to_name1 = [name1]
            
            for j, name2 in enumerate(all_names[i+1:], i+1):
                # Check similarity between key names
                key_similarity = calculate_name_similarity(name1, name2, all_competitor_info.get(name1), all_competitor_info.get(name2))
                
                # Check similarity between subnames
                subname_similarities = []
                for subname1 in competitor_names[name1]:
                    for subname2 in competitor_names[name2]:
                        if subname1 != subname2:  # Don't compare same name
                            subname_sim = calculate_name_similarity(subname1, subname2, all_competitor_info.get(name1), all_competitor_info.get(name2))
                            subname_similarities.append(subname_sim)
                
                # Get the highest similarity (either key similarity or best subname similarity)
                max_similarity = max([key_similarity] + subname_similarities) if subname_similarities else key_similarity
                
                # Only consider pairs with high similarity
                if max_similarity >= 0.7:
                    similar_to_name1.append(name2)
                    
                    # Create a unique key for this similarity pair
                    similarity_key = tuple(sorted([name1, name2]))
                    
                    # Only show if this similarity hasn't been displayed yet
                    if similarity_key not in displayed_similarities:
                        displayed_similarities.add(similarity_key)
                        
                        # Show enhanced similarity details if available
                        info1 = all_competitor_info.get(name1)
                        info2 = all_competitor_info.get(name2)
                        
                        # Find which names were most similar
                        if subname_similarities and max(subname_similarities) > key_similarity:
                            # Find the subnames that had the highest similarity
                            max_subname_sim = max(subname_similarities)
                            similar_subnames = []
                            for subname1 in competitor_names[name1]:
                                for subname2 in competitor_names[name2]:
                                    if subname1 != subname2:
                                        subname_sim = calculate_name_similarity(subname1, subname2, info1, info2)
                                        if subname_sim == max_subname_sim:
                                            similar_subnames.append((subname1, subname2, subname_sim))
                            
                            print(f"Found similar via subnames: {name1} <-> {name2} (similarity: {max_similarity:.2f})")
                            print(f"  Key similarity: {key_similarity:.2f}")
                            print(f"  Best subname match: '{similar_subnames[0][0]}' <-> '{similar_subnames[0][1]}' (similarity: {similar_subnames[0][2]:.2f})")
                            
                            # Show all names from both arrays
                            print(f"  All names in '{name1}': {competitor_names[name1]}")
                            print(f"  All names in '{name2}': {competitor_names[name2]}")
                        else:
                            print(f"Found similar via keys: {name1} <-> {name2} (similarity: {max_similarity:.2f})")
                            print(f"  All names in '{name1}': {competitor_names[name1]}")
                            print(f"  All names in '{name2}': {competitor_names[name2]}")
                        
                        if info1 and info2:
                            years1 = set(info1.get('years', []))
                            years2 = set(info2.get('years', []))
                            divisions1 = set(info1.get('divisions', []))
                            divisions2 = set(info2.get('divisions', []))
                            locations1 = set(info1.get('locations', []))
                            locations2 = set(info2.get('locations', []))
                            
                            # Calculate expanded year ranges with ±2 tolerance
                            expanded_years1 = set()
                            for year in years1:
                                expanded_years1.update(range(year - 2, year + 3))
                            
                            expanded_years2 = set()
                            for year in years2:
                                expanded_years2.update(range(year - 2, year + 3))
                            
                            overlap_years = expanded_years1.intersection(expanded_years2)
                            exact_matches = len(years1.intersection(years2))
                            division_overlap = len(divisions1.intersection(divisions2)) if divisions1 and divisions2 else 0
                            location_overlap = len(locations1.intersection(locations2)) if locations1 and locations2 else 0
                            
                            print(f"  Combined years for '{name1}': {sorted(years1)}")
                            print(f"  Combined years for '{name2}': {sorted(years2)}")
                            print(f"  Combined divisions for '{name1}': {sorted(divisions1)}")
                            print(f"  Combined divisions for '{name2}': {sorted(divisions2)}")
                            print(f"  Combined locations for '{name1}': {sorted(locations1)[:3]}{'...' if len(locations1) > 3 else ''}")
                            print(f"  Combined locations for '{name2}': {sorted(locations2)[:3]}{'...' if len(locations2) > 3 else ''}")
                            
                            if years1 and years2:
                                print(f"  Original years: {sorted(years1)} vs {sorted(years2)}")
                                print(f"  Expanded ranges: {sorted(expanded_years1)[:5]}{'...' if len(expanded_years1) > 5 else ''} vs {sorted(expanded_years2)[:5]}{'...' if len(expanded_years2) > 5 else ''}")
                                print(f"  Year overlap: {len(overlap_years)} years in expanded range")
                                if exact_matches > 0:
                                    print(f"  Exact year matches: {exact_matches} years")
                            if division_overlap > 0:
                                print(f"  Division overlap: {division_overlap} divisions ({sorted(divisions1.intersection(divisions2))})")
                            if location_overlap > 0:
                                print(f"  Location overlap: {location_overlap} locations ({sorted(locations1.intersection(locations2))})")
            
            # If we found similar names, create a group
            if len(similar_to_name1) > 1:
                # Calculate average similarity for the group
                similarities = []
                for name2 in similar_to_name1[1:]:  # Skip the first name (name1)
                    # Check similarity between key names
                    key_sim = calculate_name_similarity(name1, name2, all_competitor_info.get(name1), all_competitor_info.get(name2))
                    
                    # Check similarity between subnames
                    subname_similarities = []
                    for subname1 in competitor_names[name1]:
                        for subname2 in competitor_names[name2]:
                            if subname1 != subname2:  # Don't compare same name
                                subname_sim = calculate_name_similarity(subname1, subname2, all_competitor_info.get(name1), all_competitor_info.get(name2))
                                subname_similarities.append(subname_sim)
                    
                    # Get the highest similarity (either key similarity or best subname similarity)
                    max_sim = max([key_sim] + subname_similarities) if subname_similarities else key_sim
                    similarities.append(max_sim)
                
                avg_similarity = sum(similarities) / len(similarities) if similarities else 0
                
                # Create group info
                group_info = {
                    'names': similar_to_name1,
                    'primary_name': max(similar_to_name1, key=lambda x: all_competitor_info[x]['appearances']),
                    'average_similarity': avg_similarity,
                    'info': {name: all_competitor_info[name] for name in similar_to_name1}
                }
                
                similar_groups.append(group_info)
                total_found += 1
                new_groups_found += 1
                
                print(f"Created new group: {similar_to_name1} (avg similarity: {avg_similarity:.2f})")
        
        # Sort by average similarity (highest first)
        similar_groups.sort(key=lambda x: x['average_similarity'], reverse=True)
        
        print(f"Found {new_groups_found} new similar name groups")
        print(f"Total groups in file: {len(similar_groups)}")
        
        # Write final results to file
        print(f"Writing final results to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(similar_groups, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Completed! Found {new_groups_found} new similar groups")
        print(f"Total groups in file: {len(similar_groups)}")
        print(f"Results saved to: {output_path}")
        
        # Show some examples of new groups
        if new_groups_found > 0:
            print("\nFirst few new groups found:")
            for i, group in enumerate(similar_groups[-new_groups_found:][:5]):
                print(f"{i+1}. {group['names']} (avg similarity: {group['average_similarity']:.2f})")
        
        return output_path
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_key_press():
    """
    Get a single key press from the user.
    Returns 'enter', 'esc', or 'other'.
    """
    try:
        # Try Windows first
        if os.name == 'nt':
            import msvcrt
            key = msvcrt.getch()
            if key == b'\r' or key == b'\n':
                return 'enter'
            elif key == b'\x1b':  # ESC
                return 'esc'
            else:
                return 'other'
        else:
            # Unix-like systems
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                if ch == '\r' or ch == '\n':
                    return 'enter'
                elif ch == '\x1b':  # ESC
                    return 'esc'
                else:
                    return 'other'
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except:
        # Fallback: just read input
        try:
            input_val = input("Press Enter to merge, ESC to skip, or any other key to skip: ")
            if input_val == '':
                return 'enter'
            else:
                return 'other'
        except:
            return 'other'

def normalize_name_for_comparison(name):
    """
    Normalize a name for comparison by removing extra spaces, converting to lowercase,
    and handling common variations.
    """
    if not name:
        return ""
    
    # Convert to lowercase and remove extra spaces
    normalized = ' '.join(name.lower().split())
    
    # Remove common punctuation
    normalized = normalized.replace('.', '').replace(',', '').replace('-', ' ')
    
    # Remove extra spaces again
    normalized = ' '.join(normalized.split())
    
    return normalized

def calculate_name_similarity(name1, name2, info1=None, info2=None):
    """
    Calculate similarity between two names, handling various name variations.
    Now includes division and year overlap for more accurate matching.
    Returns a score between 0 and 1.
    """
    if not name1 or not name2:
        return 0.0
    
    norm1 = normalize_name_for_comparison(name1)
    norm2 = normalize_name_for_comparison(name2)
    
    # If exactly the same after normalization
    if norm1 == norm2:
        return 1.0
    
    # Split into words
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    
    # If one name is completely contained in the other (missing middle name)
    if words1.issubset(words2) or words2.issubset(words1):
        base_similarity = 0.9
    else:
        # Calculate sequence similarity
        sequence_similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Calculate word overlap
        common_words = words1.intersection(words2)
        total_words = words1.union(words2)
        
        if total_words:
            word_overlap = len(common_words) / len(total_words)
        else:
            word_overlap = 0
        
        # Combine scores (give more weight to word overlap for names)
        base_similarity = (sequence_similarity * 0.4) + (word_overlap * 0.6)
        
        # Boost score if they share common words
        if len(common_words) >= 2:
            base_similarity += 0.1
        elif len(common_words) >= 1:
            base_similarity += 0.05
    
    # If we have additional info, enhance the similarity score
    if info1 and info2:
        # Calculate year overlap with ±2 year tolerance
        years1 = set(info1.get('years', []))
        years2 = set(info2.get('years', []))
        
        if years1 and years2:
            # Create expanded year ranges with ±2 year tolerance
            expanded_years1 = set()
            for year in years1:
                expanded_years1.update(range(year - 2, year + 3))
            
            expanded_years2 = set()
            for year in years2:
                expanded_years2.update(range(year - 2, year + 3))
            
            # Calculate overlap between expanded ranges
            overlap_years = expanded_years1.intersection(expanded_years2)
            
            # Calculate overlap ratio based on original year sets
            year_overlap = len(overlap_years) / max(len(expanded_years1), len(expanded_years2), 1)
            
            # Additional bonus for exact year matches
            exact_matches = len(years1.intersection(years2))
            if exact_matches > 0:
                year_overlap += 0.1  # Bonus for exact year matches
        else:
            year_overlap = 0.0
        
        # Calculate division overlap
        divisions1 = set(info1.get('divisions', []))
        divisions2 = set(info2.get('divisions', []))
        
        if divisions1 and divisions2:
            division_overlap = len(divisions1.intersection(divisions2)) / max(len(divisions1), len(divisions2), 1)
        else:
            division_overlap = 0.0
        
        # Enhanced similarity calculation with additional factors
        # Weight: 70% name similarity, 20% year overlap, 10% division overlap
        enhanced_similarity = (base_similarity * 0.7) + (year_overlap * 0.2) + (division_overlap * 0.1)
        
        return min(enhanced_similarity, 1.0)
    
    # If no additional info available, return base similarity
    return min(base_similarity, 1.0)

def get_competitor_info(df, competitor_name):
    """
    Get detailed information about a competitor from the CSV data.
    """
    competitor_rows = df[df['Competitor Name'] == competitor_name]
    
    if competitor_rows.empty:
        return {
            'appearances': 0,
            'years': [],
            'divisions': [],
            'locations': [],
            'competitions': []
        }
    
    # Get years
    years = []
    if 'Start Date' in df.columns:
        for date_str in competitor_rows['Start Date'].dropna():
            try:
                if pd.notna(date_str) and str(date_str).strip():
                    date_str = str(date_str).strip()
                    if '/' in date_str:
                        parts = date_str.split('/')
                        for part in parts:
                            if len(part) == 4 and part.isdigit():
                                years.append(int(part))
                                break
                    elif '-' in date_str:
                        parts = date_str.split('-')
                        if len(parts) >= 1 and parts[0].isdigit() and len(parts[0]) == 4:
                            years.append(int(parts[0]))
            except:
                continue
    
    # Get unique divisions
    divisions = competitor_rows['Division'].dropna().unique()
    divisions = [d.strip() for d in divisions if d.strip()]
    
    # Get unique locations
    locations = set()
    for _, row in competitor_rows.iterrows():
        location_parts = []
        if pd.notna(row.get('Competitor City')) and str(row['Competitor City']).strip():
            location_parts.append(str(row['Competitor City']).strip())
        if pd.notna(row.get('Competitor State')) and str(row['Competitor State']).strip():
            location_parts.append(str(row['Competitor State']).strip())
        if pd.notna(row.get('Competitor Country')) and str(row['Competitor Country']).strip():
            location_parts.append(str(row['Competitor Country']).strip())
        
        if location_parts:
            locations.add(', '.join(location_parts))
    
    # Get unique competitions
    competitions = competitor_rows['Competition'].dropna().unique()
    competitions = [c.strip() for c in competitions if c.strip()]
    
    return {
        'appearances': len(competitor_rows),
        'years': sorted(list(set(years))),
        'divisions': sorted(divisions),
        'locations': sorted(list(locations)),
        'competitions': sorted(competitions)
    }

def merge_from_file():
    """
    Read similar names from file and allow interactive merging.
    """
    similar_names_path = "all/similar_names_to_merge.json"
    competitor_names_path = "keys/competitor_names.json"
    
    if not os.path.exists(similar_names_path):
        print(f"Similar names file not found at: {similar_names_path}")
        print("Run find_similar_names_to_file() first to generate this file.")
        return
    
    if not os.path.exists(competitor_names_path):
        print(f"Competitor names file not found at: {competitor_names_path}")
        return
    
    try:
        # Load similar groups
        print("Loading similar groups from file...")
        with open(similar_names_path, 'r', encoding='utf-8') as f:
            similar_groups = json.load(f)
        
        # Load competitor names
        print("Loading competitor names...")
        with open(competitor_names_path, 'r', encoding='utf-8') as f:
            competitor_names = json.load(f)
        
        print(f"Loaded {len(similar_groups)} similar groups")
        print(f"Loaded {len(competitor_names)} competitor entries")
        
        if not similar_groups:
            print("No similar groups found in file.")
            return
        
        # Filter to only show unreviewed groups
        unreviewed_groups = [group for group in similar_groups if 'reviewed' not in group]
        reviewed_groups = [group for group in similar_groups if 'reviewed' in group]
        
        print(f"Found {len(unreviewed_groups)} unreviewed groups")
        print(f"Found {len(reviewed_groups)} already reviewed groups")
        
        if not unreviewed_groups:
            print("No unreviewed groups found. All groups have been reviewed.")
            return
        
        # Determine how many groups to process (max 50)
        groups_to_process = min(50, len(unreviewed_groups))
        print(f"Will process {groups_to_process} unreviewed groups (max 50 per session)")
        
        # Interactive merging
        print("\nStarting interactive merging process...")
        print("For each group, press:")
        print("  ENTER - to merge the names")
        print("  ESC   - to skip this group (mark as reviewed)")
        print("  Other - to skip this group (mark as reviewed)")
        print("=" * 80)
        
        merged_count = 0
        skipped_count = 0
        
        for group_idx, group in enumerate(unreviewed_groups[:groups_to_process]):
            names = group['names']
            primary_name = group['primary_name']
            avg_similarity = group['average_similarity']
            info_dict = group['info']
            
            print(f"\nGroup {group_idx + 1}/{groups_to_process} (Avg Similarity: {avg_similarity:.2f})")
            print("=" * 60)
            print(f"Names in group: {names}")
            print(f"Primary name (most appearances): {primary_name}")
            
            # Show info for each name in the group
            for i, name in enumerate(names):
                info = info_dict[name]
                print(f"\nName {i+1}: {name}")
                print(f"  Appearances: {info['appearances']}")
                print(f"  Years: {info['years']}")
                print(f"  Divisions: {info['divisions']}")
                print(f"  Locations: {info['locations']}")
                print(f"  Competitions: {info['competitions'][:3]}{'...' if len(info['competitions']) > 3 else ''}")
            
            # Check for overlapping information between all names
            all_years = set()
            all_divisions = set()
            all_locations = set()
            
            for info in info_dict.values():
                all_years.update(info['years'])
                all_divisions.update(info['divisions'])
                all_locations.update(info['locations'])
            
            # Find overlapping years, divisions, locations
            overlapping_years = []
            overlapping_divisions = []
            overlapping_locations = []
            
            for year in all_years:
                if sum(1 for info in info_dict.values() if year in info['years']) > 1:
                    overlapping_years.append(year)
            
            for division in all_divisions:
                if sum(1 for info in info_dict.values() if division in info['divisions']) > 1:
                    overlapping_divisions.append(division)
            
            for location in all_locations:
                if sum(1 for info in info_dict.values() if location in info['locations']) > 1:
                    overlapping_locations.append(location)
            
            if overlapping_years or overlapping_divisions or overlapping_locations:
                print(f"\n⚠️  OVERLAPPING INFO:")
                if overlapping_years:
                    print(f"  Years: {sorted(overlapping_years)}")
                if overlapping_divisions:
                    print(f"  Divisions: {sorted(overlapping_divisions)}")
                if overlapping_locations:
                    print(f"  Locations: {sorted(overlapping_locations)}")
            
            print(f"\nPress ENTER to merge all names into '{primary_name}', ESC to skip, or any other key to skip...")
            
            # Get user input
            key = get_key_press()
            
            if key == 'enter':
                # Merge all names into the primary name
                print("Merging names...")
                
                # Find the actual key that contains the primary_name (if primary_name is only a subname)
                actual_primary_key = None
                for key_name, subnames in competitor_names.items():
                    if primary_name in subnames:
                        actual_primary_key = key_name
                        break
                
                # If primary_name is not found as a key, use it as the key
                if actual_primary_key is None:
                    actual_primary_key = primary_name
                
                # Get the arrays for all names
                all_arrays = []
                keys_to_remove = set()
                
                for name in names:
                    # Find which key contains this name
                    found_key = None
                    for key_name, subnames in competitor_names.items():
                        if name in subnames:
                            found_key = key_name
                            break
                    
                    if found_key:
                        # Add all subnames from this key
                        all_arrays.extend(competitor_names[found_key])
                        keys_to_remove.add(found_key)
                    else:
                        # If name is not found as a subname, add it as a single item
                        all_arrays.append(name)
                
                # Merge all arrays and remove duplicates
                merged_array = list(set(all_arrays))
                merged_array.sort()
                
                # Update the dictionary using the actual primary key
                competitor_names[actual_primary_key] = merged_array
                
                # Remove all other keys from the dictionary
                for key_to_remove in keys_to_remove:
                    if key_to_remove != actual_primary_key:
                        del competitor_names[key_to_remove]
                
                print(f"✅ Merged {len(names)} names into '{actual_primary_key}'")
                merged_count += 1
                
                # Remove this group from the file (it's been merged)
                similar_groups.remove(group)
                
            else:
                print("Skipped.")
                skipped_count += 1
                
                # Mark this group as reviewed but not merged
                group['reviewed'] = False
                # Note: group is already in similar_groups, so no need to add it back
            
            print(f"Progress: {group_idx + 1}/{groups_to_process} (Merged: {merged_count}, Skipped: {skipped_count})")
        
        # Save the updated competitor names
        print(f"\nSaving updated competitor names...")
        with open(competitor_names_path, 'w', encoding='utf-8') as f:
            json.dump(competitor_names, f, indent=2, ensure_ascii=False)
        
        # Save the updated similar groups file (with reviewed groups and without merged ones)
        print(f"Saving updated similar groups file...")
        with open(similar_names_path, 'w', encoding='utf-8') as f:
            json.dump(similar_groups, f, indent=2, ensure_ascii=False)
        
        # Count remaining unreviewed groups
        remaining_unreviewed = [group for group in similar_groups if 'reviewed' not in group]
        
        print(f"✅ Session completed!")
        print(f"Groups processed in this session: {groups_to_process}")
        print(f"Groups merged: {merged_count}")
        print(f"Groups skipped (marked as reviewed): {skipped_count}")
        print(f"Groups remaining in file: {len(similar_groups)}")
        print(f"Unreviewed groups remaining: {len(remaining_unreviewed)}")
        print(f"Final competitor count: {len(competitor_names)}")
        
        if len(remaining_unreviewed) > 0:
            print(f"\n💡 Run merge_from_file() again to process the next {min(50, len(remaining_unreviewed))} unreviewed groups")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def analyze_multi_version_competitors():
    """
    Analyze competitor names that have multiple versions in their arrays.
    For each competitor with multiple versions, provide detailed information about each version:
    - Number of appearances
    - Divisions by year
    - Competition names
    
    Creates a JSON file with this detailed analysis.
    
    Returns:
        str: Path to the created JSON file, or None if error
    """
    competitor_names_path = "keys/competitor_names.json"
    csv_path = "data/all/all_clean.csv"
    output_path = "all/multi_version_competitors_analysis.json"
    
    if not os.path.exists(competitor_names_path):
        print(f"Competitor names file not found at: {competitor_names_path}")
        return None
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found at: {csv_path}")
        return None
    
    try:
        # Load competitor names
        print("Loading competitor names...")
        with open(competitor_names_path, 'r', encoding='utf-8') as f:
            competitor_names = json.load(f)
        
        # Load CSV data
        print("Loading CSV data...")
        df = pd.read_csv(csv_path, low_memory=False)
        
        print(f"Loaded {len(competitor_names)} competitor entries")
        print(f"Loaded {len(df)} CSV rows")
        
        # Find competitors with multiple versions
        multi_version_competitors = {}
        
        for primary_name, versions in competitor_names.items():
            if len(versions) > 1:
                multi_version_competitors[primary_name] = versions
        
        print(f"Found {len(multi_version_competitors)} competitors with multiple versions")
        
        if not multi_version_competitors:
            print("No competitors with multiple versions found.")
            return None
        
        # Analyze each multi-version competitor
        analysis_results = {}
        
        for primary_name, versions in multi_version_competitors.items():
            print(f"Analyzing: {primary_name} ({len(versions)} versions)")
            
            competitor_analysis = {
                'primary_name': primary_name,
                'total_versions': len(versions),
                'versions': {}
            }
            
            # Analyze each version
            for version in versions:
                # Get all rows for this version
                version_rows = df[df['Competitor Name'] == version]
                
                if version_rows.empty:
                    # Version not found in CSV
                    competitor_analysis['versions'][version] = {
                        'appearances': 0,
                        'years': [],
                        'divisions_by_year': {},
                        'competitions': [],
                        'found_in_csv': False
                    }
                    continue
                
                # Get years and divisions by year
                years = []
                divisions_by_year = {}
                competitions = set()
                locations = set()
                
                for _, row in version_rows.iterrows():
                    # Extract year from Start Date
                    if pd.notna(row.get('Start Date')) and str(row['Start Date']).strip():
                        try:
                            date_str = str(row['Start Date']).strip()
                            year = None
                            
                            if '/' in date_str:
                                parts = date_str.split('/')
                                for part in parts:
                                    if len(part) == 4 and part.isdigit():
                                        year = int(part)
                                        break
                            elif '-' in date_str:
                                parts = date_str.split('-')
                                if len(parts) >= 1 and parts[0].isdigit() and len(parts[0]) == 4:
                                    year = int(parts[0])
                            
                            if year:
                                years.append(year)
                                if year not in divisions_by_year:
                                    divisions_by_year[year] = set()
                                
                                # Add division if available
                                if pd.notna(row.get('Division')) and str(row['Division']).strip():
                                    divisions_by_year[year].add(str(row['Division']).strip())
                        except:
                            pass
                    
                    # Add competition if available
                    if pd.notna(row.get('Competition')) and str(row['Competition']).strip():
                        competitions.add(str(row['Competition']).strip())
                    
                    # Add location combination if available
                    location_parts = []
                    if pd.notna(row.get('Competitor City')) and str(row['Competitor City']).strip():
                        location_parts.append(str(row['Competitor City']).strip())
                    if pd.notna(row.get('Competitor State')) and str(row['Competitor State']).strip():
                        location_parts.append(str(row['Competitor State']).strip())
                    if pd.notna(row.get('Competitor Country')) and str(row['Competitor Country']).strip():
                        location_parts.append(str(row['Competitor Country']).strip())
                    
                    if location_parts:
                        locations.add(', '.join(location_parts))
                
                # Convert sets to sorted lists for JSON serialization
                years = sorted(list(set(years)))
                divisions_by_year = {year: sorted(list(divisions)) for year, divisions in divisions_by_year.items()}
                competitions = sorted(list(competitions))
                locations = sorted(list(locations))
                
                competitor_analysis['versions'][version] = {
                    'appearances': len(version_rows),
                    'years': years,
                    'divisions_by_year': divisions_by_year,
                    'competitions': competitions,
                    'locations': locations,
                    'found_in_csv': True
                }
            
            # Add summary statistics
            total_appearances = sum(v['appearances'] for v in competitor_analysis['versions'].values())
            all_years = set()
            all_divisions = set()
            all_locations = set()
            
            for version_info in competitor_analysis['versions'].values():
                all_years.update(version_info['years'])
                all_locations.update(version_info['locations'])
                for divisions in version_info['divisions_by_year'].values():
                    all_divisions.update(divisions)
            
            competitor_analysis['summary'] = {
                'total_appearances': total_appearances,
                'years_range': f"{min(all_years)}-{max(all_years)}" if all_years else None,
                'all_years': sorted(list(all_years)),
                'all_divisions': sorted(list(all_divisions)),
                'all_locations': sorted(list(all_locations)),
                'different_names': versions
            }
            
            analysis_results[primary_name] = competitor_analysis
        
        # Sort by total appearances (descending)
        sorted_analysis = dict(sorted(
            analysis_results.items(), 
            key=lambda x: x[1]['summary']['total_appearances'], 
            reverse=True
        ))
        
        # Write to JSON file
        print(f"Writing analysis to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sorted_analysis, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully created analysis file: {output_path}")
        print(f"Analyzed {len(sorted_analysis)} competitors with multiple versions")
        
        # Show some statistics
        total_versions = sum(len(comp['versions']) for comp in sorted_analysis.values())
        total_appearances = sum(comp['summary']['total_appearances'] for comp in sorted_analysis.values())
        
        print(f"\nStatistics:")
        print(f"  Total versions across all competitors: {total_versions}")
        print(f"  Total appearances across all versions: {total_appearances}")
        
        # Show top 5 competitors by appearances
        print(f"\nTop 5 competitors by total appearances:")
        for i, (name, analysis) in enumerate(list(sorted_analysis.items())[:5]):
            print(f"{i+1}. {name}")
            print(f"   Different names: {analysis['summary']['different_names']}")
            print(f"   Total appearances: {analysis['summary']['total_appearances']}")
            print(f"   Years: {analysis['summary']['years_range']}")
            print(f"   All divisions: {analysis['summary']['all_divisions']}")
            print(f"   All locations: {analysis['summary']['all_locations']}")
            print()
        
        # Show some examples of version details
        print(f"Example version details for '{list(sorted_analysis.keys())[0]}':")
        first_competitor = list(sorted_analysis.values())[0]
        for version_name, version_info in first_competitor['versions'].items():
            print(f"  Version: {version_name}")
            print(f"    Appearances: {version_info['appearances']}")
            print(f"    Years: {version_info['years']}")
            print(f"    Divisions by year: {version_info['divisions_by_year']}")
            print(f"    Competitions: {version_info['competitions'][:3]}{'...' if len(version_info['competitions']) > 3 else ''}")
            print(f"    Locations: {version_info['locations']}")
            print()
        
        return output_path
        
    except Exception as e:
        print(f"Error analyzing multi-version competitors: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_enhanced_similarity():
    """
    Test function to demonstrate the enhanced similarity algorithm.
    """
    print("Testing Enhanced Similarity Algorithm with ±2 Year Tolerance and Subname Comparison")
    print("=" * 70)
    
    # Test cases with different scenarios
    test_cases = [
        {
            'name1': 'John Smith',
            'name2': 'John A. Smith',
            'subnames1': ['John Smith'],
            'subnames2': ['John A. Smith'],
            'info1': {'years': [2010, 2011, 2012], 'divisions': ['Men\'s Bodybuilding']},
            'info2': {'years': [2010, 2011, 2012], 'divisions': ['Men\'s Bodybuilding']},
            'description': 'Same person, exact year matches'
        },
        {
            'name1': 'John Smith',
            'name2': 'John A. Smith',
            'subnames1': ['John Smith'],
            'subnames2': ['John A. Smith'],
            'info1': {'years': [2010, 2011], 'divisions': ['Men\'s Bodybuilding']},
            'info2': {'years': [2012, 2013], 'divisions': ['Men\'s Bodybuilding']},
            'description': 'Same person, years 2 apart (should overlap with ±2 tolerance)'
        },
        {
            'name1': 'John Smith',
            'name2': 'John A. Smith',
            'subnames1': ['John Smith'],
            'subnames2': ['John A. Smith'],
            'info1': {'years': [2010, 2011], 'divisions': ['Men\'s Bodybuilding']},
            'info2': {'years': [2014, 2015], 'divisions': ['Men\'s Bodybuilding']},
            'description': 'Same person, years 4 apart (no overlap even with ±2 tolerance)'
        },
        {
            'name1': 'John Smith',
            'name2': 'John A. Smith',
            'subnames1': ['John Smith'],
            'subnames2': ['John A. Smith'],
            'info1': {'years': [2010, 2011], 'divisions': ['Men\'s Bodybuilding']},
            'info2': {'years': [2010, 2011], 'divisions': ['Women\'s Physique']},
            'description': 'Same person, same years, different divisions'
        },
        {
            'name1': 'John Smith',
            'name2': 'Jane Smith',
            'subnames1': ['John Smith'],
            'subnames2': ['Jane Smith'],
            'info1': {'years': [2010, 2011], 'divisions': ['Men\'s Bodybuilding']},
            'info2': {'years': [2010, 2011], 'divisions': ['Men\'s Bodybuilding']},
            'description': 'Different people, similar names, same years and divisions'
        },
        {
            'name1': 'John Smith',
            'name2': 'J. Smith',
            'subnames1': ['John Smith', 'Johnny Smith'],
            'subnames2': ['J. Smith', 'James Smith'],
            'info1': {'years': [2010, 2011], 'divisions': ['Men\'s Bodybuilding']},
            'info2': {'years': [2010, 2011], 'divisions': ['Men\'s Bodybuilding']},
            'description': 'Same person, different key names, similar subnames'
        },
        {
            'name1': 'John Smith',
            'name2': 'Johnny Smith',
            'subnames1': ['John Smith'],
            'subnames2': ['Johnny Smith'],
            'info1': {'years': [2010, 2011], 'divisions': ['Men\'s Bodybuilding']},
            'info2': {'years': [2010, 2011], 'divisions': ['Men\'s Bodybuilding']},
            'description': 'Same person, different variations (would be found in multiple checks)'
        },
        {
            'name1': 'Carlos Majid Rabiel',
            'name2': 'Carlos Rabiei',
            'subnames1': ['Carlos Majid Rabiel', 'Carlos Rabiei', 'Carlos Rabiel', 'Carlos Majid Rabiei'],
            'subnames2': ['Carlos Rabiei'],
            'info1': {'years': [2010, 2011, 2012], 'divisions': ['Men\'s Bodybuilding'], 'locations': ['California, USA', 'Texas, USA']},
            'info2': {'years': [2011, 2012], 'divisions': ['Men\'s Bodybuilding'], 'locations': ['California, USA']},
            'description': 'Complex case with multiple subnames and combined information'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Names: '{test_case['name1']}' vs '{test_case['name2']}'")
        print(f"Subnames: {test_case['subnames1']} vs {test_case['subnames2']}")
        
        # Calculate similarity with and without additional info
        basic_similarity = calculate_name_similarity(test_case['name1'], test_case['name2'])
        enhanced_similarity = calculate_name_similarity(
            test_case['name1'], test_case['name2'], 
            test_case['info1'], test_case['info2']
        )
        
        # Calculate subname similarities
        subname_similarities = []
        for subname1 in test_case['subnames1']:
            for subname2 in test_case['subnames2']:
                if subname1 != subname2:
                    subname_sim = calculate_name_similarity(subname1, subname2, test_case['info1'], test_case['info2'])
                    subname_similarities.append(subname_sim)
        
        max_subname_similarity = max(subname_similarities) if subname_similarities else 0
        max_overall_similarity = max(enhanced_similarity, max_subname_similarity)
        
        print(f"Basic similarity (key names only): {basic_similarity:.3f}")
        print(f"Enhanced similarity (key names with years/divisions): {enhanced_similarity:.3f}")
        print(f"Best subname similarity: {max_subname_similarity:.3f}")
        print(f"Overall max similarity: {max_overall_similarity:.3f}")
        print(f"Improvement: {max_overall_similarity - basic_similarity:+.3f}")
        
        # Show overlap details with expanded ranges
        years1 = set(test_case['info1']['years'])
        years2 = set(test_case['info2']['years'])
        divisions1 = set(test_case['info1']['divisions'])
        divisions2 = set(test_case['info2']['divisions'])
        
        # Calculate expanded ranges
        expanded_years1 = set()
        for year in years1:
            expanded_years1.update(range(year - 2, year + 3))
        
        expanded_years2 = set()
        for year in years2:
            expanded_years2.update(range(year - 2, year + 3))
        
        overlap_years = expanded_years1.intersection(expanded_years2)
        exact_matches = len(years1.intersection(years2))
        division_overlap = len(divisions1.intersection(divisions2))
        
        print(f"Original years: {sorted(years1)} vs {sorted(years2)}")
        print(f"Expanded ranges: {sorted(expanded_years1)[:8]}{'...' if len(expanded_years1) > 8 else ''} vs {sorted(expanded_years2)[:8]}{'...' if len(expanded_years2) > 8 else ''}")
        print(f"Year overlap: {len(overlap_years)} years in expanded range")
        if exact_matches > 0:
            print(f"Exact year matches: {exact_matches} years")
        print(f"Division overlap: {division_overlap}/{max(len(divisions1), len(divisions2))} divisions")
        
        if max_overall_similarity >= 0.7:
            print("✅ Would be grouped together")
        else:
            print("❌ Would NOT be grouped together")

def test_merge_with_subname_primary():
    """
    Test function to demonstrate how the merge function handles cases where primary_name is only a subname.
    """
    print("Testing Merge with Subname Primary")
    print("=" * 50)
    
    # Create test data using actual names from the user's data
    test_competitor_names = {
        "Vlasta Gruberova": ["Vlasta Gruberova"],
        "Vojtech Koritenskya": ["Vojtech Koritensky", "Vojtech Koritenskya", "Vojtěch Koritenský"]
    }
    
    # Create test group - simulate a case where "Vojtěch Koritenský" is the primary_name
    # but it's only a subname in the "Vojtech Koritenskya" key
    test_group = {
        "names": ["Vlasta Gruberova", "Vojtěch Koritenský"],
        "primary_name": "Vojtěch Koritenský",  # This is only a subname!
        "average_similarity": 0.85,
        "info": {
            "Vlasta Gruberova": {"appearances": 5, "years": [2010, 2011], "divisions": ["Women's Physique"]},
            "Vojtěch Koritenský": {"appearances": 12, "years": [2011, 2012], "divisions": ["Men's Bodybuilding"]}
        }
    }
    
    print("Before merging:")
    for key, values in test_competitor_names.items():
        print(f"  '{key}': {values}")
    
    # Simulate the merge logic
    names = test_group['names']
    primary_name = test_group['primary_name']
    
    # Find the actual key that contains the primary_name
    actual_primary_key = None
    for key_name, subnames in test_competitor_names.items():
        if primary_name in subnames:
            actual_primary_key = key_name
            break
    
    if actual_primary_key is None:
        actual_primary_key = primary_name
    
    print(f"\nPrimary name from group: '{primary_name}'")
    print(f"Actual key found: '{actual_primary_key}'")
    
    # Get the arrays for all names - this is the key fix!
    # We need to find which keys contain each name in the group
    all_arrays = []
    keys_to_remove = set()
    
    for name in names:
        # Find which key contains this name
        found_key = None
        for key_name, subnames in test_competitor_names.items():
            if name in subnames:
                found_key = key_name
                break
        
        if found_key:
            # Add all subnames from this key
            all_arrays.extend(test_competitor_names[found_key])
            keys_to_remove.add(found_key)
        else:
            # If name is not found as a subname, add it as a single item
            all_arrays.append(name)
    
    # Merge all arrays and remove duplicates
    merged_array = list(set(all_arrays))
    merged_array.sort()
    
    # Update the dictionary using the actual primary key
    test_competitor_names[actual_primary_key] = merged_array
    
    # Remove all other keys from the dictionary
    for key_to_remove in keys_to_remove:
        if key_to_remove != actual_primary_key:
            del test_competitor_names[key_to_remove]
    
    print(f"\nAfter merging:")
    for key, values in test_competitor_names.items():
        print(f"  '{key}': {values}")
    
    print(f"\n✅ Successfully merged into '{actual_primary_key}'")
    print(f"✅ All subnames combined: {merged_array}")
    
    # Test the reverse case - what if "Vlasta Gruberova" was the primary_name?
    print(f"\n" + "="*50)
    print("Testing reverse case - 'Vlasta Gruberova' as primary_name")
    
    # Reset test data
    test_competitor_names = {
        "Vlasta Gruberova": ["Vlasta Gruberova"],
        "Vojtech Koritenskya": ["Vojtech Koritensky", "Vojtech Koritenskya", "Vojtěch Koritenský"]
    }
    
    test_group_reverse = {
        "names": ["Vlasta Gruberova", "Vojtěch Koritenský"],
        "primary_name": "Vlasta Gruberova",  # This IS a key
        "average_similarity": 0.85,
        "info": {
            "Vlasta Gruberova": {"appearances": 5, "years": [2010, 2011], "divisions": ["Women's Physique"]},
            "Vojtěch Koritenský": {"appearances": 12, "years": [2011, 2012], "divisions": ["Men's Bodybuilding"]}
        }
    }
    
    print("Before merging:")
    for key, values in test_competitor_names.items():
        print(f"  '{key}': {values}")
    
    # Simulate the merge logic
    names = test_group_reverse['names']
    primary_name = test_group_reverse['primary_name']
    
    # Find the actual key that contains the primary_name
    actual_primary_key = None
    for key_name, subnames in test_competitor_names.items():
        if primary_name in subnames:
            actual_primary_key = key_name
            break
    
    if actual_primary_key is None:
        actual_primary_key = primary_name
    
    print(f"\nPrimary name from group: '{primary_name}'")
    print(f"Actual key found: '{actual_primary_key}'")
    
    # Get the arrays for all names - this is the key fix!
    # We need to find which keys contain each name in the group
    all_arrays = []
    keys_to_remove = set()
    
    for name in names:
        # Find which key contains this name
        found_key = None
        for key_name, subnames in test_competitor_names.items():
            if name in subnames:
                found_key = key_name
                break
        
        if found_key:
            # Add all subnames from this key
            all_arrays.extend(test_competitor_names[found_key])
            keys_to_remove.add(found_key)
        else:
            # If name is not found as a subname, add it as a single item
            all_arrays.append(name)
    
    # Merge all arrays and remove duplicates
    merged_array = list(set(all_arrays))
    merged_array.sort()
    
    # Update the dictionary using the actual primary key
    test_competitor_names[actual_primary_key] = merged_array
    
    # Remove all other keys from the dictionary
    for key_to_remove in keys_to_remove:
        if key_to_remove != actual_primary_key:
            del test_competitor_names[key_to_remove]
    
    print(f"\nAfter merging:")
    for key, values in test_competitor_names.items():
        print(f"  '{key}': {values}")
    
    print(f"\n✅ Successfully merged into '{actual_primary_key}'")
    print(f"✅ All subnames combined: {merged_array}")

def normalize_for_pattern(name):
    """Normalize name for letter pattern comparison."""
    if not name:
        return ""
    
    # Convert to lowercase and remove extra spaces
    normalized = ' '.join(name.lower().split())
    
    # Remove common punctuation
    normalized = normalized.replace('.', '').replace(',', '').replace('-', ' ').replace("'", '')
    
    # Remove extra spaces again
    normalized = ' '.join(normalized.split())
    
    return normalized

def get_letter_pattern(name):
    """Get sorted letter pattern from name."""
    normalized = normalize_for_pattern(name)
    # Remove spaces and sort letters
    letters = ''.join(c for c in normalized if c.isalpha())
    return ''.join(sorted(letters))

def are_similar_patterns(name1, name2):
    """Check if two names have similar letter patterns."""
    norm1 = normalize_for_pattern(name1)
    norm2 = normalize_for_pattern(name2)
    
    # If exactly the same after normalization
    if norm1 == norm2:
        return True, "exact_match"
    
    # Check for reversed names (e.g., "John Smith" vs "Smith John")
    words1 = norm1.split()
    words2 = norm2.split()
    
    if len(words1) >= 2 and len(words2) >= 2:
        # Check if names are reversed
        if words1 == words2[::-1]:
            return True, "reversed_names"
    
    # Check for space variations (e.g., "JohnSmith" vs "John Smith")
    no_space1 = norm1.replace(' ', '')
    no_space2 = norm2.replace(' ', '')
    
    if no_space1 == no_space2:
        return True, "space_variation"
    
    # Check for hyphen variations (e.g., "John-Smith" vs "John Smith")
    no_hyphen1 = norm1.replace('-', ' ')
    no_hyphen2 = norm2.replace('-', ' ')
    
    if no_hyphen1 == no_hyphen2:
        return True, "hyphen_variation"
    
    # Check for exact anagrams (same letters, same frequency)
    def get_letter_count(name):
        """Get letter frequency count."""
        letter_count = {}
        for char in name.lower():
            if char.isalpha():
                letter_count[char] = letter_count.get(char, 0) + 1
        return letter_count
    
    letter_count1 = get_letter_count(norm1)
    letter_count2 = get_letter_count(norm2)
    
    if letter_count1 == letter_count2:
        return True, "exact_anagram"
    
    # Check for subset names (one name is contained within the other)
    # Only if they share the same letters in the same order
    if len(words1) >= 2 and len(words2) >= 2:
        # Check if one name is a subset of the other (missing middle name, etc.)
        if set(words1).issubset(set(words2)) or set(words2).issubset(set(words1)):
            # Additional check: the remaining words should be similar
            if len(words1) == 1 or len(words2) == 1:
                return True, "subset_names"
            elif len(words1) == 2 and len(words2) == 3:
                # Check if it's just a middle name difference
                if words1[0] == words2[0] and words1[-1] == words2[-1]:
                    return True, "middle_name_difference"
            elif len(words2) == 2 and len(words1) == 3:
                if words2[0] == words1[0] and words2[-1] == words1[-1]:
                    return True, "middle_name_difference"
    
    # Check for common name variations (Jr/Sr, III/3, etc.)
    variations = [
        ("jr", "junior"),
        ("sr", "senior"),
        ("iii", "3"),
        ("ii", "2"),
        ("iv", "4"),
        ("jr.", "junior"),
        ("sr.", "senior"),
    ]
    
    for var1, var2 in variations:
        if var1 in norm1 and var2 in norm2:
            # Check if the rest is exactly the same
            rest1 = norm1.replace(var1, '').strip()
            rest2 = norm2.replace(var2, '').strip()
            if rest1 == rest2:
                return True, "name_variation"
        elif var2 in norm1 and var1 in norm2:
            rest1 = norm1.replace(var2, '').strip()
            rest2 = norm2.replace(var1, '').strip()
            if rest1 == rest2:
                return True, "name_variation"
    
    return False, None

def find_similar_letter_patterns():
    """
    Find competitor names with similar letter patterns, handling cases like:
    - Reversed first/last names (e.g., "John Smith" vs "Smith John")
    - Added/removed spaces (e.g., "JohnSmith" vs "John Smith")
    - Case variations
    - Common name variations
    
    Creates a JSON file with groups of similar letter patterns.
    
    Returns:
        str: Path to the created JSON file, or None if error
    """
    competitor_names_path = "keys/competitor_names.json"
    output_path = "all/similar_letter_patterns.json"
    
    if not os.path.exists(competitor_names_path):
        print(f"Competitor names file not found at: {competitor_names_path}")
        return None
    
    try:
        # Load competitor names
        print("Loading competitor names...")
        with open(competitor_names_path, 'r', encoding='utf-8') as f:
            competitor_names = json.load(f)
        
        print(f"Loaded {len(competitor_names)} competitor entries")
        
        # Find similar patterns
        print("Finding similar letter patterns...")
        similar_groups = []
        processed_names = set()
        
        all_names = list(competitor_names.keys())
        
        for i, name1 in enumerate(all_names):
            if i % 100 == 0:
                print(f"Processing name {i+1}/{len(all_names)}")
            
            if name1 in processed_names:
                continue
            
            # Find all names similar to name1 (including subnames from other keys)
            similar_to_name1 = [name1]
            similarity_types = []
            
            # Compare with other keys
            for j, name2 in enumerate(all_names[i+1:], i+1):
                if name2 in processed_names:
                    continue
                
                # Compare key names
                is_similar, similarity_type = are_similar_patterns(name1, name2)
                if is_similar:
                    similar_to_name1.append(name2)
                    similarity_types.append(similarity_type)
                
                # Compare name1 with subnames from name2's array
                for subname2 in competitor_names[name2]:
                    if subname2 != name2:  # Don't compare with the key itself (already done above)
                        is_similar, similarity_type = are_similar_patterns(name1, subname2)
                        if is_similar:
                            similar_to_name1.append(name2)
                            similarity_types.append(similarity_type)
                            break  # Found a match, no need to check other subnames from this key
            
            # Compare subnames from name1's array with other keys
            for subname1 in competitor_names[name1]:
                if subname1 != name1:  # Don't compare with the key itself (already done above)
                    for j, name2 in enumerate(all_names[i+1:], i+1):
                        if name2 in processed_names:
                            continue
                        
                        # Compare subname1 with key name2
                        is_similar, similarity_type = are_similar_patterns(subname1, name2)
                        if is_similar:
                            similar_to_name1.append(name2)
                            similarity_types.append(similarity_type)
                            break  # Found a match, no need to check other keys
                        
                        # Compare subname1 with subnames from name2's array
                        for subname2 in competitor_names[name2]:
                            if subname2 != name2:  # Don't compare with the key itself
                                is_similar, similarity_type = are_similar_patterns(subname1, subname2)
                                if is_similar:
                                    similar_to_name1.append(name2)
                                    similarity_types.append(similarity_type)
                                    break  # Found a match, no need to check other subnames from this key
                        else:
                            continue  # No match found in this key's subnames, continue to next key
                        break  # Match found, break out of key loop
            
            # If we found similar names, create a group
            if len(similar_to_name1) > 1:
                # Get all subnames for each name in the group
                all_subnames = []
                for name in similar_to_name1:
                    all_subnames.extend(competitor_names[name])
                
                # Remove duplicates and sort
                all_subnames = sorted(list(set(all_subnames)))
                
                # Create group info
                group_info = {
                    'names': similar_to_name1,
                    'all_subnames': all_subnames,
                    'primary_name': max(similar_to_name1, key=lambda x: len(competitor_names[x])),
                    'similarity_types': similarity_types,
                    'letter_patterns': [get_letter_pattern(name) for name in similar_to_name1],
                    'normalized_names': [normalize_for_pattern(name) for name in similar_to_name1]
                }
                
                similar_groups.append(group_info)
                
                # Mark all names as processed
                processed_names.update(similar_to_name1)
        
        # Sort by number of names in group (descending)
        similar_groups.sort(key=lambda x: len(x['names']), reverse=True)
        
        print(f"Found {len(similar_groups)} groups with similar letter patterns")
        
        # Create the output structure: key = primary_name, value = array of all similar names
        output_dict = {}
        
        for group in similar_groups:
            primary_name = group['primary_name']
            all_subnames = group['all_subnames']
            
            # Use the primary name as the key and all subnames as the value
            output_dict[primary_name] = all_subnames
        
        # Write to JSON file
        print(f"Writing results to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_dict, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully created file: {output_path}")
        
        # Show some statistics
        total_names_in_groups = sum(len(group['names']) for group in similar_groups)
        total_subnames_in_groups = sum(len(group['all_subnames']) for group in similar_groups)
        
        print(f"\nStatistics:")
        print(f"  Total groups found: {len(similar_groups)}")
        print(f"  Total names in groups: {total_names_in_groups}")
        print(f"  Total subnames in groups: {total_subnames_in_groups}")
        print(f"  Output JSON keys: {len(output_dict)}")
        
        # Show top 10 groups
        print(f"\nTop 10 groups with most names:")
        for i, group in enumerate(similar_groups[:10]):
            print(f"{i+1}. Primary: '{group['primary_name']}'")
            print(f"   All subnames: {group['all_subnames']}")
            print(f"   Similarity types: {group['similarity_types']}")
            print()
        
        # Show examples by similarity type
        similarity_type_counts = {}
        for group in similar_groups:
            for sim_type in group['similarity_types']:
                similarity_type_counts[sim_type] = similarity_type_counts.get(sim_type, 0) + 1
        
        print(f"Similarity types found:")
        for sim_type, count in sorted(similarity_type_counts.items()):
            print(f"  {sim_type}: {count} groups")
        
        return output_path
        
    except Exception as e:
        print(f"Error finding similar letter patterns: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_letter_pattern_functions():
    """
    Test function to demonstrate the letter pattern matching functions.
    """
    print("Testing Letter Pattern Functions")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        ("John Smith", "Smith John", "Reversed names"),
        ("John Smith", "JohnSmith", "No space vs space"),
        ("John-Smith", "John Smith", "Hyphen vs space"),
        ("John Smith", "john smith", "Case difference"),
        ("John Smith", "John A. Smith", "Middle name difference"),
        ("John Smith Jr", "John Smith Junior", "Jr vs Junior"),
        ("John Smith III", "John Smith 3", "III vs 3"),
        ("John Smith", "Jane Smith", "Different names (should NOT match)"),
        ("John Smith", "Johnny Smith", "Similar names (should NOT match)"),
        ("Carlos Majid Rabiel", "Carlos Rabiei", "Complex case (should NOT match)"),
        ("Vojtech Koritensky", "Vojtěch Koritenský", "Accent variations (should NOT match)"),
        ("Silent", "Listen", "Exact anagram"),
        ("Dormitory", "Dirty Room", "Exact anagram"),
        ("A Gentleman", "Elegant Man", "Exact anagram"),
    ]
    
    for name1, name2, description in test_cases:
        print(f"\nTest: {description}")
        print(f"Names: '{name1}' vs '{name2}'")
        
        is_similar, similarity_type = are_similar_patterns(name1, name2)
        
        print(f"Similar: {is_similar}")
        if is_similar:
            print(f"Type: {similarity_type}")
        
        # Show normalized versions
        norm1 = normalize_for_pattern(name1)
        norm2 = normalize_for_pattern(name2)
        print(f"Normalized: '{norm1}' vs '{norm2}'")
        
        # Show letter patterns
        pattern1 = get_letter_pattern(name1)
        pattern2 = get_letter_pattern(name2)
        print(f"Letter patterns: '{pattern1}' vs '{pattern2}'")
    
    # Test with sample competitor data to show subname comparison
    print(f"\n" + "="*50)
    print("Testing with sample competitor data (subname comparisons)")
    
    sample_competitors = {
        "John Smith": ["John Smith", "Johnny Smith", "J. Smith"],
        "Smith John": ["Smith John", "John Smith"],
        "Jane Doe": ["Jane Doe", "J. Doe"],
        "Carlos Majid Rabiel": ["Carlos Majid Rabiel", "Carlos Rabiei", "Carlos Rabiel"]
    }
    
    # Test key vs key
    print(f"\nKey vs Key comparison:")
    is_similar, similarity_type = are_similar_patterns("John Smith", "Smith John")
    print(f"'John Smith' vs 'Smith John': {is_similar} ({similarity_type})")
    
    # Test key vs subname from different key
    print(f"\nKey vs Subname comparison:")
    is_similar, similarity_type = are_similar_patterns("John Smith", "Johnny Smith")
    print(f"'John Smith' vs 'Johnny Smith': {is_similar} ({similarity_type})")
    
    # Test subname vs subname from different keys
    print(f"\nSubname vs Subname comparison:")
    is_similar, similarity_type = are_similar_patterns("Johnny Smith", "Carlos Rabiei")
    print(f"'Johnny Smith' vs 'Carlos Rabiei': {is_similar} ({similarity_type})")
    
    # Test subname vs key
    print(f"\nSubname vs Key comparison:")
    is_similar, similarity_type = are_similar_patterns("Carlos Rabiei", "Carlos Majid Rabiel")
    print(f"'Carlos Rabiei' vs 'Carlos Majid Rabiel': {is_similar} ({similarity_type})")

def test_letter_pattern_output_format():
    """
    Test function to demonstrate the new JSON output format.
    """
    print("Testing Letter Pattern Output Format")
    print("=" * 50)
    
    # Sample similar groups (what the function would find)
    sample_groups = [
        {
            'names': ['John Smith', 'Smith John'],
            'all_subnames': ['John Smith', 'Johnny Smith', 'J. Smith', 'Smith John'],
            'primary_name': 'John Smith',
            'similarity_types': ['reversed_names']
        },
        {
            'names': ['Carlos Majid Rabiel', 'Carlos Rabiei'],
            'all_subnames': ['Carlos Majid Rabiel', 'Carlos Rabiei', 'Carlos Rabiel', 'Carlos Majid Rabiei'],
            'primary_name': 'Carlos Majid Rabiel',
            'similarity_types': ['subset_names']
        }
    ]
    
    # Create the output structure: key = primary_name, value = array of all similar names
    output_dict = {}
    
    for group in sample_groups:
        primary_name = group['primary_name']
        all_subnames = group['all_subnames']
        
        # Use the primary name as the key and all subnames as the value
        output_dict[primary_name] = all_subnames
    
    print("Sample output JSON structure:")
    print(json.dumps(output_dict, indent=2, ensure_ascii=False))
    
    print(f"\nOutput format explanation:")
    print(f"- Keys: Primary names (the main name for each group)")
    print(f"- Values: Arrays containing ALL similar names found (including subnames)")
    print(f"- Total keys: {len(output_dict)}")
    
    for key, value in output_dict.items():
        print(f"  '{key}': {len(value)} names - {value}")

def analyze_competitor_names_file():
    """
    Analyze the competitor_names.json file to show statistics and check for duplicates.
    """
    competitor_names_path = "keys/competitor_names.json"
    
    if not os.path.exists(competitor_names_path):
        print(f"Competitor names file not found at: {competitor_names_path}")
        return None
    
    try:
        # Load competitor names
        print("Loading competitor names...")
        with open(competitor_names_path, 'r', encoding='utf-8') as f:
            competitor_names = json.load(f)
        
        print(f"✅ Successfully loaded competitor names file")
        
        # Basic statistics
        total_keys = len(competitor_names)
        print(f"\n📊 Basic Statistics:")
        print(f"  Total keys: {total_keys}")
        
        # Count names in arrays
        all_names = []
        total_names_in_arrays = 0
        key_name_counts = []
        
        for key, names_array in competitor_names.items():
            total_names_in_arrays += len(names_array)
            all_names.extend(names_array)
            key_name_counts.append((key, len(names_array)))
        
        print(f"  Total names in all arrays: {total_names_in_arrays}")
        print(f"  Average names per key: {total_names_in_arrays / total_keys:.2f}")
        
        # Show distribution of array sizes
        print(f"\n📈 Array Size Distribution:")
        size_counts = {}
        for _, count in key_name_counts:
            size_counts[count] = size_counts.get(count, 0) + 1
        
        for size in sorted(size_counts.keys()):
            count = size_counts[size]
            percentage = (count / total_keys) * 100
            print(f"  {size} name(s): {count} keys ({percentage:.1f}%)")
        
        # Show keys with most names
        print(f"\n🏆 Top 10 Keys with Most Names:")
        sorted_by_count = sorted(key_name_counts, key=lambda x: x[1], reverse=True)
        for i, (key, count) in enumerate(sorted_by_count[:10]):
            print(f"  {i+1}. '{key}': {count} names")
        
        # Check for duplicate names across all arrays
        print(f"\n🔍 Checking for Duplicate Names...")
        
        # Count occurrences of each name
        name_counts = {}
        for name in all_names:
            name_counts[name] = name_counts.get(name, 0) + 1
        
        # Find duplicates
        duplicates = {name: count for name, count in name_counts.items() if count > 1}
        
        if duplicates:
            print(f"  Found {len(duplicates)} duplicate names:")
            print(f"  Total duplicate occurrences: {sum(duplicates.values())}")
            
            # Show top duplicates
            sorted_duplicates = sorted(duplicates.items(), key=lambda x: x[1], reverse=True)
            print(f"\n  Top 10 Most Duplicated Names:")
            for i, (name, count) in enumerate(sorted_duplicates[:10]):
                print(f"    {i+1}. '{name}': appears {count} times")
            
            # Find which keys contain each duplicate
            print(f"\n  Detailed Duplicate Analysis:")
            for name, count in sorted_duplicates[:5]:  # Show first 5 duplicates
                print(f"\n    '{name}' (appears {count} times) found in:")
                for key, names_array in competitor_names.items():
                    if name in names_array:
                        print(f"      - '{key}'")
        else:
            print(f"  ✅ No duplicate names found!")
        
        # Show some examples of names that appear in multiple keys
        if duplicates:
            print(f"\n📋 Examples of Names in Multiple Keys:")
            for name, count in sorted_duplicates[:3]:
                print(f"\n  '{name}' appears in {count} different keys:")
                for key, names_array in competitor_names.items():
                    if name in names_array:
                        print(f"    - '{key}': {names_array}")
        
        # Summary
        print(f"\n📋 Summary:")
        print(f"  Total unique names across all arrays: {len(set(all_names))}")
        print(f"  Total name occurrences (including duplicates): {len(all_names)}")
        if duplicates:
            print(f"  Duplicate names found: {len(duplicates)}")
            print(f"  Duplicate occurrences: {sum(duplicates.values()) - len(duplicates)}")
        else:
            print(f"  ✅ No duplicates found - all names are unique!")
        
        return {
            'total_keys': total_keys,
            'total_names': total_names_in_arrays,
            'unique_names': len(set(all_names)),
            'duplicates': len(duplicates) if duplicates else 0,
            'duplicate_occurrences': sum(duplicates.values()) - len(duplicates) if duplicates else 0
        }
        
    except Exception as e:
        print(f"Error analyzing competitor names file: {e}")
        import traceback
        traceback.print_exc()
        return None

def find_specific_competitor_names(target_names):
    """
    Find all rows where the competitor names match the specified target names.
    
    Args:
        target_names (list): List of competitor names to search for
    
    Returns:
        None: Prints results to console
    """
    csv_path = "data/all/all_clean.csv"
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found at: {csv_path}")
        return
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path, low_memory=False)
        
        # Search for rows with the specified competitor names
        matching_rows = df[df['Competitor Name'].isin(target_names)]
        
        if matching_rows.empty:
            print(f"No rows found with competitor names: {target_names}")
            return
        
        print(f"Found {len(matching_rows)} rows with competitor names: {target_names}")
        print("=" * 80)
        
        # Display all rows
        for idx, row in matching_rows.iterrows():
            print(f"Row {idx + 1}:")
            for column in df.columns:
                value = row[column]
                if pd.notna(value):  # Only print non-null values
                    print(f"  {column}: {value}")
            print("-" * 40)
        
        # Show summary statistics
        print("\nSummary by competitor name:")
        for name in target_names:
            name_rows = matching_rows[matching_rows['Competitor Name'] == name]
            if not name_rows.empty:
                print(f"\n'{name}': {len(name_rows)} rows")
                print(f"  Competitions: {name_rows['Competition'].unique()}")
                print(f"  Divisions: {name_rows['Division'].unique()}")
                
                # Show date information
                if 'Start Date' in name_rows.columns:
                    print(f"  Start Dates: {name_rows['Start Date'].unique()}")
                if 'End Date' in name_rows.columns:
                    print(f"  End Dates: {name_rows['End Date'].unique()}")
                if 'Year' in name_rows.columns:
                    print(f"  Years: {name_rows['Year'].unique()}")
                
                print(f"  Places: {name_rows['Place'].unique()}")
        
        # Show summary table
        print("\nSummary table:")
        summary_columns = ['Competitor Name', 'Competition', 'Division', 'Place', 'Start Date', 'End Date', 'Year']
        available_columns = [col for col in summary_columns if col in df.columns]
        print(matching_rows[available_columns].to_string(index=False))
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        import traceback
        traceback.print_exc()

def analyze_competition_names_file_duplicates():
    """
    Analyze the competition_names.json file to check for duplicates in keys and values.
    """
    competition_names_path = "keys/competition_names.json"
    
    if not os.path.exists(competition_names_path):
        print(f"Competition names file not found at: {competition_names_path}")
        return None
    
    try:
        # Load competition names
        print("Loading competition names...")
        with open(competition_names_path, 'r', encoding='utf-8') as f:
            competition_names = json.load(f)
        
        print(f"✅ Successfully loaded competition names file")
        
        # Collect all keys and values from the nested structure
        all_keys = []
        all_values = []
        key_paths = []  # Store the full path to each key for reporting
        
        def traverse_structure(data, current_path=""):
            """Recursively traverse the nested structure to collect keys and values."""
            if isinstance(data, dict):
                for key, value in data.items():
                    new_path = f"{current_path}.{key}" if current_path else key
                    if isinstance(value, list):
                        # This is a competition key with an array of competition names
                        all_keys.append(key)
                        key_paths.append(new_path)
                        all_values.extend(value)
                    else:
                        # This is a nested object, continue traversing
                        traverse_structure(value, new_path)
        
        traverse_structure(competition_names)
        
        # Basic statistics
        total_keys = len(all_keys)
        total_values = len(all_values)
        unique_values = len(set(all_values))
        
        print(f"\n📊 Basic Statistics:")
        print(f"  Total competition keys: {total_keys}")
        print(f"  Total competition names in all arrays: {total_values}")
        print(f"  Unique competition names: {unique_values}")
        print(f"  Average competition names per key: {total_values / total_keys:.2f}")
        
        # Check for duplicate keys
        print(f"\n🔍 Checking for Duplicate Keys...")
        key_counts = {}
        for key in all_keys:
            key_counts[key] = key_counts.get(key, 0) + 1
        
        duplicate_keys = {key: count for key, count in key_counts.items() if count > 1}
        
        if duplicate_keys:
            print(f"  Found {len(duplicate_keys)} duplicate keys:")
            print(f"  Total duplicate key occurrences: {sum(duplicate_keys.values())}")
            
            # Show duplicate keys with their paths
            print(f"\n  Duplicate Keys and Their Locations:")
            for key, count in sorted(duplicate_keys.items()):
                print(f"\n    '{key}' (appears {count} times) found at:")
                for i, path in enumerate(key_paths):
                    if path.split('.')[-1] == key:  # Get the last part of the path
                        print(f"      {i+1}. {path}")
        else:
            print(f"  ✅ No duplicate keys found!")
        
        # Check for duplicate values
        print(f"\n🔍 Checking for Duplicate Competition Names...")
        value_counts = {}
        for value in all_values:
            value_counts[value] = value_counts.get(value, 0) + 1
        
        duplicate_values = {value: count for value, count in value_counts.items() if count > 1}
        
        if duplicate_values:
            print(f"  Found {len(duplicate_values)} duplicate competition names:")
            print(f"  Total duplicate occurrences: {sum(duplicate_values.values())}")
            
            # Show top duplicates
            sorted_duplicates = sorted(duplicate_values.items(), key=lambda x: x[1], reverse=True)
            print(f"\n  Top 10 Most Duplicated Competition Names:")
            for i, (name, count) in enumerate(sorted_duplicates[:10]):
                print(f"    {i+1}. '{name}': appears {count} times")
            
            # Find which keys contain each duplicate
            print(f"\n  Detailed Duplicate Analysis:")
            for name, count in sorted_duplicates[:5]:  # Show first 5 duplicates
                print(f"\n    '{name}' (appears {count} times) found in:")
                for key_path in key_paths:
                    # Get the actual data at this path
                    path_parts = key_path.split('.')
                    current_data = competition_names
                    for part in path_parts:
                        if part in current_data:
                            current_data = current_data[part]
                        else:
                            break
                    else:
                        # We found the path, check if it contains the duplicate name
                        if isinstance(current_data, list) and name in current_data:
                            print(f"      - {key_path}")
        
        else:
            print(f"  ✅ No duplicate competition names found!")
        
        # Show some examples of competition names that appear in multiple keys
        if duplicate_values:
            print(f"\n📋 Examples of Competition Names in Multiple Keys:")
            for name, count in sorted_duplicates[:3]:
                print(f"\n  '{name}' appears in {count} different keys:")
                for key_path in key_paths:
                    # Get the actual data at this path
                    path_parts = key_path.split('.')
                    current_data = competition_names
                    for part in path_parts:
                        if part in current_data:
                            current_data = current_data[part]
                        else:
                            break
                    else:
                        # We found the path, check if it contains the duplicate name
                        if isinstance(current_data, list) and name in current_data:
                            print(f"    - {key_path}: {current_data}")
        
        # Show distribution of array sizes
        print(f"\n📈 Array Size Distribution:")
        size_counts = {}
        for key_path in key_paths:
            # Get the actual data at this path
            path_parts = key_path.split('.')
            current_data = competition_names
            for part in path_parts:
                if part in current_data:
                    current_data = current_data[part]
                else:
                    break
            else:
                if isinstance(current_data, list):
                    size = len(current_data)
                    size_counts[size] = size_counts.get(size, 0) + 1
        
        for size in sorted(size_counts.keys()):
            count = size_counts[size]
            percentage = (count / total_keys) * 100
            print(f"  {size} competition name(s): {count} keys ({percentage:.1f}%)")
        
        # Show keys with most competition names
        print(f"\n🏆 Top 10 Keys with Most Competition Names:")
        key_size_pairs = []
        for key_path in key_paths:
            # Get the actual data at this path
            path_parts = key_path.split('.')
            current_data = competition_names
            for part in path_parts:
                if part in current_data:
                    current_data = current_data[part]
                else:
                    break
            else:
                if isinstance(current_data, list):
                    key_size_pairs.append((key_path, len(current_data)))
        
        sorted_by_size = sorted(key_size_pairs, key=lambda x: x[1], reverse=True)
        for i, (key_path, size) in enumerate(sorted_by_size[:10]):
            print(f"  {i+1}. '{key_path}': {size} competition names")
        
        # Summary
        print(f"\n📋 Summary:")
        print(f"  Total unique competition names across all arrays: {unique_values}")
        print(f"  Total competition name occurrences (including duplicates): {total_values}")
        if duplicate_keys:
            print(f"  Duplicate keys found: {len(duplicate_keys)}")
            print(f"  Duplicate key occurrences: {sum(duplicate_keys.values()) - len(duplicate_keys)}")
        else:
            print(f"  ✅ No duplicate keys found - all keys are unique!")
        
        if duplicate_values:
            print(f"  Duplicate competition names found: {len(duplicate_values)}")
            print(f"  Duplicate competition name occurrences: {sum(duplicate_values.values()) - len(duplicate_values)}")
        else:
            print(f"  ✅ No duplicate competition names found - all names are unique!")
        
        return {
            'total_keys': total_keys,
            'total_values': total_values,
            'unique_values': unique_values,
            'duplicate_keys': len(duplicate_keys) if duplicate_keys else 0,
            'duplicate_key_occurrences': sum(duplicate_keys.values()) - len(duplicate_keys) if duplicate_keys else 0,
            'duplicate_values': len(duplicate_values) if duplicate_values else 0,
            'duplicate_value_occurrences': sum(duplicate_values.values()) - len(duplicate_values) if duplicate_values else 0
        }
        
    except Exception as e:
        print(f"Error analyzing competition names file: {e}")
        import traceback
        traceback.print_exc()
        return None

def find_missing_rows_in_copy():
    """
    Find rows that exist in data/all/all_clean.csv but not in all_clean copy.csv
    using the combination of Start Date and Competitor Name as the key.
    
    Returns:
        None: Prints results to console
    """
    original_csv_path = "data/all/all_clean.csv"
    copy_csv_path = "data/all/all_clean_copy.csv"
    
    if not os.path.exists(original_csv_path):
        print(f"Original CSV file not found at: {original_csv_path}")
        return
    
    if not os.path.exists(copy_csv_path):
        print(f"Copy CSV file not found at: {copy_csv_path}")
        return
    
    try:
        # Read both CSV files
        print("Reading original CSV file...")
        df_original = pd.read_csv(original_csv_path, low_memory=False)
        
        print("Reading copy CSV file...")
        df_copy = pd.read_csv(copy_csv_path, low_memory=False)
        
        print(f"Original CSV: {len(df_original)} rows")
        print(f"Copy CSV: {len(df_copy)} rows")
        
        # Check if required columns exist
        required_columns = ['Start Date', 'Competitor Name']
        for col in required_columns:
            if col not in df_original.columns:
                print(f"Error: Column '{col}' not found in original CSV")
                return
            if col not in df_copy.columns:
                print(f"Error: Column '{col}' not found in copy CSV")
                return
        
        # Create keys for both dataframes
        print("Creating keys for comparison...")
        
        def create_key(row):
            """Create a key from Start Date and Competitor Name."""
            start_date = str(row['Start Date']).strip() if pd.notna(row['Start Date']) else ''
            competitor_name = str(row['Competitor Name']).strip() if pd.notna(row['Competitor Name']) else ''
            return f"{start_date}|{competitor_name}"
        
        # Create keys for original dataframe
        df_original['key'] = df_original.apply(create_key, axis=1)
        original_keys = set(df_original['key'].dropna())
        
        # Create keys for copy dataframe
        df_copy['key'] = df_copy.apply(create_key, axis=1)
        copy_keys = set(df_copy['key'].dropna())
        
        print(f"Original CSV unique keys: {len(original_keys)}")
        print(f"Copy CSV unique keys: {len(copy_keys)}")
        
        # Find keys that are in original but not in copy
        missing_keys = original_keys - copy_keys
        
        print(f"Keys in original but not in copy: {len(missing_keys)}")
        
        if not missing_keys:
            print("✅ All rows from the original CSV are present in the copy CSV!")
            return
        
        # Find rows in original that have missing keys
        missing_rows = df_original[df_original['key'].isin(missing_keys)]
        
        print(f"\nFound {len(missing_rows)} rows that are in the original but not in the copy:")
        print("=" * 80)
        
        # Display missing rows
        for idx, row in missing_rows.iterrows():
            print(f"Row {idx + 1}:")
            print(f"  Key: {row['key']}")
            print(f"  Start Date: {row['Start Date']}")
            print(f"  Competitor Name: {row['Competitor Name']}")
            
            # Show other important columns
            important_columns = ['Competition', 'Division', 'Place', 'Year', 'Source']
            for col in important_columns:
                if col in df_original.columns and pd.notna(row[col]):
                    print(f"  {col}: {row[col]}")
            
            print("-" * 40)
        
        # Show summary statistics
        print(f"\n📊 Summary of Missing Rows:")
        
        # Count by competition
        if 'Competition' in missing_rows.columns:
            competition_counts = missing_rows['Competition'].value_counts()
            print(f"\nMissing rows by Competition (top 10):")
            for competition, count in competition_counts.head(10).items():
                print(f"  {competition}: {count} rows")
        
        # Count by division
        if 'Division' in missing_rows.columns:
            division_counts = missing_rows['Division'].value_counts()
            print(f"\nMissing rows by Division (top 10):")
            for division, count in division_counts.head(10).items():
                print(f"  {division}: {count} rows")
        
        # Count by year (extracted from Start Date)
        print(f"\nMissing rows by Year:")
        year_counts = {}
        for _, row in missing_rows.iterrows():
            if pd.notna(row['Start Date']) and str(row['Start Date']).strip():
                try:
                    date_str = str(row['Start Date']).strip()
                    year = None
                    
                    if '/' in date_str:
                        parts = date_str.split('/')
                        for part in parts:
                            if len(part) == 4 and part.isdigit():
                                year = part
                                break
                    elif '-' in date_str:
                        parts = date_str.split('-')
                        if len(parts) >= 1 and parts[0].isdigit() and len(parts[0]) == 4:
                            year = parts[0]
                    
                    if year:
                        year_counts[year] = year_counts.get(year, 0) + 1
                except:
                    pass
        
        for year in sorted(year_counts.keys()):
            print(f"  {year}: {year_counts[year]} rows")
        
        # Count by source
        if 'Source' in missing_rows.columns:
            source_counts = missing_rows['Source'].value_counts()
            print(f"\nMissing rows by Source:")
            for source, count in source_counts.items():
                print(f"  {source}: {count} rows")
        
        # Show some examples of keys that exist in copy but not in original (for verification)
        extra_keys = copy_keys - original_keys
        if extra_keys:
            print(f"\n📋 Note: {len(extra_keys)} keys exist in copy but not in original")
            print("This might indicate additional rows in the copy file.")
        
        # Save missing rows to a new CSV file for further analysis
        output_path = "all/missing_rows.csv"
        missing_rows.to_csv(output_path, index=False)
        print(f"\n💾 Missing rows saved to: {output_path}")
        
        # Show summary table
        print(f"\n📋 Summary Table of Missing Rows:")
        summary_columns = ['Start Date', 'Competitor Name', 'Competition', 'Division', 'Place', 'Year', 'Source']
        available_columns = [col for col in summary_columns if col in missing_rows.columns]
        print(missing_rows[available_columns].to_string(index=False))
        
    except Exception as e:
        print(f"Error comparing CSV files: {e}")
        import traceback
        traceback.print_exc()

def find_multiple_events_per_year():
    """
    Find competitions that appear multiple times within the same year with different dates.
    Excludes same-day events and those with small date differences of ±5 days.
    
    This function analyzes the competition data to identify:
    - Competitions that occur multiple times in the same year
    - Different dates for the same competition (excluding ±5 day differences)
    - Events from different sources (2024, scorecards, npcnews, musclememory)
    
    Returns:
        None: Prints results to console and saves to JSON file
    """
    csv_path = "data/all/all_clean.csv"
    output_path = "all/multiple_events_per_year.json"
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found at: {csv_path}")
        return
    
    try:
        # Read the CSV file
        print("Reading CSV file...")
        df = pd.read_csv(csv_path, low_memory=False)
        
        print(f"Loaded {len(df)} rows")
        
        # Check if required columns exist
        required_columns = ['Competition', 'Start Date', 'End Date', 'Source']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Error: Missing required columns: {missing_columns}")
            return
        
        # Function to extract year from date string
        def extract_year(date_str):
            """Extract year from date string, handling various formats."""
            if pd.isna(date_str) or str(date_str).strip() == '':
                return None
            
            try:
                date_str = str(date_str).strip()
                
                # Handle different date formats
                if '/' in date_str:
                    parts = date_str.split('/')
                    for part in parts:
                        if len(part) == 4 and part.isdigit():
                            return int(part)
                elif '-' in date_str:
                    parts = date_str.split('-')
                    if len(parts) >= 1 and parts[0].isdigit() and len(parts[0]) == 4:
                        return int(parts[0])
                
                # Try parsing as datetime
                from datetime import datetime
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%Y/%m/%d', '%d/%m/%Y']:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.year
                    except ValueError:
                        continue
                
                return None
            except:
                return None
        
        # Function to parse date string to datetime
        def parse_date(date_str):
            """Parse date string to datetime object."""
            if pd.isna(date_str) or str(date_str).strip() == '':
                return None
            
            try:
                date_str = str(date_str).strip()
                from datetime import datetime
                
                # Try different date formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%Y/%m/%d', '%d/%m/%Y']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
                
                return None
            except:
                return None
        
        # Function to check if two date ranges overlap significantly
        def dates_overlap_significantly(start1, end1, start2, end2, source1, source2, tolerance_days=5):
            """
            Check if two date ranges overlap significantly (within tolerance).
            
            Args:
                start1, end1: First date range
                start2, end2: Second date range
                source1, source2: Sources for the two events
                tolerance_days: Number of days tolerance for considering dates "the same"
            
            Returns:
                bool: True if dates overlap significantly
            """
            if not all([start1, end1, start2, end2]):
                return False
            
            # Use larger tolerance for npcnews vs scorecards/musclememory
            if (source1 == 'npcnews' and source2 in ['scorecards', 'musclememory']) or \
               (source2 == 'npcnews' and source1 in ['scorecards', 'musclememory']):
                tolerance_days = 10
            
            # Calculate the difference between the start dates
            start_diff = abs((start1 - start2).days)
            
            # Calculate the difference between the end dates
            end_diff = abs((end1 - end2).days)
            
            # If both start and end dates are within tolerance, consider them the same event
            return start_diff <= tolerance_days and end_diff <= tolerance_days
        
        # Add year column
        print("Extracting years from dates...")
        df['Year'] = df['Start Date'].apply(extract_year)
        
        # Parse dates for comparison
        print("Parsing dates for comparison...")
        df['Start_Date_Parsed'] = df['Start Date'].apply(parse_date)
        df['End_Date_Parsed'] = df['End Date'].apply(parse_date)
        
        # Remove rows without valid years
        df_with_years = df[df['Year'].notna()].copy()
        print(f"Rows with valid years: {len(df_with_years)}")
        
        # Group by competition and year
        print("Analyzing competitions by year...")
        competition_year_groups = {}
        
        for _, row in df_with_years.iterrows():
            competition = str(row['Competition']).strip()
            year = row['Year']
            source = str(row['Source']).strip()
            start_date = row['Start_Date_Parsed']
            end_date = row['End_Date_Parsed']
            
            key = (competition, year)
            
            if key not in competition_year_groups:
                competition_year_groups[key] = []
            
            competition_year_groups[key].append({
                'source': source,
                'start_date': start_date,
                'end_date': end_date,
                'start_date_str': row['Start Date'],
                'end_date_str': row['End Date'],
                'row_data': row.to_dict()
            })
        
        # Find competitions with multiple events in the same year
        multiple_events = {}
        
        for (competition, year), events in competition_year_groups.items():
            if len(events) > 1:
                # Sort events by start date
                events.sort(key=lambda x: x['start_date'] if x['start_date'] else datetime.min)
                
                # Group events that are the same (within tolerance)
                event_groups = []
                processed_events = set()
                
                for i, event1 in enumerate(events):
                    if i in processed_events:
                        continue
                    
                    current_group = [event1]
                    processed_events.add(i)
                    
                    for j, event2 in enumerate(events[i+1:], i+1):
                        if j in processed_events:
                            continue
                        
                        # Check if these events are the same (within tolerance)
                        if dates_overlap_significantly(
                            event1['start_date'], event1['end_date'],
                            event2['start_date'], event2['end_date'],
                            event1['source'], event2['source']
                        ):
                            current_group.append(event2)
                            processed_events.add(j)
                    
                    event_groups.append(current_group)
                
                # Only include if there are multiple different event groups
                if len(event_groups) > 1:
                    multiple_events[(competition, year)] = {
                        'competition': competition,
                        'year': year,
                        'total_events': len(events),
                        'different_event_groups': len(event_groups),
                        'event_groups': event_groups,
                        'sources': list(set(event['source'] for event in events))
                    }
        
        print(f"Found {len(multiple_events)} competitions with multiple events in the same year")
        
        if not multiple_events:
            print("✅ No competitions found with multiple events in the same year!")
            return
        
        # Sort by year, then by competition name
        sorted_multiple_events = dict(sorted(
            multiple_events.items(),
            key=lambda x: (x[1]['year'], x[1]['competition'])
        ))
        
        # Display all results
        for (competition, year), data in sorted_multiple_events.items():
            print(f"\n{'='*80}")
            print(f"Competition: {competition}")
            print(f"Year: {year}")
            print(f"Sources: {', '.join(data['sources'])}")
            
            for i, group in enumerate(data['event_groups'], 1):
                print(f"\n  Event Group {i}:")
                
                # Get unique dates and their sources for this group
                date_sources = {}
                for event in group:
                    if event['start_date_str']:
                        date = event['start_date_str']
                        source = event['source']
                        if date not in date_sources:
                            date_sources[date] = set()
                        date_sources[date].add(source)
                
                # Sort dates and display with sources
                sorted_dates = sorted(date_sources.keys())
                for date in sorted_dates:
                    sources = sorted(date_sources[date])
                    print(f"    {date} (sources: {', '.join(sources)})")
        
        # Create summary statistics
        # Count by year
        year_counts = {}
        for (_, year), data in sorted_multiple_events.items():
            year_counts[year] = year_counts.get(year, 0) + 1
        
        summary_stats = {
            'total_competitions': len(sorted_multiple_events),
            'by_year': year_counts,
            'by_source': {},
            'competitions': {}
        }
        
        # Count by source
        all_sources = set()
        for data in sorted_multiple_events.values():
            all_sources.update(data['sources'])
        
        for source in sorted(all_sources):
            count = sum(1 for data in sorted_multiple_events.values() if source in data['sources'])
            summary_stats['by_source'][source] = count
        
        # Add competition details
        for (competition, year), data in sorted_multiple_events.items():
            summary_stats['competitions'][f"{competition}_{year}"] = {
                'competition': competition,
                'year': year,
                'total_events': data['total_events'],
                'different_event_groups': data['different_event_groups'],
                'sources': data['sources'],
                'event_groups': [
                    {
                        'group_size': len(group),
                        'dates': [
                            {
                                'source': event['source'],
                                'start_date': event['start_date_str'],
                                'end_date': event['end_date_str']
                            }
                            for event in group
                        ]
                    }
                    for group in data['event_groups']
                ]
            }
        
        # Save results to JSON file
        print(f"\n💾 Saving results to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary_stats, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results saved to: {output_path}")
        

        
        # Show statistics about date differences
        print(f"\n📊 Date Difference Analysis:")
        all_date_differences = []
        
        for (competition, year), data in sorted_multiple_events.items():
            for i, group1 in enumerate(data['event_groups']):
                for j, group2 in enumerate(data['event_groups'][i+1:], i+1):
                    # Compare dates between different groups
                    for event1 in group1:
                        for event2 in group2:
                            if event1['start_date'] and event2['start_date']:
                                diff = abs((event1['start_date'] - event2['start_date']).days)
                                all_date_differences.append(diff)
        
        if all_date_differences:
            all_date_differences.sort()
            print(f"  Minimum date difference: {min(all_date_differences)} days")
            print(f"  Maximum date difference: {max(all_date_differences)} days")
            print(f"  Average date difference: {sum(all_date_differences) / len(all_date_differences):.1f} days")
            print(f"  Median date difference: {all_date_differences[len(all_date_differences)//2]} days")
        
        return summary_stats
        
    except Exception as e:
        print(f"Error analyzing multiple events per year: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Find multiple events per year
    print("Finding multiple events per year...")
    find_multiple_events_per_year()
    
    #print("\n" + "="*80)
    
    # Find missing rows in copy
    #print("Finding rows that are in original CSV but not in copy CSV...")
    #find_missing_rows_in_copy()
    
    #print("\n" + "="*80)
    
    # Find specific competitor names
    #print("Searching for specific competitor names...")
    #find_specific_competitor_names(["14", "16"])
    
    #print("\n" + "="*80)
    
    # Analyze competitor names file
    #print("Analyzing competitor names file...")
    #analyze_competitor_names_file()
    
    #print("\n" + "="*80)
    
    # Analyze competition names file for duplicates
    #print("Analyzing competition names file for duplicates...")
    #analyze_competition_names_file_duplicates()
    
    #print("\n" + "="*80)
    
    # Test the letter pattern output format
    #test_letter_pattern_output_format()
    
    #print("\n" + "="*80)
    
    # Test the letter pattern functions
    #test_letter_pattern_functions()
    
    #print("\n" + "="*80)
    
    # Find similar letter patterns
    #print("Finding similar letter patterns...")
    #find_similar_letter_patterns()
    
    #print("\n" + "="*80)
    
    # Test the merge function with subname primary
    #test_merge_with_subname_primary()
    
    #print("\n" + "="*80)
    
    # Test the enhanced similarity algorithm
    #test_enhanced_similarity()
    
    #print("\n" + "="*80)
    
    # Search for empty divisions
    #print("Searching for rows with empty division column...")
    #find_empty_divisions()
    
    #print("\n" + "="*80)
    
    # Search for Olympia divisions
    #print("Searching for rows with 'olympia' in Division column...")
    #find_olympia_divisions()
    
    #print("\n" + "="*80)
    
    # Example usage of other functions
    #print_new_divisions()
    
    # Create JSON file
    #print("\n" + "="*50)
    #create_divisions_json()
    
    # Search for Round 2/3 entries
    #print("Searching for rows with entries in Round 2 or Round 3...")
    #find_round_2_3_entries()
    
    # Get unique locations and countries
    #print("Extracting unique locations and countries...")
    #get_unique_locations_countries()

    # Get unique competitor names (detailed version)
    #print("Extracting unique competitor names with details...")
    #get_unique_competitor_names_detailed()

    # Get unique competitor names (simple version)
    #print("Extracting unique competitor names (simple version)")
    #get_unique_competitor_names()

    # Analyze and merge competitor names
    #print("Analyzing and merging competitor names")
    #analyze_and_merge_competitor_names()

    # Find and merge similar names
    #print("Finding and merging similar names")
    #find_similar_names_to_file()
    
    # Interactive merging of similar names
    #print("Starting interactive merging process...")
    #merge_from_file()
    
    # Analyze multi-version competitors
    #print("Analyzing multi-version competitors")
    #analyze_multi_version_competitors()
    
    # Find multiple events per year
    #print("Finding multiple events per year...")
    #find_multiple_events_per_year()
    
    pass  # Add this to fix the indentation error
