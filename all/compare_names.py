import json

def find_missing_names():
    """
    Find competition names from competition_names.json that are not present
    in comp_name_dir.json or competition_names_others.json
    """
    # Load the JSON files
    with open('all/competition_names.json', 'r') as f:
        competition_names = json.load(f)
    
    with open('all/comp_name_dir.json', 'r') as f:
        comp_name_dir = json.load(f)
    
    with open('all/competition_names_others.json', 'r') as f:
        competition_names_others = json.load(f)
    
    # Collect all names from competition_names.json (the ones in the arrays)
    all_names_from_main = set()
    for names_list in competition_names.values():
        all_names_from_main.update(names_list)
    
    # Collect all names from comp_name_dir.json
    all_names_from_dir = set()
    for names_list in comp_name_dir.values():
        all_names_from_dir.update(names_list)
    
    # Collect all names from competition_names_others.json
    all_names_from_others = set()
    for names_list in competition_names_others.values():
        all_names_from_others.update(names_list)
    
    # Combine the names from both comparison files
    all_names_in_comparison = all_names_from_dir.union(all_names_from_others)
    
    # Find names that are in competition_names.json but not in the comparison files
    missing_names = all_names_from_main - all_names_in_comparison
    
    # Print the missing names
    print(f"Found {len(missing_names)} names that are in competition_names.json but not in comp_name_dir.json or competition_names_others.json:")
    print()
    
    for name in sorted(missing_names):
        print(f"  - {name}")
    
    return missing_names

if __name__ == "__main__":
    find_missing_names()
