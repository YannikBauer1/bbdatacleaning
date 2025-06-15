import pandas as pd
import re

# Read the input CSV file
df = pd.read_csv('all/all_years_combined.csv')

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
# Set date for Wings Of Strength Chicago Pro without dates to July 1, 2016
mask = (cleaned_df['Competition'].str.contains('Wings of Strength Chicago Pro', case=False, na=False)) & (cleaned_df['Date'].isna() | (cleaned_df['Date'] == ''))
cleaned_df.loc[mask, 'Date'] = 'July 1, 2016'

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




# Order by start date and Competition
cleaned_df = cleaned_df.sort_values(by=['Start Date', 'Competition'])

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
write_competition_names_json(cleaned_df, 'all/competition_names.json')

# new column order: Competition,Location,Date,Competitor Name,Country,Judging,Finals,Round 2,Round 3,Routine,Total,Place,Competition Type
cleaned_df = cleaned_df[['Start Date', 'End Date', 'Competition', 'Location', 'Competitor Name', 'Country', 'Judging', 'Finals', 'Round 2', 'Round 3', 'Routine', 'Total', 'Place', 'Division', 'Date', 'Year', 'Contest URL', 'Source']]

# Save the cleaned DataFrame to a new CSV file
cleaned_df.to_csv('all/all_clean.csv', index=False)

print('Cleaned data written to all/all_clean.csv')

# Print unique date strings from the 'Date' column
#print(cleaned_df['Date'].unique())
