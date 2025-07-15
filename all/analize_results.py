import pandas as pd
import numpy as np
import json

def convert_numpy_types(obj):
    """
    Convert numpy types to standard Python types for JSON serialization
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

def check_duplicate_athletes():
    """
    Check for rows with the same year, competition, division, subdivision, and place
    but different athlete names AND different sources (cross-source conflicts).
    Excludes conflicts that are already known in cross_source_conflicts_remain.json
    """
    df = pd.read_csv('data/all/results.csv')
    
    # Load existing conflicts to exclude them
    try:
        with open('cross_source_conflicts_remain.json', 'r') as f:
            existing_conflicts = json.load(f)
        
        # Create a set of conflict keys to exclude (year_competition_place)
        exclude_keys = set()
        for conflict in existing_conflicts:
            key = f"{conflict['year']}_{conflict['competition_name_key']}_{conflict['place']}"
            exclude_keys.add(key)
            
    except FileNotFoundError:
        exclude_keys = set()
    
    # Create a key for grouping based on the specified columns (excluding source)
    df['group_key'] = df['year'].astype(str) + '_' + \
                     df['competition_name_key'].astype(str) + '_' + \
                     df['Division'].astype(str) + '_' + \
                     df['Division Subtype'].astype(str) + '_' + \
                     df['Place'].astype(str)
    
    # Create a combined competition key that matches the JSON format
    df['combined_competition_key'] = df['competition_name_key'].astype(str) + '_' + \
                                    df['Division'].astype(str) + '_' + \
                                    df['Division Subtype'].astype(str)
    
    # Create the proper exclude key that matches the JSON format
    df['json_exclude_key'] = df['year'].astype(str) + '_' + \
                            df['combined_competition_key'] + '_' + \
                            df['Place'].astype(str)
    
    # Group by this key and check for multiple athlete names
    duplicates = []
    json_output = []
    skipped_count = 0
    
    for group_key, group in df.groupby('group_key'):
        # Check if this group should be excluded based on year, competition, and place only
        exclude_key = group['json_exclude_key'].iloc[0]
        
        if exclude_key in exclude_keys:
            skipped_count += 1
            continue
            
        unique_athletes = group['athlete_name_key'].unique()
        unique_sources = group['Source'].unique()
        
        # Only consider duplicates if there are multiple athletes AND multiple sources
        if len(unique_athletes) > 1 and len(unique_sources) > 1:
            # Parse the group key to extract components
            parts = group_key.split('_')
            year = parts[0]
            place = parts[-1]
            competition_name_key = '_'.join(parts[1:-1])
            
            # Create source-specific athlete lists
            source_athletes = {}
            for source in unique_sources:
                source_athletes[source] = group[group['Source'] == source]['athlete_name_key'].tolist()
            
            # Create JSON object
            json_obj = {
                'year': year,
                'competition_name_key': competition_name_key,
                'place': place
            }
            json_obj.update(source_athletes)
            
            json_output.append(json_obj)
            
            duplicates.append({
                'group_key': group_key,
                'athletes': unique_athletes.tolist(),
                'count': len(unique_athletes),
                'sources': unique_sources.tolist(),
                'rows': group.to_dict('records')
            })
    
    print(f"Found {len(duplicates)} NEW groups with duplicate athletes (excluding known conflicts)")
    print(f"Skipped {skipped_count} known conflicts")
    
    # Write JSON output to file
    with open('cross_source_conflicts_new.json', 'w') as f:
        json.dump(json_output, f, indent=2)
    
    return duplicates

def find_same_place_not_last():
    """
    Find entries that have the same place for each competition in each year and division,
    but is not the last place of that division.
    """
    df = pd.read_csv('data/all/results.csv')
    
    # Group by year, competition, division, and subdivision
    same_place_entries = []
    
    for (year, competition, division, subtype), group in df.groupby(['year', 'competition_name_key', 'Division', 'Division Subtype']):
        # Get the maximum place (last place) for this division
        max_place = group['Place'].max()
        
        # Find places that appear more than once but are not the last place
        place_counts = group['Place'].value_counts()
        
        for place, count in place_counts.items():
            if count > 1 and place != max_place:
                # Get all entries for this place
                place_entries = group[group['Place'] == place]
                
                # Extract only athlete_name_key and source from entries
                simplified_entries = []
                for _, row in place_entries.iterrows():
                    simplified_entries.append({
                        'athlete_name_key': str(row['athlete_name_key']),
                        'source': str(row['Source'])
                    })
                
                same_place_entries.append({
                    'year': int(year),
                    'competition': str(competition),
                    'division': str(division),
                    'subtype': str(subtype),
                    'place': int(place),
                    'max_place': int(max_place),
                    'entries': simplified_entries
                })
    
    # Write results to JSON file
    with open('same_place_not_last.json', 'w') as f:
        json.dump(same_place_entries, f, indent=2)
    
    print(f"Found {len(same_place_entries)} cases where multiple athletes have the same place (not last place)")
    print("Results written to same_place_not_last.json")
    
    return same_place_entries

def find_duplicated_names_in_competitions():
    """
    Find and print duplicated athlete names for each competition in each year in each division/subdivision.
    This helps identify cases where the same athlete appears multiple times in the same competition.
    """
    df = pd.read_csv('data/all/results.csv')
    
    # Group by year, competition, division, and subdivision
    duplicated_names = []
    
    for (year, competition, division, subtype), group in df.groupby(['year', 'competition_name_key', 'Division', 'Division Subtype']):
        # Count occurrences of each athlete name
        athlete_counts = group['athlete_name_key'].value_counts()
        
        # Find athletes that appear more than once
        duplicated_athletes = athlete_counts[athlete_counts > 1]
        
        if len(duplicated_athletes) > 0:
            competition_data = {
                'year': int(year),
                'competition': str(competition),
                'division': str(division),
                'subtype': str(subtype),
                'duplicated_athletes': []
            }
            
            for athlete_name, count in duplicated_athletes.items():
                # Get all entries for this athlete in this competition
                athlete_entries = group[group['athlete_name_key'] == athlete_name]
                
                entries_details = []
                for _, row in athlete_entries.iterrows():
                    entries_details.append({
                        'place': int(row['Place']),
                        'source': str(row['Source']),
                        'athlete_name_key': str(row['athlete_name_key'])
                    })
                
                competition_data['duplicated_athletes'].append({
                    'athlete_name': str(athlete_name),
                    'count': int(count),
                    'entries': entries_details
                })
            
            duplicated_names.append(competition_data)
    
    # Print results in a readable format
    print(f"\n=== DUPLICATED ATHLETE NAMES BY COMPETITION ===\n")
    
    for comp in duplicated_names:
        print(f"Year: {comp['year']}")
        print(f"Competition: {comp['competition']}")
        print(f"Division: {comp['division']}")
        print(f"Subtype: {comp['subtype']}")
        print(f"Duplicated athletes: {len(comp['duplicated_athletes'])}")
        print("-" * 50)
        
        for athlete in comp['duplicated_athletes']:
            print(f"  Athlete: {athlete['athlete_name']} (appears {athlete['count']} times)")
            for entry in athlete['entries']:
                print(f"    - Place: {entry['place']}, Source: {entry['source']}")
            print()
        
        print("=" * 80)
        print()
    
    # Write detailed results to JSON file
    with open('duplicated_names_by_competition.json', 'w') as f:
        json.dump(duplicated_names, f, indent=2, default=convert_numpy_types)
    
    print(f"Found {len(duplicated_names)} competitions with duplicated athlete names")
    print("Detailed results written to duplicated_names_by_competition.json")
    
    return duplicated_names

if __name__ == "__main__":
    check_duplicate_athletes()
    #find_same_place_not_last()
    find_duplicated_names_in_competitions()
