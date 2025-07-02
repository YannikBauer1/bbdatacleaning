import pandas as pd
import re
import json

# Read the input CSV file
df = pd.read_csv('data/all/all_years_combined.csv')

# TODO: Make changes to the DataFrame here
# Example: cleaned_df = df.copy()
cleaned_df = df.copy()

# remove all rows without a Competitior Name or if it is an empty string
cleaned_df = cleaned_df[~cleaned_df['Competitor Name'].isna()]
cleaned_df = cleaned_df[cleaned_df['Competitor Name'] != '']
cleaned_df = cleaned_df[cleaned_df['Competitor Name'] != ' ']

# Remove prefixes like the year, IFBB, IFBB Pro, IFBB PRO LEAGUE, and also leading "-"
cleaned_df['Competition'] = cleaned_df['Competition'].str.replace(
    r'^(?:\d{4}\s*|-+\s*|IFBB PRO LEAGUE\s*|IFBB PRO\s*|IFBB\s*)+', '', 
    regex=True, 
    case=False
).str.replace('-', ' ').str.replace(r'\s+', ' ', regex=True)
# make all names lowercase with the start of a word capitalized
cleaned_df['Competition'] = cleaned_df['Competition'].str.title()
cleaned_df['Competitor Name'] = cleaned_df['Competitor Name'].str.title()

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


def parse_location(location_str):
    """
    Parse location string into city, state, and country.
    Always output city, state, and country in title case.
    Convert state abbreviations to full names.
    Generalize malformed US location fix.
    """
    if pd.isna(location_str) or location_str == '' or location_str == ' ':
        return {'city': None, 'state': None, 'country': None}
    
    location_str = str(location_str).strip()
    location_str = location_str.replace('"', '').replace("'", "")
    location_str = re.sub(r'^,+|,+$', '', location_str).strip()

    # Special case handling for common typos and formatting issues
    special_cases = {
        # ... existing special cases ...
    }
    if location_str in special_cases:
        location_str = special_cases[location_str]

    # Capitalization fix for city part
    def fix_city_capitalization(text):
        if not text:
            return text
        parts = text.split(',')
        if len(parts) > 0:
            city_part = parts[0].strip()
            import re
            word_parts = re.split(r'([\s\-\'])', city_part)
            fixed_parts = []
            for part in word_parts:
                if part.strip() and part not in [' ', '-', "'"]:
                    word = part.strip()
                    if word.upper() in ['LA', 'NY', 'DC', 'BC', 'ON', 'QC', 'AB', 'SK', 'MB', 'NB', 'NS', 'PE', 'NL', 'YT', 'NT', 'NU', 'ST', 'MT', 'FT']:
                        fixed_parts.append(word.upper())
                    else:
                        if len(word) > 2:
                            if (word[0].isupper() and word[1].isupper() and any(c.islower() for c in word[2:])):
                                fixed_word = word[0].upper() + word[1:].lower()
                            else:
                                fixed_word = word.capitalize()
                        else:
                            fixed_word = word.capitalize()
                        fixed_parts.append(fixed_word)
                else:
                    fixed_parts.append(part)
            fixed_city = ''.join(fixed_parts)
            parts[0] = fixed_city
            return ','.join(parts)
        return text
    location_str = fix_city_capitalization(location_str)

    # Handle "City, State - USA" pattern before comma splitting
    # This handles cases like "Canton, Georgia - Usa" -> "Canton, Georgia, United States"
    location_str = re.sub(
        r'([A-Za-z .\'-]+),\s*([A-Za-z .\'-]+)\s*-\s*Usa',
        r'\1, \2, United States',
        location_str,
        flags=re.IGNORECASE
    )
    
    # Handle "City, StateAbbrUnited States" pattern (e.g., "Albuquerque, Nmunited States", "Alexandria, Vaunited States")
    location_str = re.sub(
        r'^([^,]+),\s*([A-Za-z]{2})united\s*states$',
        r'\1, \2, United States',
        location_str,
        flags=re.IGNORECASE
    )
    
    # Handle "City, Province Canada" pattern (e.g., "Cumberland, Bc Canada", "Guelph, Ontario Canada")
    location_str = re.sub(
        r'^([^,]+),\s*([A-Za-z\s]+)\s+canada$',
        r'\1, \2, Canada',
        location_str,
        flags=re.IGNORECASE
    )

    # US state/province mappings
    us_states = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
        'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
        'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
        'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire',
        'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina',
        'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania',
        'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee',
        'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington',
        'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
    }
    us_states_lower = {v.lower(): v for v in us_states.values()}
    us_states_abbr = {k.lower(): v for k, v in us_states.items()}

    ca_provinces = {
        'AB': 'Alberta', 'BC': 'British Columbia', 'MB': 'Manitoba', 'NB': 'New Brunswick',
        'NL': 'Newfoundland and Labrador', 'NS': 'Nova Scotia', 'NT': 'Northwest Territories',
        'NU': 'Nunavut', 'ON': 'Ontario', 'PE': 'Prince Edward Island', 'QC': 'Quebec',
        'SK': 'Saskatchewan', 'YT': 'Yukon'
    }
    ca_provinces_lower = {v.lower(): v for v in ca_provinces.values()}
    ca_provinces_abbr = {k.lower(): v for k, v in ca_provinces.items()}

    def normalize_state(state):
        if not state:
            return None
        s = state.strip().lower()
        if s in us_states_abbr:
            return us_states_abbr[s]
        if s in us_states_lower:
            return us_states_lower[s]
        if s in ca_provinces_abbr:
            return ca_provinces_abbr[s]
        if s in ca_provinces_lower:
            return ca_provinces_lower[s]
        return state.title()

    def normalize_country(country_str):
        if not country_str:
            return None
        c = country_str.strip().lower().replace('.', '')
        if c in ['usa', 'united states', 'united states of america', 'us', 'u s a', 'u s']:
            return 'United States'
        if c in ['uk', 'united kingdom', 'england', 'scotland', 'wales', 'northern ireland', 'u k']:
            return 'United Kingdom'
        if c in ['uae', 'united arab emirates']:
            return 'United Arab Emirates'
        if c in ['tunesia', 'tunisia']:
            return 'Tunisia'
        if c in ['ukrain', 'ukraine']:
            return 'Ukraine'
        if c in ['trinidad', 'trinidad & tobago', 'trinidad and tobago', 'trinidad-tobago', 'trinidad/tobago']:
            return 'Trinidad and Tobago'
        if c in ['netherland', 'netherlands', 'the netherland', 'the netherlands', 'holland']:
            return 'Netherlands'
        if c in ['taiwan', 'taiwan r o c', 'taiwan roc', 'r o c', 'r o c']:
            return 'Taiwan'
        if c in ['svecia', 'sweden']:
            return 'Sweden'
        if c in ['slovak republic', 'slovakia']:
            return 'Slovakia'
        if c in ['serbia', 'serbia & montenegro']:
            return 'Serbia'
        if c in ['romain', 'romania']:
            return 'Romania'
        if c in ['russia', 'russian', 'russian federation']:
            return 'Russia'
        if c in ['phillipines', 'philippines']:
            return 'Philippines'
        if c in ['brasil', 'brazil']:
            return 'Brazil'
        if c in ['czech rep', 'czech republic', 'czechia']:
            return 'Czech Republic'
        if c in ['paraquay', 'paraguay']:
            return 'Paraguay'
        if c in ['vanezuela', 'venezuela']:
            return 'Venezuela'
        if c in ['columbia', 'colombia']:
            return 'Colombia'
        if c in ['new zeland', 'new zealand']:
            return 'New Zealand'
        if c in ['morrocco', 'morocco']:
            return 'Morocco'
        return country_str.title()

    # Split by comma and clean up each part
    parts = [part.strip() for part in location_str.split(',') if part.strip()]
    if not parts:
        return {'city': None, 'state': None, 'country': None}

    # Generalized malformed US location fix
    if len(parts) == 3:
        first, second, third = parts
        # City, State, USA/United States
        if (
            (second.upper() in us_states or second.lower() in us_states_lower)
            and normalize_country(third) == 'United States'
        ):
            return {
                'city': fix_city_capitalization(first).title(),
                'state': normalize_state(second),
                'country': 'United States'
            }
        # City, Province, Canada
        if (
            (second.upper() in ca_provinces or second.lower() in ca_provinces_lower)
            and normalize_country(third) == 'Canada'
        ):
            return {
                'city': fix_city_capitalization(first).title(),
                'state': normalize_state(second),
                'country': 'Canada'
            }
        # If first part is a US state abbr, second is US, third is a state (abbr, full, or typo)
        if first.upper() in us_states and second.lower() in ['united states', 'usa']:
            norm_state = normalize_state(third)
            return {'city': None, 'state': norm_state, 'country': 'United States'}
        # If first part is a city, second is a state abbr/full, third is a country
        if second.upper() in us_states:
            return {'city': fix_city_capitalization(first).title(), 'state': normalize_state(second), 'country': normalize_country(third)}
        if second.lower() in us_states_lower:
            return {'city': fix_city_capitalization(first).title(), 'state': normalize_state(second), 'country': normalize_country(third)}
        # If second is a Canadian province
        if second.upper() in ca_provinces:
            return {'city': fix_city_capitalization(first).title(), 'state': normalize_state(second), 'country': normalize_country(third)}
        if second.lower() in ca_provinces_lower:
            return {'city': fix_city_capitalization(first).title(), 'state': normalize_state(second), 'country': normalize_country(third)}

    if len(parts) == 2:
        first, second = parts
        # City, State or City, Country or State, Country
        if second.upper() in us_states:
            return {'city': fix_city_capitalization(first).title(), 'state': normalize_state(second), 'country': 'United States'}
        if second.lower() in us_states_lower:
            return {'city': fix_city_capitalization(first).title(), 'state': normalize_state(second), 'country': 'United States'}
        if second.upper() in ca_provinces:
            return {'city': fix_city_capitalization(first).title(), 'state': normalize_state(second), 'country': 'Canada'}
        if second.lower() in ca_provinces_lower:
            return {'city': fix_city_capitalization(first).title(), 'state': normalize_state(second), 'country': 'Canada'}
        # State, Country
        if first.upper() in us_states and normalize_country(second) == 'United States':
            return {'city': None, 'state': normalize_state(first), 'country': 'United States'}
        if first.upper() in ca_provinces and normalize_country(second) == 'Canada':
            return {'city': None, 'state': normalize_state(first), 'country': 'Canada'}
        # City, Country
        return {'city': fix_city_capitalization(first).title(), 'state': None, 'country': normalize_country(second)}

    if len(parts) == 1:
        part = parts[0]
        # State abbr/full
        if part.upper() in us_states:
            return {'city': None, 'state': normalize_state(part), 'country': 'United States'}
        if part.lower() in us_states_lower:
            return {'city': None, 'state': normalize_state(part), 'country': 'United States'}
        if part.upper() in ca_provinces:
            return {'city': None, 'state': normalize_state(part), 'country': 'Canada'}
        if part.lower() in ca_provinces_lower:
            return {'city': None, 'state': normalize_state(part), 'country': 'Canada'}
        # Check if it's a full state name (case insensitive)
        for abbr, full_name in us_states.items():
            if part.lower() == full_name.lower():
                return {'city': None, 'state': full_name, 'country': 'United States'}
        for abbr, full_name in ca_provinces.items():
            if part.lower() == full_name.lower():
                return {'city': None, 'state': full_name, 'country': 'Canada'}
        # Country
        country = normalize_country(part)
        if country:
            return {'city': None, 'state': None, 'country': country}
        # City
        return {'city': fix_city_capitalization(part).title(), 'state': None, 'country': None}

    # Fallback for 3+ parts
    city = fix_city_capitalization(parts[0]).title() if parts[0] else None
    state = normalize_state(parts[1]) if len(parts) > 1 else None
    country = normalize_country(parts[2]) if len(parts) > 2 else None
    return {'city': city, 'state': state, 'country': country}


def parse_competitor_name(name_str):
    """
    Parse competitor name string and handle comma-separated names by swapping the order.
    Example: "Smith, John" -> "John Smith"
    """
    if pd.isna(name_str) or name_str == '' or name_str == ' ':
        return name_str
    
    name_str = str(name_str).strip()
    
    # Check if there's a comma in the name
    if ',' in name_str:
        # Split by comma and clean up each part
        parts = [part.strip() for part in name_str.split(',') if part.strip()]
        
        if len(parts) >= 2:
            # Swap the order: "Last, First" -> "First Last"
            # Join all parts after the first one as the first name (in case of multiple first names)
            first_name = ' '.join(parts[1:])
            last_name = parts[0]
            
            # Combine them in the correct order
            return f"{first_name} {last_name}".strip()
    
    # If no comma or only one part, return as is
    return name_str

# Apply competitor name parsing to handle comma-separated names
cleaned_df['Competitor Name'] = cleaned_df['Competitor Name'].apply(parse_competitor_name)


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



def apply_division_mapping(cleaned_df):
    """
    Apply division name mapping from JSON file and return the cleaned DataFrame.
    """
    # Load division names mapping from JSON
    with open('keys/division_names.json', 'r', encoding='utf-8') as f:
        division_mapping = json.load(f)

    def create_division_lookup(mapping_dict):
        """
        Create a flat lookup dictionary for faster division name mapping.
        """
        lookup = {}
        for standard_name, variations in mapping_dict.items():
            if isinstance(variations, list):
                for variation in variations:
                    lookup[variation.lower()] = standard_name
        return lookup

    # Create lookup dictionary for faster mapping
    division_lookup = create_division_lookup(division_mapping)

    def find_division_mapping(division_name, lookup_dict):
        """
        Fast lookup for division name mapping using pre-built dictionary.
        """
        if pd.isna(division_name) or division_name == '':
            return division_name
        return lookup_dict.get(division_name.lower(), division_name)

    # Apply the division name mapping
    original_divisions = cleaned_df['Division'].copy()
    cleaned_df['Division'] = cleaned_df['Division'].apply(
        lambda x: find_division_mapping(x, division_lookup)
    )

    # Count how many divisions were mapped
    mapped_count = 0
    unmapped_divisions = []
    
    for orig, mapped in zip(original_divisions, cleaned_df['Division']):
        if pd.notna(orig) and orig != '' and orig.lower() != mapped.lower():
            mapped_count += 1
        elif pd.notna(orig) and orig != '' and orig.lower() not in division_lookup:
            unmapped_divisions.append(orig)
    
    # Remove duplicates and sort alphabetically
    unmapped_divisions = sorted(list(set(unmapped_divisions)))
    
    # Save unmapped divisions to JSON file
    with open('all/unmapped_divisions.json', 'w', encoding='utf-8') as f:
        json.dump(unmapped_divisions, f, ensure_ascii=False, indent=2)
    
    print(f"Division name mapping: {mapped_count} divisions were standardized")
    print(f"Unmapped divisions saved to: all/unmapped_divisions.json")

    # Show some examples of mappings
    if mapped_count > 0:
        mapping_examples = pd.DataFrame({
            'Original': original_divisions,
            'Standardized': cleaned_df['Division']
        })
        mapping_examples = mapping_examples[
            (mapping_examples['Original'] != mapping_examples['Standardized']) & 
            (mapping_examples['Original'].notna()) & 
            (mapping_examples['Original'] != '')
        ].drop_duplicates().head(15)
        
        print("\nExamples of division name mappings:")
        for _, row in mapping_examples.iterrows():
            print(f"  '{row['Original']}' -> '{row['Standardized']}'")
        
        # Show unique divisions that were mapped
        unique_mappings = mapping_examples.drop_duplicates(subset=['Original', 'Standardized'])
        print(f"\nUnique division name mappings: {len(unique_mappings)}")
        if len(unique_mappings) > 0:
            print("First 10 unique mappings:")
            for _, row in unique_mappings.head(10).iterrows():
                print(f"  '{row['Original']}' -> '{row['Standardized']}'")
    
    return cleaned_df

# Apply the division mapping function
cleaned_df = apply_division_mapping(cleaned_df)

# Create Division Subtype column
def extract_division_subtype(division_name):
    """
    Extract the subtype from division names that contain a dash.
    Example: 'mensbb - heavyweight' -> 'heavyweight'
    """
    if pd.isna(division_name) or division_name == '':
        return None
    
    # Split by dash and strip whitespace
    parts = division_name.split('-')
    if len(parts) > 1:
        # Return the part after the dash, stripped of whitespace
        return parts[1].strip()
    else:
        # No dash found, return None
        return None

# Create the Division Subtype column
cleaned_df['Division Subtype'] = cleaned_df['Division'].apply(extract_division_subtype)

# Update Division column to remove the subtype part
def clean_division_name(division_name):
    """
    Remove the subtype part from division names that contain a dash.
    Example: 'mensbb - heavyweight' -> 'mensbb'
    """
    if pd.isna(division_name) or division_name == '':
        return division_name
    
    # Split by dash and return the first part, stripped of whitespace
    parts = division_name.split('-')
    return parts[0].strip()

# Update the Division column to remove subtypes
cleaned_df['Division'] = cleaned_df['Division'].apply(clean_division_name)

# Print statistics about Division Subtype creation
subtype_count = cleaned_df['Division Subtype'].notna().sum()
total_divisions = len(cleaned_df)
print(f"\nDivision Subtype creation:")
print(f"  Total divisions: {total_divisions}")
print(f"  Divisions with subtypes: {subtype_count}")
print(f"  Divisions without subtypes: {total_divisions - subtype_count}")

# Show examples of divisions with subtypes
if subtype_count > 0:
    subtype_examples = cleaned_df[cleaned_df['Division Subtype'].notna()][['Division', 'Division Subtype']].drop_duplicates().head(10)
    print(f"\nExamples of divisions with subtypes:")
    for _, row in subtype_examples.iterrows():
        print(f"  Division: '{row['Division']}', Subtype: '{row['Division Subtype']}'")

# Show unique division subtypes
unique_subtypes = cleaned_df['Division Subtype'].dropna().unique()
if len(unique_subtypes) > 0:
    print(f"\nUnique division subtypes: {sorted(unique_subtypes)}")

# Create Division Level column (always "pro")
cleaned_df['Division Level'] = 'pro'
print(f"\nDivision Level column created: all rows set to 'pro'")

# Judging adjustment function
def process_judging_columns(df):
    """
    Rename judging columns to have consistent naming and parse numeric columns to integers:
    - Judging -> Judging 1
    - Finals -> Judging 2
    - Round 2 -> Judging 3
    - Round 3 -> Judging 4
    
    Also parse Judging 1-4, Routine, Total, and Place columns to integers.
    """
    column_mapping = {
        'Judging': 'Judging 1',
        'Finals': 'Judging 2',
        'Round 2': 'Judging 3',
        'Round 3': 'Judging 4'
    }
    
    # Rename columns that exist in the DataFrame
    existing_columns = [col for col in column_mapping.keys() if col in df.columns]
    if existing_columns:
        df = df.rename(columns={col: column_mapping[col] for col in existing_columns})
        print(f"Renamed judging columns: {existing_columns}")
    else:
        print("No judging columns found to rename")
    
    # Parse numeric columns to integers
    numeric_columns = ['Judging 1', 'Judging 2', 'Judging 3', 'Judging 4', 'Routine', 'Total', 'Place']
    
    for col in numeric_columns:
        if col in df.columns:
            # Convert to numeric, coercing errors to NaN, then to Int64 (which handles NaN)
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
            print(f"Parsed {col} column to integers")
        else:
            print(f"Column {col} not found in DataFrame")
    
    return df

# Apply the judging column processing
cleaned_df = process_judging_columns(cleaned_df)

cleaned_df['Location'] = cleaned_df['Location'].str.title()
cleaned_df['Country'] = cleaned_df['Country'].str.title()


parsed = cleaned_df['Location'].apply(parse_location)
cleaned_df['Location City'] = parsed.apply(lambda x: x['city'])
cleaned_df['Location State'] = parsed.apply(lambda x: x['state'])
cleaned_df['Location Country'] = parsed.apply(lambda x: x['country'])

parsed2 = cleaned_df['Country'].apply(parse_location)
cleaned_df['Competitor City'] = parsed2.apply(lambda x: x['city'])
cleaned_df['Competitor State'] = parsed2.apply(lambda x: x['state'])
cleaned_df['Competitor Country'] = parsed2.apply(lambda x: x['country'])


# Order by start date and Competition
cleaned_df = cleaned_df.sort_values(by=['Start Date', 'Competition'])

# new column order: Competition,Location,Date,Competitor Name,Country,Judging,Finals,Round 2,Round 3,Routine,Total,Place,Competition Type
cleaned_df = cleaned_df[['Start Date', 'End Date', 'Competition', 'Location City', 'Location State', 'Location Country', 'Competitor Name', 'Competitor City', 'Competitor State', 'Competitor Country', 'Judging 1', 'Judging 2', 'Judging 3', 'Judging 4', 'Routine', 'Total', 'Place', 'Division', 'Division Subtype', 'Division Level', 'Source', 'Location', 'Country']]

# Save the cleaned DataFrame to a new CSV file
cleaned_df.to_csv('data/all/all_clean.csv', index=False)

print('Cleaned data written to data/all/all_clean.csv')

# Print unique date strings from the 'Date' column
#print(cleaned_df['Date'].unique())

