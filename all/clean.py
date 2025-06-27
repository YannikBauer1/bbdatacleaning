import pandas as pd
import re
import json

# Read the input CSV file
df = pd.read_csv('data/all/all_years_combined.csv')

# TODO: Make changes to the DataFrame here
# Example: cleaned_df = df.copy()
cleaned_df = df.copy()

# Remove prefixes like the year, IFBB, IFBB Pro, IFBB PRO LEAGUE, and also leading "-"
cleaned_df['Competition'] = cleaned_df['Competition'].str.replace(
    r'^(?:\d{4}\s*|-+\s*|IFBB PRO LEAGUE\s*|IFBB PRO\s*|IFBB\s*)+', '', 
    regex=True, 
    case=False
).str.replace('-', ' ').str.replace(r'\s+', ' ', regex=True)
# make all names lowercase with the start of a word capitalized
cleaned_df['Competition'] = cleaned_df['Competition'].str.title()


# Fix incorrect year 2103 to 2013
cleaned_df['Date'] = cleaned_df['Date'].str.replace('November 16, 2103', 'November 16, 2013')

# Fix incorrect date for Mr Olympia 2021
mask = (cleaned_df['Competition'].str.contains('Mr Olympia', case=False, na=False)) & (cleaned_df['Date'].str.contains('December 30, 2021', case=False, na=False))
cleaned_df.loc[mask, 'Date'] = 'October 9, 2021'

# Set date for Wings Of Strength Chicago Pro without dates to July 1, 2016
mask = (cleaned_df['Competition'].str.contains('Wings of Strength Chicago Pro', case=False, na=False)) & (cleaned_df['Date'].isna() | (cleaned_df['Date'] == ''))
cleaned_df.loc[mask, 'Date'] = 'July 1, 2016'

# Fix incorrect date for Torunament Of Champions Pro
mask = (cleaned_df['Competition'].str.contains('Torunament Of Champions Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('September 25, 2019', case=False, na=False))
cleaned_df.loc[mask, 'Date'] = 'September 25, 2021'


def parse_date_range(date_str):
    """
    Parse a date string that may contain a range (e.g., 'September 24th & 25th, 2010')
    and return (start_date, end_date) as pd.Timestamp objects.
    If only one date, both are the same.
    """
    if pd.isna(date_str):
        return (pd.NaT, pd.NaT)
    
    # Strip whitespace and normalize
    date_str = str(date_str).strip()
    #print(f"Processing date: '{date_str}'")
    
    # Updated regex pattern to handle ordinal numbers
    pattern = r'(\w+)\s+(\d+)(?:st|nd|rd|th)?\s*&\s*(\d+)(?:st|nd|rd|th)?,\s*(\d{4})'
    m = re.search(pattern, date_str, flags=re.IGNORECASE)
    if m:
        month, day1, day2, year = m.groups()
        start = f"{month} {day1}, {year}"
        end = f"{month} {day2}, {year}"
        return (pd.to_datetime(start, errors='coerce'), pd.to_datetime(end, errors='coerce'))
    
    # Pattern for "Month day1-day2-day3, year" (three-day range)
    m = re.search(r'([A-Za-z]+) (\d+)-(\d+)-(\d+), (\d{4})', date_str, flags=re.IGNORECASE)
    if m:
        month, day1, day2, day3, year = m.groups()
        start = f"{month} {day1}, {year}"
        end = f"{month} {day3}, {year}"
        return (pd.to_datetime(start, errors='coerce'), pd.to_datetime(end, errors='coerce'))
    
    # Pattern for "Month1 day1-Month2 day2, year" (cross-month range)
    m = re.search(r'([A-Za-z]+) (\d+)\s*-\s*([A-Za-z]+) (\d+), (\d{4})', date_str, flags=re.IGNORECASE)
    if m:
        month1, day1, month2, day2, year = m.groups()
        start = f"{month1} {day1}, {year}"
        end = f"{month2} {day2}, {year}"
        return (pd.to_datetime(start, errors='coerce'), pd.to_datetime(end, errors='coerce'))
    
    # Pattern for "Month day, year"
    m = re.search(r'([A-Za-z]+) (\d+), (\d{4})', date_str, flags=re.IGNORECASE)
    if m:
        month, day, year = m.groups()
        date = f"{month} {day}, {year}"
        return (pd.to_datetime(date, errors='coerce'), pd.to_datetime(date, errors='coerce'))
    
    # Pattern for "Month day1-day2, year"
    m = re.search(r'([A-Za-z]+) (\d+)-(\d+), (\d{4})', date_str, flags=re.IGNORECASE)
    if m:
        month, day1, day2, year = m.groups()
        start = f"{month} {day1}, {year}"
        end = f"{month} {day2}, {year}"
        return (pd.to_datetime(start, errors='coerce'), pd.to_datetime(end, errors='coerce'))
    
    # If not matched, try to parse as is
    try:
        dt = pd.to_datetime(date_str, errors='coerce')
        if pd.isna(dt):
            print(f"Could not parse date: '{date_str}'")
        return (dt, dt)
    except Exception:
        print(f"Could not parse date (exception): '{date_str}'")
        return (pd.NaT, pd.NaT)

# Apply the function to create Start Date and End Date columns
cleaned_df[['Start Date', 'End Date']] = cleaned_df['Date'].apply(
    lambda x: pd.Series(parse_date_range(x))
)

# All years without an entry in year i want to get the year from the Start Date
cleaned_df.loc[(cleaned_df['Year'].isna()) | (cleaned_df['Year'] == ''), 'Year'] = cleaned_df['Start Date'].dt.year



# Fix specific date issues

mask = (cleaned_df['Competition'].str.contains('Rising Phoenix Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('August 24, 2024', case=False, na=False))
#mask = (cleaned_df['Competition'] == 'Rising Phoenix Pro') & (cleaned_df['Date'] == 'August 24, 2024')
cleaned_df.loc[mask, 'Competition'] = 'Arizona Pro'

# Fix incorrect competition "Agp South Korea Pro"
mask = (cleaned_df['Competition'].str.contains('Agp South Korea Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('October 8, 2023', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Agp South Korea Mens Physique Pro'

# Fix incorrect competition "Dennis James Classic Pro"
mask = (cleaned_df['Competition'].str.contains('Dennis James Classic Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('October 26, 2024', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Dennis James Classic Germany'

# Fix incorrect competition "Empro Pro Show"
mask = (cleaned_df['Competition'].str.contains('Empro Pro Show', case=False, na=False)) & (cleaned_df['Date'].str.contains('17 September 2023', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Europa Pro'

# Fix incorrect competition "Expo Sport Izmir Turkey Pro"
mask = (cleaned_df['Competition'].str.contains('9', case=False, na=False)) & (cleaned_df['Date'].str.contains('2024-09-19', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Expo Sport Izmir Turkey Pro'

# Fix incorrect competition "Korea Pro"
mask = (cleaned_df['Competition'].str.contains('Korea Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('November 11, 2023', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'World Of Monsterzym 8 Korea Pro'

# Fix incorrect competition "South Korea Pro"
mask = (cleaned_df['Competition'].str.contains('South Korea Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('June 17, 2023', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Asia Grand Prix Mens Physique Pro'

# Fix incorrect competition "Arnold Classic Pro"
mask = (cleaned_df['Competition'].str.contains('Arnold Classic Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('April 27, 2013', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Arnold Classic Brasil Pro'

# Fix incorrect competition "Colombia Pro"
mask = (cleaned_df['Competition'].str.contains('Colombia Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('November 10, 2024', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Battle Of Bogota Pro'

# Fix incorrect competition "Colombia Pro"
mask = (cleaned_df['Competition'].str.contains('Colombia Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('2024-11-08', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Battle Of Bogota Pro'

# Fix incorrect competition "Battle Of Champions"
mask = (cleaned_df['Competition'].str.contains('Battle Of Champions', case=False, na=False)) & (cleaned_df['Date'].str.contains('August 29, 2021', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Battle Of Champions Pro'

# Fix incorrect competition "Flex Pro (Santa Monica)"
mask = (cleaned_df['Competition'].str.contains('Flex Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('February 18, 2012', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Flex Pro (Santa Monica)'

# Fix incorrect competition "Flex Pro (Santa Monica)"
mask = (cleaned_df['Competition'].str.contains('Flex Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('February 19, 2011', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Flex Pro (Santa Monica)'

# Fix incorrect competition "Florida Pro"
mask = (cleaned_df['Competition'].str.contains('Florida Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('December 10, 2011', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Florida Pro World'

# Fix incorrect competition "Grand Prix Hungary"
mask = (cleaned_df['Competition'].str.contains('Grand Prix Hungary', case=False, na=False)) & (cleaned_df['Date'].str.contains('2019-01-01', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Fitparade Ifbb Pro Grand Prix Hungary'

# Fix incorrect competition "Musclecontest Brazil"
mask = (cleaned_df['Competition'].str.contains('Musclecontest Brazil', case=False, na=False)) & (cleaned_df['Date'].str.contains('Nov 25, 2023', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Musclecontest Brazil Masters'

# Fix incorrect competition "Musclecontest Brazil"
mask = (cleaned_df['Competition'].str.contains('New York Pro', case=False, na=False)) & (cleaned_df['Division'].str.contains('FITNESS', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'New York Pro Fitness'

# Fix incorrect competition "Pittsburgh"
mask = (cleaned_df['Competition'].str.contains('Pittsburgh', case=False, na=False)) & (cleaned_df['Division'].str.contains('\\+', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Pittsburgh Masters Pro'

# Fix incorrect competition "Sheru Classic"
mask = (cleaned_df['Competition'].str.contains('Sheru Classic India Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('November 17-19, 2023', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Sheru Classic Mumbai Pro'

# Fix incorrect competition "St. Louis Pro"
mask = (cleaned_df['Competition'].str.contains('St. Louis Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('September 15, 2012', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'St. Louis Pro Bikini'

# Fix incorrect competition "St. Louis Pro"
mask = (cleaned_df['Competition'].str.contains('St. Louis Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('August 24, 2013', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'St. Louis Pro Bikini'

# Fix incorrect competition "St. Louis Pro"
mask = (cleaned_df['Competition'].str.contains('St. Louis Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('August 23, 2014', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'St. Louis Pro Bikini'

# Fix incorrect division "Tahoe Show"
mask = (cleaned_df['Competition'].str.contains('Tahoe Show', case=False, na=False)) & (cleaned_df['Date'].str.contains('August 24, 2013', case=False, na=False))
cleaned_df.loc[mask, 'Division'] = 'Figure'

# Fix incorrect competition "Taiwan Pro"
mask = (cleaned_df['Competition'].str.contains('Taiwan Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('April 4, 2024', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Taiwan Pro Bikini'

# Fix incorrect competition "Taiwan Pro"
mask = (cleaned_df['Competition'].str.contains('Tw Pro', case=False, na=False)) & (cleaned_df['Date'].str.contains('2024-04-04', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Taiwan Pro Bikini'

# Fix incorrect division "Tournament Of Champions"
mask = (cleaned_df['Competition'].str.contains('Tournament Of Champions', case=False, na=False)) & (cleaned_df['Date'].str.contains('December 4, 2018', case=False, na=False))
cleaned_df.loc[mask, 'Division'] = 'Mens Physique'

# Fix incorrect competition "Rising Phoenix World Championship"
mask = (cleaned_df['Competition'].str.contains('Rising Phoenix World Championship', case=False, na=False)) & (cleaned_df['Date'].str.contains('August 22, 2015', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Wings Of Strength Texas Pro'

# Fix incorrect competition "Baltimore Pro"
mask = (cleaned_df['Competition'].str.contains('Baltimore Pro', case=False, na=False)) & (cleaned_df['Division'].str.contains('Masters', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Baltimore Classic Masters Pro'

# Fix incorrect competition "Baltimore Pro"
mask = (cleaned_df['Competition'].str.contains('Baltimore Pro', case=False, na=False)) & (cleaned_df['Division'].str.contains('\\+', case=False, na=False))
cleaned_df.loc[mask, 'Competition'] = 'Baltimore Classic Masters Pro'



def write_competition_names_json(df, output_path):
    """
    Takes a DataFrame with a 'Competition' column, sorts unique competition names,
    and writes them to a JSON file where each name is a key and the value is a list
    containing only that name (as the initial subnames array).
    """
    import json

    # Get unique competition names, sort them
    competition_names = sorted(df['Competition'].dropna().unique())
    # Build the dictionary
    competitions_dict = {name: [name] for name in competition_names}
    # Write to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(competitions_dict, f, ensure_ascii=False, indent=2)

# Example usage:
#write_competition_names_json(cleaned_df, 'all/competition_names.json')

# new column order: Competition,Location,Date,Competitor Name,Country,Judging,Finals,Round 2,Round 3,Routine,Total,Place,Competition Type
cleaned_df = cleaned_df[['Start Date', 'End Date', 'Competition', 'Location', 'Competitor Name', 'Country', 'Judging', 'Finals', 'Round 2', 'Round 3', 'Routine', 'Total', 'Place', 'Division', 'Date', 'Year', 'Contest URL', 'Source']]



def apply_competition_mapping(cleaned_df):
    """
    Apply competition name mapping from JSON file and return the cleaned DataFrame.
    """
    # Load competition names mapping from JSON
    with open('keys/competition_names.json', 'r', encoding='utf-8') as f:
        competition_mapping = json.load(f)

    def create_competition_lookup(mapping_dict):
        """
        Create a flat lookup dictionary for faster competition name mapping.
        """
        lookup = {}
        for region, sub_regions in mapping_dict.items():
            if isinstance(sub_regions, dict):
                for sub_region, competitions in sub_regions.items():
                    if isinstance(competitions, dict):
                        for standard_name, variations in competitions.items():
                            if isinstance(variations, list):
                                for variation in variations:
                                    lookup[variation.lower()] = standard_name
        return lookup

    # Create lookup dictionary for faster mapping
    competition_lookup = create_competition_lookup(competition_mapping)

    def find_competition_mapping(competition_name, lookup_dict):
        """
        Fast lookup for competition name mapping using pre-built dictionary.
        """
        return lookup_dict.get(competition_name.lower(), competition_name)

    # Apply the competition name mapping
    original_competitions = cleaned_df['Competition'].copy()
    cleaned_df['Competition'] = cleaned_df['Competition'].apply(
        lambda x: find_competition_mapping(x, competition_lookup)
    )

    # Filter out competitions that don't have a mapping (keep only mapped competitions)
    original_count = len(cleaned_df)
    
    # Get competitions that were filtered out (not found in mapping file)
    # A competition is filtered out if it's not in the lookup dictionary
    filtered_out_competitions = []
    for comp in original_competitions.unique():
        if comp.lower() not in competition_lookup:
            filtered_out_competitions.append(comp)
    
    # Remove duplicates and sort alphabetically
    filtered_out_competitions = sorted(list(set(filtered_out_competitions)))
    
    # Save filtered out competitions to JSON file
    with open('all/filtered_out_competitions.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_out_competitions, f, ensure_ascii=False, indent=2)
    
    # Keep only rows where the competition name was found in the mapping (even if it maps to itself)
    cleaned_df = cleaned_df[cleaned_df['Competition'].apply(lambda x: x.lower() in competition_lookup)]
    print(f"Filtered out {original_count - len(cleaned_df)} competitions that don't have mappings in competition_names.json")
    print(f"Kept {len(cleaned_df)} competitions with valid mappings")
    print(f"Filtered out competitions saved to: all/filtered_out_competitions.json")

    # Count how many competitions were mapped
    mapped_count = len(cleaned_df)  # All remaining competitions were mapped
    print(f"Competition name mapping: {mapped_count} competitions were standardized and kept")

    # Show some examples of mappings
    if mapped_count > 0:
        mapping_examples = pd.DataFrame({
            'Original': original_competitions,
            'Standardized': cleaned_df['Competition']
        })
        mapping_examples = mapping_examples[mapping_examples['Original'] != mapping_examples['Standardized']].drop_duplicates().head(15)
        print("\nExamples of competition name mappings:")
        for _, row in mapping_examples.iterrows():
            print(f"  '{row['Original']}' -> '{row['Standardized']}'")
        
        # Show unique competitions that were mapped
        unique_mappings = mapping_examples.drop_duplicates(subset=['Original', 'Standardized'])
        print(f"\nUnique competition name mappings: {len(unique_mappings)}")
        if len(unique_mappings) > 0:
            print("First 10 unique mappings:")
            for _, row in unique_mappings.head(10).iterrows():
                print(f"  '{row['Original']}' -> '{row['Standardized']}'")
    
    return cleaned_df

# Apply the competition mapping function
cleaned_df = apply_competition_mapping(cleaned_df)

# make all division names lowercase
cleaned_df['Division'] = cleaned_df['Division'].str.lower()

# get rid of all rows where masters is in the division
cleaned_df = cleaned_df[~cleaned_df['Division'].str.contains('master', case=False, na=False)]
cleaned_df = cleaned_df[~cleaned_df['Division'].str.contains('\\+', case=False, na=False)]
cleaned_df = cleaned_df[~cleaned_df['Division'].str.contains('junior', case=False, na=False)]
cleaned_df = cleaned_df[~cleaned_df['Division'].str.contains('teen', case=False, na=False)]
cleaned_df = cleaned_df[~cleaned_df['Division'].str.contains('amateur', case=False, na=False)]
cleaned_df = cleaned_df[~cleaned_df['Division'].str.contains('male - most symmetrical', case=False, na=False)]
cleaned_df = cleaned_df[~cleaned_df['Division'].str.contains('male - most muscular', case=False, na=False)]

# get rid of the rows with compeititon "Mr Japan" in the years 1976 and 1977 which are not division "male - professional"
mask = (cleaned_df['Competition'] == 'Mr Japan') & (cleaned_df['Year'].astype(float) == 1976.0) & (cleaned_df['Division'] != 'male - professional')
cleaned_df = cleaned_df[~mask]
mask = (cleaned_df['Competition'] == 'Mr Japan') & (cleaned_df['Year'].astype(float) == 1977.0) & (cleaned_df['Division'] != 'male - professional')
cleaned_df = cleaned_df[~mask]




# Fix dates for competitions incorrectly set to January 1st
def fix_january_first_dates(df):
    """
    Find competitions with the same name in each year and fix dates for entries 
    incorrectly set to January 1st by copying dates from other entries with the same name.
    """
    print("\nFixing dates for competitions incorrectly set to January 1st...")
    
    # Group by year and competition name
    fixed_count = 0
    
    for year in df['Year'].dropna().unique():
        year_data = df[df['Year'] == year]
        
        # Group by competition name within the year
        for competition_name in year_data['Competition'].unique():
            competition_entries = year_data[year_data['Competition'] == competition_name]
            
            if len(competition_entries) > 1:
                # Check if any entry has January 1st date
                jan_first_mask = (
                    (competition_entries['Start Date'].dt.month == 1) & 
                    (competition_entries['Start Date'].dt.day == 1)
                )
                
                if jan_first_mask.any():
                    # Get the correct dates from other entries (not January 1st)
                    correct_entries = competition_entries[~jan_first_mask]
                    
                    if len(correct_entries) > 0:
                        # Use the first correct entry's dates
                        correct_start_date = correct_entries.iloc[0]['Start Date']
                        correct_end_date = correct_entries.iloc[0]['End Date']
                        
                        # Update the January 1st entries
                        jan_first_indices = competition_entries[jan_first_mask].index
                        
                        for idx in jan_first_indices:
                            df.loc[idx, 'Start Date'] = correct_start_date
                            df.loc[idx, 'End Date'] = correct_end_date
                            fixed_count += 1
                            
                            #print(f"Fixed date for '{competition_name}' in {year}: "
                            #      f"January 1st -> {correct_start_date.strftime('%Y-%m-%d')}")
    
    print(f"Fixed dates for {fixed_count} entries")
    return df

# Apply the date fixing function
cleaned_df = fix_january_first_dates(cleaned_df)


# Try a simpler pattern without word boundaries
mask_before_simple = (cleaned_df['Division'] == 'male - lightweight') & (pd.to_datetime(cleaned_df['Start Date'], errors='coerce') < pd.to_datetime('September 1, 2011')) & (pd.to_datetime(cleaned_df['Start Date'], errors='coerce') > pd.to_datetime('September 1, 2006'))
mask_after_simple = (cleaned_df['Division'] == 'male - lightweight') & (pd.to_datetime(cleaned_df['Start Date'], errors='coerce') >= pd.to_datetime('September 1, 2011'))

cleaned_df.loc[mask_before_simple, 'Division'] = '202'
cleaned_df.loc[mask_after_simple, 'Division'] = '212'

# Fix incorrect division "Olympia"
mask_after_simple = (cleaned_df['Division'] == 'olympia')
cleaned_df.loc[mask_after_simple, 'Division'] = 'fitness'

# Order by start date and Competition
cleaned_df = cleaned_df.sort_values(by=['Start Date', 'Competition'])

# remove all rows without a Competitior Name or if it is an empty string
cleaned_df = cleaned_df[~cleaned_df['Competitor Name'].isna()]
cleaned_df = cleaned_df[cleaned_df['Competitor Name'] != '']
cleaned_df = cleaned_df[cleaned_df['Competitor Name'] != ' ']

# Save the cleaned DataFrame to a new CSV file
cleaned_df.to_csv('data/all/all_clean.csv', index=False, quoting=1)

print('Cleaned data written to data/all/all_clean.csv')

# Print unique date strings from the 'Date' column
#print(cleaned_df['Date'].unique())
