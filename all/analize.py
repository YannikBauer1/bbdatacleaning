import pandas as pd
import os
import json
from difflib import SequenceMatcher
from collections import defaultdict
import sys
import tty
import termios  # For Unix-like systems

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
            
            # Skip if already processed in this session
            if name1 in processed_names:
                continue
            
            # Find all names similar to name1
            similar_to_name1 = [name1]
            
            for j, name2 in enumerate(all_names[i+1:], i+1):
                # Skip if already processed in this session
                if name2 in processed_names:
                    continue
                
                similarity = calculate_name_similarity(name1, name2)
                
                # Only consider pairs with high similarity
                if similarity >= 0.7:
                    similar_to_name1.append(name2)
                    print(f"Found similar: {name1} <-> {name2} (similarity: {similarity:.2f})")
            
            # If we found similar names, create a group
            if len(similar_to_name1) > 1:
                # Calculate average similarity for the group
                similarities = []
                for name2 in similar_to_name1[1:]:  # Skip the first name (name1)
                    sim = calculate_name_similarity(name1, name2)
                    similarities.append(sim)
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
                
                # Mark all names in this group as processed
                processed_names.update(similar_to_name1)
                
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

def calculate_name_similarity(name1, name2):
    """
    Calculate similarity between two names, handling various name variations.
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
        return 0.9
    
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
    combined_score = (sequence_similarity * 0.4) + (word_overlap * 0.6)
    
    # Boost score if they share common words
    if len(common_words) >= 2:
        combined_score += 0.1
    elif len(common_words) >= 1:
        combined_score += 0.05
    
    return min(combined_score, 1.0)

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
                
                # Get the arrays for all names
                all_arrays = []
                for name in names:
                    all_arrays.extend(competitor_names[name])
                
                # Merge all arrays and remove duplicates
                merged_array = list(set(all_arrays))
                merged_array.sort()
                
                # Update the dictionary
                competitor_names[primary_name] = merged_array
                
                # Remove all other names from the dictionary
                for name in names:
                    if name != primary_name:
                        del competitor_names[name]
                
                print(f"✅ Merged {len(names)} names into '{primary_name}'")
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

if __name__ == "__main__":
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
    print("Extracting unique locations and countries...")
    get_unique_locations_countries()

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
    
    pass  # Add this to fix the indentation error
