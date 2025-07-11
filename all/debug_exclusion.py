import pandas as pd
import json

# Load the data
print("Loading results.csv...")
df = pd.read_csv('../data/all/results.csv')

# Load existing conflicts
print("Loading existing conflicts...")
with open('cross_source_conflicts_remain.json', 'r') as f:
    existing_conflicts = json.load(f)

# Create exclude keys
exclude_keys = set()
for conflict in existing_conflicts:
    key = f"{conflict['year']}_{conflict['competition_name_key']}_{conflict['place']}"
    exclude_keys.add(key)

print(f"Total exclude keys: {len(exclude_keys)}")

# Check problematic keys
problematic_keys = ["2008_atlantic_city_pro_mensbb_open_8", "2008_atlantic_city_pro_mensbb_open_9"]
for key in problematic_keys:
    print(f"{key} in exclude_keys: {key in exclude_keys}")

# Look at the actual data for these conflicts
print("\nLooking at actual data for problematic conflicts...")
problematic_data = df[
    (df['year'] == 2008) & 
    (df['competition_name_key'] == 'atlantic_city_pro_mensbb_open') & 
    (df['Place'].isin([8, 9]))
]

print(f"Found {len(problematic_data)} rows for problematic conflicts")

# Check what data exists for 2008 Atlantic City Pro
print("\nChecking all data for 2008 Atlantic City Pro...")
atlantic_2008_data = df[
    (df['year'] == 2008) & 
    (df['competition_name_key'] == 'atlantic_city_pro_mensbb_open')
]

print(f"Found {len(atlantic_2008_data)} total rows for 2008 Atlantic City Pro")
if len(atlantic_2008_data) > 0:
    print("Places found:", sorted(atlantic_2008_data['Place'].unique()))
    print("Sample data:")
    for _, row in atlantic_2008_data.head(10).iterrows():
        print(f"  Year: {row['year']}, Competition: {row['competition_name_key']}, Place: {row['Place']}, Division: {row['Division']}, Subtype: {row['Division Subtype']}")

# Check what conflicts are in the remain file for 2008 Atlantic City Pro
print("\nChecking conflicts in remain file for 2008 Atlantic City Pro...")
atlantic_2008_conflicts = [c for c in existing_conflicts if c['year'] == '2008' and c['competition_name_key'] == 'atlantic_city_pro_mensbb_open']
print(f"Found {len(atlantic_2008_conflicts)} conflicts in remain file")
for conflict in atlantic_2008_conflicts:
    print(f"  Year: {conflict['year']}, Competition: {conflict['competition_name_key']}, Place: {conflict['place']}")

# Create group keys
print("\nCreating group keys...")
df['group_key'] = df['year'].astype(str) + '_' + \
                 df['competition_name_key'].astype(str) + '_' + \
                 df['Division'].astype(str) + '_' + \
                 df['Division Subtype'].astype(str) + '_' + \
                 df['Place'].astype(str)

df['exclude_key'] = df['year'].astype(str) + '_' + \
                   df['competition_name_key'].astype(str) + '_' + \
                   df['Place'].astype(str)

# Now check the problematic data with group keys
problematic_data_with_keys = df[
    (df['year'] == 2008) & 
    (df['competition_name_key'] == 'atlantic_city_pro_mensbb_open') & 
    (df['Place'].isin([8, 9]))
]

print(f"\nFound {len(problematic_data_with_keys)} rows for problematic conflicts (with keys)")

if len(problematic_data_with_keys) > 0:
    print("Sample data with keys:")
    for _, row in problematic_data_with_keys.head(10).iterrows():
        exclude_key = f"{row['year']}_{row['competition_name_key']}_{row['Place']}"
        print(f"  Year: {row['year']}, Competition: {row['competition_name_key']}, Place: {row['Place']}, Division: {row['Division']}, Subtype: {row['Division Subtype']}")
        print(f"  Group key: {row['group_key']}")
        print(f"  Exclude key: {row['exclude_key']}")
        print(f"  In exclude_keys: {row['exclude_key'] in exclude_keys}")
        print()

# Check what groups exist for the problematic data
problematic_groups = problematic_data_with_keys['group_key'].unique()
print(f"\nProblematic groups found: {len(problematic_groups)}")
for group in problematic_groups:
    print(f"  Group: {group}")
    group_data = df[df['group_key'] == group]
    exclude_key = group_data['exclude_key'].iloc[0]
    print(f"  Exclude key: {exclude_key}")
    print(f"  In exclude_keys: {exclude_key in exclude_keys}")
    print(f"  Group size: {len(group_data)}")
    print() 