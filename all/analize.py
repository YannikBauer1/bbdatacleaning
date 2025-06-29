import pandas as pd
import os
import json
from difflib import SequenceMatcher
from collections import defaultdict

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
    Extract unique Location and Country entries from the CSV file,
    order them alphabetically, and write them to a JSON file.
    
    Returns:
        str: Path to the created JSON file, or None if error
    """
    csv_path = "data/all/all_clean.csv"
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found at: {csv_path}")
        return None
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Get unique values from Location and Country columns
        unique_entries = set()
        
        # Extract unique locations (non-null, non-empty)
        if 'Location' in df.columns:
            locations = df['Location'].dropna()
            locations = locations[locations.astype(str).str.strip() != '']
            unique_entries.update(locations.unique())
        
        # Extract unique countries (non-null, non-empty)
        if 'Country' in df.columns:
            countries = df['Country'].dropna()
            countries = countries[countries.astype(str).str.strip() != '']
            unique_entries.update(countries.unique())
        
        # Convert to list and sort alphabetically
        all_entries = sorted(list(unique_entries))
        
        # Define output file path
        output_path = "all/locations_countries.json"
        
        # Write to JSON file with nice formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_entries, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully created JSON file: {output_path}")
        print(f"Contains {len(all_entries)} unique locations and countries")
        print(f"First few entries: {all_entries[:5]}{'...' if len(all_entries) > 5 else ''}")
        
        return output_path
        
    except Exception as e:
        print(f"Error processing CSV file: {e}")
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
    #print("Extracting unique locations and countries...")
    #get_unique_locations_countries()

    # Get unique competitor names (detailed version)
    print("Extracting unique competitor names with details...")
    get_unique_competitor_names_detailed()

    # Get unique competitor names (simple version)
    print("Extracting unique competitor names (simple version)")
    get_unique_competitor_names()

    # Analyze and merge competitor names
    print("Analyzing and merging competitor names")
    analyze_and_merge_competitor_names()
