import pandas as pd

# Read the input CSV file
print("Loading data...")
df = pd.read_csv('data/all/all_years_combined.csv')

print(f"DataFrame shape: {df.shape}")

# Check specific cases that showed 0 rows
print("\n=== Checking specific place correction cases ===")

# Case 1: Flake, Michelle in Sacramento Pro
print("\n1. Checking Flake, Michelle in Sacramento Pro:")
sacramento_flake = df[
    (df['Competition'].str.contains('Sacramento Pro', case=False, na=False)) & 
    (df['Competitor Name'].str.contains('Flake, Michelle', case=False, na=False))
]
print(f"Found {len(sacramento_flake)} rows for Flake, Michelle in Sacramento Pro")
if len(sacramento_flake) > 0:
    for idx, row in sacramento_flake.iterrows():
        print(f"  Date: {row['Date']}, Place: {row['Place']}, Division: {row['Division']}")

# Case 2: Brezovac, Brigita in Europa Battle of Champions
print("\n2. Checking Brezovac, Brigita in Europa Battle of Champions:")
brezovac_europa = df[
    (df['Competition'].str.contains('Europa Battle of Champions', case=False, na=False)) & 
    (df['Competitor Name'].str.contains('Brezovac, Brigita', case=False, na=False))
]
print(f"Found {len(brezovac_europa)} rows for Brezovac, Brigita in Europa Battle of Champions")
if len(brezovac_europa) > 0:
    for idx, row in brezovac_europa.iterrows():
        print(f"  Date: {row['Date']}, Place: {row['Place']}, Division: {row['Division']}")

# Case 3: Yaxeni Oriquen Garcia in Arnold Classic
print("\n3. Checking Yaxeni Oriquen Garcia in Arnold Classic:")
yaxeni_arnold = df[
    (df['Competition'].str.contains('Arnold Classic', case=False, na=False)) & 
    (df['Competitor Name'].str.contains('Yaxeni Oriquen Garcia', case=False, na=False)) &
    (df['Date'].str.contains('March 4, 2011', case=False, na=False))
]
print(f"Found {len(yaxeni_arnold)} rows for Yaxeni Oriquen Garcia in Arnold Classic on March 4, 2011")
if len(yaxeni_arnold) > 0:
    for idx, row in yaxeni_arnold.iterrows():
        print(f"  Date: {row['Date']}, Place: {row['Place']}, Division: {row['Division']}")

# Case 4: Check all Arnold Classic entries for Yaxeni Oriquen Garcia
print("\n4. Checking all Arnold Classic entries for Yaxeni Oriquen Garcia:")
yaxeni_all_arnold = df[
    (df['Competition'].str.contains('Arnold Classic', case=False, na=False)) & 
    (df['Competitor Name'].str.contains('Yaxeni Oriquen Garcia', case=False, na=False))
]
print(f"Found {len(yaxeni_all_arnold)} total rows for Yaxeni Oriquen Garcia in Arnold Classic")
if len(yaxeni_all_arnold) > 0:
    for idx, row in yaxeni_all_arnold.iterrows():
        print(f"  Date: {row['Date']}, Place: {row['Place']}, Division: {row['Division']}")

# Case 5: Check if the place corrections are already correct
print("\n5. Checking if place corrections are already correct:")
print("Checking Rosada Plummer in Pittsburgh PRO (this one showed 1 row found):")
rosada_pittsburgh = df[
    (df['Competition'].str.contains('Pittsburgh PRO', case=False, na=False)) & 
    (df['Competitor Name'].str.contains('Rosada Plummer', case=False, na=False)) &
    (df['Date'].str.contains('May 6, 2022', case=False, na=False))
]
print(f"Found {len(rosada_pittsburgh)} rows for Rosada Plummer in Pittsburgh PRO on May 6, 2022")
if len(rosada_pittsburgh) > 0:
    for idx, row in rosada_pittsburgh.iterrows():
        print(f"  Place: {row['Place']} (should be changed from 166 to 16)")

# Case 6: Check some recent competitions that might have different data
print("\n6. Checking recent competitions:")
recent_competitions = [
    ('2024-lenda-murray-atlanta-pro-supershow', 'Ashley Hampton'),
    ('2024-chicago-pro', 'Will Vaughn'),
    ('2024-phoenix-pro', 'King Stevenson'),
]

for competition, competitor in recent_competitions:
    recent_data = df[
        (df['Competition'].str.contains(competition, case=False, na=False)) & 
        (df['Competitor Name'].str.contains(competitor, case=False, na=False))
    ]
    print(f"\n{competitor} in {competition}: {len(recent_data)} rows found")
    if len(recent_data) > 0:
        for idx, row in recent_data.iterrows():
            print(f"  Date: {row['Date']}, Place: {row['Place']}, Division: {row['Division']}")

print("\n=== Analysis complete ===") 