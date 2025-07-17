import pandas as pd
import json
from collections import Counter

def analyze_schedule2025():
    """
    Analyze schedule2025.csv to check if all competition keys exist in competitions.json
    and identify duplicates.
    """
    
    # Read the CSV file
    try:
        df = pd.read_csv('data/clean/schedule2025.csv')
        print(f"Successfully loaded schedule2025.csv with {len(df)} rows")
    except FileNotFoundError:
        print("Error: schedule2025.csv not found in data/clean/")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Read the competitions.json file
    try:
        with open('keys/competitions.json', 'r') as f:
            competitions_data = json.load(f)
        print("Successfully loaded competitions.json")
    except FileNotFoundError:
        print("Error: competitions.json not found in keys/")
        return
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return
    
    # Extract all competition keys from the JSON file
    json_keys = set()
    for region, countries in competitions_data.items():
        if isinstance(countries, dict):
            for country, competitions in countries.items():
                if isinstance(competitions, dict):
                    json_keys.update(competitions.keys())
                else:
                    # Handle case where country directly contains competitions
                    json_keys.update(competitions.keys() if isinstance(competitions, dict) else [])
        else:
            # Handle case where region directly contains competitions
            json_keys.update(countries.keys() if isinstance(countries, dict) else [])
    
    print(f"Found {len(json_keys)} unique competition keys in competitions.json")
    
    # Get competition keys from CSV
    csv_keys = df['competition_key'].tolist()
    unique_csv_keys = set(csv_keys)
    
    print(f"Found {len(unique_csv_keys)} unique competition keys in schedule2025.csv")
    print(f"Total competition entries in CSV: {len(csv_keys)}")
    
    # Check for duplicates in CSV
    duplicate_counts = Counter(csv_keys)
    duplicates = {key: count for key, count in duplicate_counts.items() if count > 1}
    
    if duplicates:
        print(f"\n⚠️  Found {len(duplicates)} duplicate competition keys in CSV:")
        for key, count in duplicates.items():
            print(f"  - {key}: appears {count} times")
    else:
        print("\n✅ No duplicate competition keys found in CSV")
    
    # Check which CSV keys are missing from JSON
    missing_keys = unique_csv_keys - json_keys
    
    if missing_keys:
        print(f"\n❌ Found {len(missing_keys)} competition keys in CSV that are missing from JSON:")
        for key in sorted(missing_keys):
            print(f"  - {key}")
    else:
        print("\n✅ All competition keys from CSV are present in JSON")
    
    # Check which JSON keys are not used in CSV
    unused_keys = json_keys - unique_csv_keys
    
    if unused_keys:
        print(f"\nℹ️  Found {len(unused_keys)} competition keys in JSON that are not used in CSV:")
        for key in sorted(unused_keys):
            print(f"  - {key}")
    else:
        print("\n✅ All JSON competition keys are used in CSV")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"  - CSV entries: {len(csv_keys)}")
    print(f"  - Unique CSV keys: {len(unique_csv_keys)}")
    print(f"  - JSON keys: {len(json_keys)}")
    print(f"  - Missing from JSON: {len(missing_keys)}")
    print(f"  - Unused in CSV: {len(unused_keys)}")
    print(f"  - Duplicates in CSV: {len(duplicates)}")
    
    return {
        'csv_entries': len(csv_keys),
        'unique_csv_keys': len(unique_csv_keys),
        'json_keys': len(json_keys),
        'missing_keys': list(missing_keys),
        'unused_keys': list(unused_keys),
        'duplicates': duplicates
    }

if __name__ == "__main__":
    analyze_schedule2025()
