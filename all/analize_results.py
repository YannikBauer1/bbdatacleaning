import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

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

def find_athletes_same_date_range():
    """
    Find athletes who appear in competitions within the same date range (±4 days).
    This is physically impossible and indicates data errors.
    Excludes legitimate cases where athletes compete in multiple divisions at the same competition.
    """
    # Load the results and events data
    results_df = pd.read_csv('data/all/results.csv')
    events_df = pd.read_csv('data/all/events.csv')
    
    # Filter events that have date information
    events_with_dates = events_df[events_df['start_date'].notna() & (events_df['start_date'] != '')].copy()
    
    # Convert start_date to datetime
    events_with_dates['start_date'] = pd.to_datetime(events_with_dates['start_date'])
    
    # Merge results with events to get competition dates
    merged_df = results_df.merge(
        events_with_dates[['competition_key', 'year', 'start_date']], 
        left_on=['competition_name_key', 'year'], 
        right_on=['competition_key', 'year'], 
        how='inner'
    )
    
    # Group by athlete and find competitions within ±4 days
    athlete_conflicts = []
    
    for athlete_name in merged_df['athlete_name_key'].unique():
        athlete_competitions = merged_df[merged_df['athlete_name_key'] == athlete_name].copy()
        
        if len(athlete_competitions) < 2:
            continue
            
        # Sort by date
        athlete_competitions = athlete_competitions.sort_values('start_date')
        
        conflicts = []
        
        # Check each competition against others within ±4 days
        for i, (idx1, comp1) in enumerate(athlete_competitions.iterrows()):
            date1 = comp1['start_date']
            
            for j, (idx2, comp2) in enumerate(athlete_competitions.iterrows()):
                if i >= j:  # Skip already checked pairs and self-comparison
                    continue
                    
                date2 = comp2['start_date']
                days_diff = abs((date2 - date1).days)
                
                # Only consider conflicts if:
                # 1. Within ±4 days AND
                # 2. Different competitions (not same competition, different divisions)
                if days_diff <= 4 and comp1['competition_name_key'] != comp2['competition_name_key']:
                    conflict = {
                        'competition1': {
                            'name': comp1['competition_name_key'],
                            'year': comp1['year'],
                            'date': comp1['start_date'].strftime('%Y-%m-%d'),
                            'division': comp1['Division'],
                            'subtype': comp1['Division Subtype'],
                            'place': comp1['Place'],
                            'source': comp1['Source']
                        },
                        'competition2': {
                            'name': comp2['competition_name_key'],
                            'year': comp2['year'],
                            'date': comp2['start_date'].strftime('%Y-%m-%d'),
                            'division': comp2['Division'],
                            'subtype': comp2['Division Subtype'],
                            'place': comp2['Place'],
                            'source': comp2['Source']
                        },
                        'days_difference': days_diff
                    }
                    conflicts.append(conflict)
        
        if conflicts:
            athlete_conflicts.append({
                'athlete_name': athlete_name,
                'conflicts': conflicts
            })
    
    # Write results to JSON file
    with open('athletes_same_date_range.json', 'w') as f:
        json.dump(athlete_conflicts, f, indent=2, default=convert_numpy_types)
    
    # Print summary
    print(f"\n=== ATHLETES IN DIFFERENT COMPETITIONS WITHIN ±4 DAYS ===\n")
    print(f"Found {len(athlete_conflicts)} athletes with impossible date conflicts")
    print(f"Total conflicts: {sum(len(athlete['conflicts']) for athlete in athlete_conflicts)}")
    print("\nDetailed results written to athletes_same_date_range.json")
    
    # Print some examples
    for i, athlete in enumerate(athlete_conflicts[:5]):  # Show first 5 athletes
        print(f"\nAthlete: {athlete['athlete_name']}")
        print(f"Number of conflicts: {len(athlete['conflicts'])}")
        for j, conflict in enumerate(athlete['conflicts'][:3]):  # Show first 3 conflicts per athlete
            print(f"  Conflict {j+1}:")
            print(f"    {conflict['competition1']['name']} ({conflict['competition1']['date']}) - {conflict['competition1']['division']} {conflict['competition1']['subtype']} - Place {conflict['competition1']['place']}")
            print(f"    {conflict['competition2']['name']} ({conflict['competition2']['date']}) - {conflict['competition2']['division']} {conflict['competition2']['subtype']} - Place {conflict['competition2']['place']}")
            print(f"    Days difference: {conflict['days_difference']}")
    
    if len(athlete_conflicts) > 5:
        print(f"\n... and {len(athlete_conflicts) - 5} more athletes with conflicts")
    
    return athlete_conflicts

def check_athlete_name_keys():
    """
    Check if each athlete name key in the results data exists in the competitor_names.json mapping file.
    This helps identify unmapped athlete names that need to be added to the mapping.
    """
    # Load the results data
    results_df = pd.read_csv('data/all/results.csv')
    
    # Load the competitor names mapping
    try:
        with open('keys/competitor_names.json', 'r') as f:
            competitor_names = json.load(f)
    except FileNotFoundError:
        print("Error: keys/competitor_names.json not found")
        return
    
    # Get unique athlete name keys from results
    unique_athlete_keys = results_df['athlete_name_key'].unique()
    
    # Check which keys exist in the mapping
    mapped_keys = set(competitor_names.keys())
    unmapped_keys = []
    mapped_count = 0
    
    for athlete_key in unique_athlete_keys:
        if athlete_key in mapped_keys:
            mapped_count += 1
        else:
            unmapped_keys.append(athlete_key)
    
    # Calculate statistics
    total_keys = len(unique_athlete_keys)
    unmapped_count = len(unmapped_keys)
    mapping_percentage = (mapped_count / total_keys) * 100 if total_keys > 0 else 0
    
    # Print results
    print(f"\n=== ATHLETE NAME KEY MAPPING STATUS ===\n")
    print(f"Total unique athlete name keys: {total_keys}")
    print(f"Mapped keys: {mapped_count}")
    print(f"Unmapped keys: {unmapped_count}")
    print(f"Mapping coverage: {mapping_percentage:.2f}%")
    
    if unmapped_keys:
        print(f"\n=== UNMAPPED ATHLETE NAME KEYS ===\n")
        print(f"Found {len(unmapped_keys)} unmapped athlete name keys:")
        
        # Sort unmapped keys for better readability
        unmapped_keys.sort()
        
        # Show first 50 unmapped keys
        for i, key in enumerate(unmapped_keys[:50]):
            print(f"  {i+1:3d}. {key}")
        
        if len(unmapped_keys) > 50:
            print(f"  ... and {len(unmapped_keys) - 50} more unmapped keys")
        
        # Write unmapped keys to JSON file
        unmapped_data = {
            'summary': {
                'total_keys': total_keys,
                'mapped_keys': mapped_count,
                'unmapped_keys': unmapped_count,
                'mapping_percentage': mapping_percentage
            },
            'unmapped_keys': unmapped_keys
        }
        
        with open('unmapped_athlete_keys.json', 'w') as f:
            json.dump(unmapped_data, f, indent=2)
        
        print(f"\nUnmapped keys written to unmapped_athlete_keys.json")
    else:
        print(f"\n✅ All athlete name keys are properly mapped!")
    
    return {
        'total_keys': total_keys,
        'mapped_keys': mapped_count,
        'unmapped_keys': unmapped_count,
        'mapping_percentage': mapping_percentage,
        'unmapped_keys_list': unmapped_keys
    }

def check_competition_name_keys():
    """
    Check if each competition name key in the results data exists in the competition_names.json mapping file.
    This helps identify unmapped competition names that need to be added to the mapping.
    The competition_names.json has a hierarchical structure: region -> country/subregion -> competition_key -> [name_variations]
    """
    # Load the results data
    results_df = pd.read_csv('data/all/results.csv')
    
    # Load the competition names mapping
    try:
        with open('keys/competition_names.json', 'r') as f:
            competition_names = json.load(f)
    except FileNotFoundError:
        print("Error: keys/competition_names.json not found")
        return
    
    # Get unique competition name keys from results
    unique_competition_keys = results_df['competition_name_key'].unique()
    
    # Flatten the hierarchical structure to get all competition keys
    all_mapped_keys = set()
    region_stats = {}
    
    for region, countries in competition_names.items():
        region_stats[region] = {'total_keys': 0, 'mapped_keys': 0}
        
        for country, competitions in countries.items():
            if isinstance(competitions, dict):
                # This is a sub-region with competitions
                for competition_key in competitions.keys():
                    all_mapped_keys.add(competition_key)
                    region_stats[region]['total_keys'] += 1
            else:
                # This might be a direct competition (though unlikely based on structure)
                print(f"Warning: Unexpected structure in {region}.{country}")
    
    # Check which keys exist in the mapping
    unmapped_keys = []
    mapped_count = 0
    
    for competition_key in unique_competition_keys:
        if competition_key in all_mapped_keys:
            mapped_count += 1
            # Track which region this key belongs to
            for region, countries in competition_names.items():
                for country, competitions in countries.items():
                    if isinstance(competitions, dict) and competition_key in competitions:
                        region_stats[region]['mapped_keys'] += 1
                        break
        else:
            unmapped_keys.append(competition_key)
    
    # Calculate statistics
    total_keys = len(unique_competition_keys)
    unmapped_count = len(unmapped_keys)
    mapping_percentage = (mapped_count / total_keys) * 100 if total_keys > 0 else 0
    
    # Print results
    print(f"\n=== COMPETITION NAME KEY MAPPING STATUS ===\n")
    print(f"Total unique competition name keys: {total_keys}")
    print(f"Mapped keys: {mapped_count}")
    print(f"Unmapped keys: {unmapped_count}")
    print(f"Mapping coverage: {mapping_percentage:.2f}%")
    
    # Print regional breakdown
    print(f"\n=== REGIONAL BREAKDOWN ===\n")
    for region, stats in region_stats.items():
        if stats['total_keys'] > 0:
            region_percentage = (stats['mapped_keys'] / stats['total_keys']) * 100 if stats['total_keys'] > 0 else 0
            print(f"{region}: {stats['mapped_keys']}/{stats['total_keys']} ({region_percentage:.2f}%)")
    
    if unmapped_keys:
        print(f"\n=== UNMAPPED COMPETITION NAME KEYS ===\n")
        print(f"Found {len(unmapped_keys)} unmapped competition name keys:")
        
        # Sort unmapped keys for better readability
        unmapped_keys.sort()
        
        # Show first 50 unmapped keys
        for i, key in enumerate(unmapped_keys[:50]):
            print(f"  {i+1:3d}. {key}")
        
        if len(unmapped_keys) > 50:
            print(f"  ... and {len(unmapped_keys) - 50} more unmapped keys")
        
        # Write unmapped keys to JSON file
        unmapped_data = {
            'summary': {
                'total_keys': total_keys,
                'mapped_keys': mapped_count,
                'unmapped_keys': unmapped_count,
                'mapping_percentage': mapping_percentage
            },
            'regional_breakdown': region_stats,
            'unmapped_keys': unmapped_keys
        }
        
        with open('unmapped_competition_keys.json', 'w') as f:
            json.dump(unmapped_data, f, indent=2)
        
        print(f"\nUnmapped keys written to unmapped_competition_keys.json")
    else:
        print(f"\n✅ All competition name keys are properly mapped!")
    
    return {
        'total_keys': total_keys,
        'mapped_keys': mapped_count,
        'unmapped_keys': unmapped_count,
        'mapping_percentage': mapping_percentage,
        'unmapped_keys_list': unmapped_keys,
        'regional_breakdown': region_stats
    }

def check_missing_values():
    """
    Check for missing values in critical columns: year, competition_name_key, athlete_name_key, 
    Place, Division, Division Subtype, and Division Level.
    This helps identify data quality issues that need to be addressed.
    """
    # Load the results data
    df = pd.read_csv('data/all/results.csv')
    
    # Define the columns to check for missing values
    critical_columns = [
        'year',
        'competition_name_key', 
        'athlete_name_key',
        'Place',
        'Division',
        'Division Subtype',
        'Division Level'
    ]
    
    # Check for missing values in each column
    missing_data = {}
    total_rows = len(df)
    
    print(f"\n=== MISSING VALUES ANALYSIS ===\n")
    print(f"Total rows in dataset: {total_rows:,}")
    print("-" * 60)
    
    for column in critical_columns:
        if column in df.columns:
            missing_count = df[column].isnull().sum()
            missing_percentage = (missing_count / total_rows) * 100 if total_rows > 0 else 0
            
            missing_data[column] = {
                'missing_count': int(missing_count),
                'missing_percentage': float(missing_percentage),
                'total_rows': total_rows
            }
            
            print(f"{column:20s}: {missing_count:6,} missing ({missing_percentage:5.2f}%)")
            
            # If there are missing values, show some examples
            if missing_count > 0:
                missing_rows = df[df[column].isnull()]
                print(f"{'':20s}  Examples of rows with missing {column}:")
                
                # Show first 5 examples with relevant context
                for i, (idx, row) in enumerate(missing_rows.head(5).iterrows()):
                    context_cols = [col for col in critical_columns if col != column and col in df.columns]
                    context_values = []
                    for col in context_cols:
                        if pd.notna(row[col]):
                            context_values.append(f"{col}={row[col]}")
                        else:
                            context_values.append(f"{col}=NULL")
                    
                    print(f"{'':20s}    Row {idx}: {', '.join(context_values)}")
                
                if missing_count > 5:
                    print(f"{'':20s}    ... and {missing_count - 5} more rows")
                print()
        else:
            print(f"{column:20s}: Column not found in dataset")
            missing_data[column] = {
                'missing_count': 0,
                'missing_percentage': 0,
                'total_rows': total_rows,
                'error': 'Column not found'
            }
    
    # Check for rows with multiple missing values
    print(f"\n=== ROWS WITH MULTIPLE MISSING VALUES ===\n")
    
    # Count missing values per row
    df['missing_count'] = df[critical_columns].isnull().sum(axis=1)
    
    # Group by missing count
    missing_counts = df['missing_count'].value_counts().sort_index()
    
    for missing_count, row_count in missing_counts.items():
        if missing_count > 0:
            percentage = (row_count / total_rows) * 100
            print(f"Rows with {missing_count} missing values: {row_count:,} ({percentage:.2f}%)")
    
    # Show examples of rows with the most missing values
    max_missing = df['missing_count'].max()
    if max_missing > 0:
        worst_rows = df[df['missing_count'] == max_missing].head(3)
        print(f"\nExamples of rows with {max_missing} missing values:")
        
        for i, (idx, row) in enumerate(worst_rows.iterrows()):
            print(f"  Row {idx}:")
            for col in critical_columns:
                if col in df.columns:
                    value = row[col] if pd.notna(row[col]) else "NULL"
                    print(f"    {col}: {value}")
            print()
    
    # Calculate overall data completeness
    total_cells = total_rows * len([col for col in critical_columns if col in df.columns])
    total_missing = sum(data['missing_count'] for data in missing_data.values() if 'error' not in data)
    overall_completeness = ((total_cells - total_missing) / total_cells) * 100 if total_cells > 0 else 0
    
    print(f"\n=== OVERALL DATA COMPLETENESS ===\n")
    print(f"Total cells in critical columns: {total_cells:,}")
    print(f"Total missing cells: {total_missing:,}")
    print(f"Overall completeness: {overall_completeness:.2f}%")
    
    # Write detailed results to JSON file
    results_data = {
        'summary': {
            'total_rows': total_rows,
            'total_cells': total_cells,
            'total_missing': total_missing,
            'overall_completeness': overall_completeness
        },
        'column_analysis': missing_data,
        'missing_counts_distribution': missing_counts.to_dict()
    }
    
    with open('missing_values_analysis.json', 'w') as f:
        json.dump(results_data, f, indent=2, default=convert_numpy_types)
    
    print(f"\nDetailed analysis written to missing_values_analysis.json")
    
    return results_data

if __name__ == "__main__":
    #check_duplicate_athletes()
    #find_same_place_not_last()
    #find_duplicated_names_in_competitions()
    #find_athletes_same_date_range()
    #check_athlete_name_keys()
    #check_competition_name_keys()
    check_missing_values()
