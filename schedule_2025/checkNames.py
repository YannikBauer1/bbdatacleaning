import csv
import json
import os

def load_json_file(file_path):
    """Load and return JSON data from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def get_all_names_from_json(json_data):
    """Extract all competition names from JSON arrays"""
    all_names = set()
    for key, name_list in json_data.items():
        if isinstance(name_list, list):
            all_names.update(name_list)
    return all_names

def check_competition_names():
    # File paths
    csv_file = "data/all_competitions.csv"
    comp_name_dir_file = "../all/comp_name_dir.json"
    competition_names_others_file = "../all/competition_names_others.json"
    
    # Load JSON files
    comp_name_dir = load_json_file(comp_name_dir_file)
    competition_names_others = load_json_file(competition_names_others_file)
    
    # Get all names from both JSON files
    comp_name_dir_names = get_all_names_from_json(comp_name_dir)
    competition_names_others_names = get_all_names_from_json(competition_names_others)
    
    # Combine all names from both JSON files
    all_json_names = comp_name_dir_names.union(competition_names_others_names)
    
    # Read CSV file and extract competition names
    csv_competition_names = set()
    missing_names = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                competition_name = row['Competition Name'].strip()
                csv_competition_names.add(competition_name)
                
                # Check if this name exists in either JSON file
                if competition_name not in all_json_names:
                    missing_names.append(competition_name)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Print results
    print(f"Total competitions in CSV: {len(csv_competition_names)}")
    print(f"Total names in comp_name_dir.json: {len(comp_name_dir_names)}")
    print(f"Total names in competition_names_others.json: {len(competition_names_others_names)}")
    print(f"Total unique names in both JSON files: {len(all_json_names)}")
    print(f"Missing names: {len(missing_names)}")
    
    if missing_names:
        print("\nMissing competition names:")
        for name in sorted(missing_names):
            print(f"  - {name}")
    else:
        print("\nAll competition names from CSV are found in the JSON files!")
    
    # Also check for exact matches and similar matches
    print("\n" + "="*50)
    print("DETAILED ANALYSIS:")
    print("="*50)
    
    found_in_comp_name_dir = []
    found_in_others = []
    not_found = []
    
    for name in sorted(csv_competition_names):
        if name in comp_name_dir_names:
            found_in_comp_name_dir.append(name)
        elif name in competition_names_others_names:
            found_in_others.append(name)
        else:
            not_found.append(name)
    
    print(f"\nFound in comp_name_dir.json ({len(found_in_comp_name_dir)}):")
    for name in found_in_comp_name_dir:
        print(f"  ✓ {name}")
    
    print(f"\nFound in competition_names_others.json ({len(found_in_others)}):")
    for name in found_in_others:
        print(f"  ✓ {name}")
    
    print(f"\nNOT FOUND in either JSON file ({len(not_found)}):")
    for name in not_found:
        print(f"  ✗ {name}")

if __name__ == "__main__":
    check_competition_names()
