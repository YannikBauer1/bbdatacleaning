import pandas as pd
import os
import json

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
