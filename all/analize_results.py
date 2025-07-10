import pandas as pd
import numpy as np
import json

def check_duplicate_athletes():
    """
    Check for rows with the same year, competition, division, subdivision, and place
    but different athlete names AND different sources (cross-source conflicts).
    """
    print("Loading results.csv...")
    df = pd.read_csv('../data/all/results.csv')
    
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Create a key for grouping based on the specified columns (excluding source)
    # Note: 'Division Subtype' might be the subdivision column
    df['group_key'] = df['year'].astype(str) + '_' + \
                     df['competition_name_key'].astype(str) + '_' + \
                     df['Division'].astype(str) + '_' + \
                     df['Division Subtype'].astype(str) + '_' + \
                     df['Place'].astype(str)
    
    # Group by this key and check for multiple athlete names
    duplicates = []
    json_output = []
    
    print("Checking for duplicates...")
    for group_key, group in df.groupby('group_key'):
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
    
    print(f"\nFound {len(duplicates)} groups with duplicate athletes:")
    print("=" * 80)
    
    for i, dup in enumerate(duplicates, 1):
        print(f"\n{i}. Group: {dup['group_key']}")
        print(f"   Athletes: {dup['athletes']}")
        print(f"   Sources: {dup['sources']}")
        print(f"   Count: {dup['count']} different athletes across {len(dup['sources'])} sources")
        
        # Show the actual rows
        print("   Rows:")
        for row in dup['rows']:
            print(f"     - {row['athlete_name_key']} (Place: {row['Place']}, Year: {row['year']}, Competition: {row['competition_name_key']}, Source: {row['Source']})")
    
    # Summary statistics
    if duplicates:
        total_duplicate_rows = sum(len(dup['rows']) for dup in duplicates)
        print(f"\n" + "=" * 80)
        print(f"SUMMARY:")
        print(f"Total groups with duplicates: {len(duplicates)}")
        print(f"Total rows involved in duplicates: {total_duplicate_rows}")
        print(f"Percentage of total data: {(total_duplicate_rows/len(df)*100):.2f}%")
    else:
        print("\nNo duplicates found!")
    
    # Write JSON output to file
    with open('cross_source_conflicts.json', 'w') as f:
        json.dump(json_output, f, indent=2)
    
    print(f"\nJSON output written to cross_source_conflicts.json")
    print(f"Total conflicts written: {len(json_output)}")
    
    return duplicates

if __name__ == "__main__":
    check_duplicate_athletes()
