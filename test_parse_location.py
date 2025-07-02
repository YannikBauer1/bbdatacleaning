import pandas as pd
import re

def parse_location(location_str):
    """
    Parse location string into city, state, and country.
    Handles various formats including:
    - "Atlanta, Georgia" -> city: "Atlanta", state: "Georgia", country: "United States"
    - "Toronto, Canada" -> city: "Toronto", state: None, country: "Canada"
    - "Las Vegas, NV" -> city: "Las Vegas", state: "NV", country: "United States"
    - "Brazil" -> city: None, state: None, country: "Brazil"
    - "New York, NY, USA" -> city: "New York", state: "NY", country: "United States"
    - "London, United Kingdom" -> city: "London", state: None, country: "United Kingdom"
    
    Returns a dictionary with keys: city, state, country
    """
    if pd.isna(location_str) or location_str == '' or location_str == ' ':
        return {'city': None, 'state': None, 'country': None}
    
    location_str = str(location_str).strip()
    
    # Remove quotes if present
    location_str = location_str.replace('"', '').replace("'", "")
    
    # Handle special cases with leading/trailing commas
    location_str = re.sub(r'^,+|,+$', '', location_str).strip()
    
    # Split by comma and clean up each part
    parts = [part.strip() for part in location_str.split(',') if part.strip()]
    
    if not parts:
        return {'city': None, 'state': None, 'country': None}
    
    # US State abbreviations and full names mapping
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
        'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
        'DC': 'District of Columbia'
    }
    
    # Common country variations
    country_mappings = {
        'usa': 'United States', 'united states': 'United States', 'united states of america': 'United States',
        'uk': 'United Kingdom', 'united kingdom': 'United Kingdom', 'england': 'United Kingdom',
        'scotland': 'United Kingdom', 'wales': 'United Kingdom', 'northern ireland': 'United Kingdom',
        'canada': 'Canada', 'canadian': 'Canada',
        'australia': 'Australia', 'australian': 'Australia',
        'brazil': 'Brazil', 'brasil': 'Brazil',
        'germany': 'Germany', 'deutschland': 'Germany',
        'france': 'France', 'francia': 'France',
        'italy': 'Italy', 'italia': 'Italy',
        'spain': 'Spain', 'espana': 'Spain',
        'netherlands': 'Netherlands', 'holland': 'Netherlands',
        'sweden': 'Sweden', 'svecia': 'Sweden',
        'norway': 'Norway', 'norge': 'Norway',
        'finland': 'Finland', 'suomi': 'Finland',
        'denmark': 'Denmark', 'danmark': 'Denmark',
        'poland': 'Poland', 'polska': 'Poland',
        'czech republic': 'Czech Republic', 'czech rep.': 'Czech Republic',
        'slovakia': 'Slovakia', 'slovak republic': 'Slovakia',
        'hungary': 'Hungary', 'magyarorszag': 'Hungary',
        'romania': 'Romania', 'romania': 'Romania',
        'bulgaria': 'Bulgaria',
        'russia': 'Russia', 'russian federation': 'Russia',
        'ukraine': 'Ukraine',
        'belarus': 'Belarus',
        'lithuania': 'Lithuania',
        'latvia': 'Latvia',
        'estonia': 'Estonia',
        'moldova': 'Moldova',
        'serbia': 'Serbia',
        'croatia': 'Croatia',
        'slovenia': 'Slovenia',
        'bosnia': 'Bosnia and Herzegovina', 'bosnia & herzegovina': 'Bosnia and Herzegovina',
        'montenegro': 'Montenegro',
        'albania': 'Albania',
        'macedonia': 'Macedonia',
        'greece': 'Greece',
        'turkey': 'Turkey', 'turkiye': 'Turkey',
        'israel': 'Israel',
        'lebanon': 'Lebanon',
        'jordan': 'Jordan',
        'iran': 'Iran',
        'iraq': 'Iraq',
        'kuwait': 'Kuwait',
        'qatar': 'Qatar',
        'uae': 'United Arab Emirates', 'united arab emirates': 'United Arab Emirates',
        'saudi arabia': 'Saudi Arabia',
        'oman': 'Oman',
        'yemen': 'Yemen',
        'egypt': 'Egypt',
        'libya': 'Libya',
        'tunisia': 'Tunisia', 'tunesia': 'Tunisia',
        'algeria': 'Algeria',
        'morocco': 'Morocco', 'morrocco': 'Morocco',
        'sudan': 'Sudan',
        'south africa': 'South Africa',
        'nigeria': 'Nigeria',
        'ghana': 'Ghana',
        'kenya': 'Kenya',
        'ethiopia': 'Ethiopia',
        'uganda': 'Uganda',
        'tanzania': 'Tanzania',
        'zimbabwe': 'Zimbabwe',
        'zambia': 'Zambia',
        'botswana': 'Botswana',
        'namibia': 'Namibia',
        'angola': 'Angola',
        'mozambique': 'Mozambique',
        'madagascar': 'Madagascar',
        'mauritius': 'Mauritius',
        'seychelles': 'Seychelles',
        'china': 'China',
        'japan': 'Japan', 'japon': 'Japan',
        'south korea': 'South Korea', 'korea': 'South Korea', 'republic of korea': 'South Korea',
        'north korea': 'North Korea',
        'taiwan': 'Taiwan', 'r.o.c': 'Taiwan', 'r.o.c.': 'Taiwan',
        'hong kong': 'Hong Kong', 'hong kong sar': 'Hong Kong', 'hksar': 'Hong Kong',
        'singapore': 'Singapore',
        'malaysia': 'Malaysia',
        'thailand': 'Thailand',
        'vietnam': 'Vietnam', 'viet nam': 'Vietnam',
        'cambodia': 'Cambodia',
        'laos': 'Laos',
        'myanmar': 'Myanmar', 'burma': 'Myanmar',
        'philippines': 'Philippines', 'phillipines': 'Philippines',
        'indonesia': 'Indonesia',
        'india': 'India',
        'pakistan': 'Pakistan',
        'bangladesh': 'Bangladesh',
        'sri lanka': 'Sri Lanka',
        'nepal': 'Nepal',
        'bhutan': 'Bhutan',
        'mongolia': 'Mongolia',
        'kazakhstan': 'Kazakhstan',
        'uzbekistan': 'Uzbekistan',
        'kyrgyzstan': 'Kyrgyzstan',
        'tajikistan': 'Tajikistan',
        'turkmenistan': 'Turkmenistan',
        'afghanistan': 'Afghanistan',
        'iran': 'Iran',
        'iraq': 'Iraq',
        'syria': 'Syria',
        'lebanon': 'Lebanon',
        'jordan': 'Jordan',
        'israel': 'Israel',
        'palestine': 'Palestine',
        'mexico': 'Mexico',
        'guatemala': 'Guatemala',
        'belize': 'Belize',
        'el salvador': 'El Salvador',
        'honduras': 'Honduras',
        'nicaragua': 'Nicaragua',
        'costa rica': 'Costa Rica', 'costa rico': 'Costa Rica',
        'panama': 'Panama',
        'colombia': 'Colombia',
        'venezuela': 'Venezuela', 'vanezuela': 'Venezuela',
        'ecuador': 'Ecuador',
        'peru': 'Peru',
        'bolivia': 'Bolivia',
        'chile': 'Chile',
        'argentina': 'Argentina',
        'paraguay': 'Paraguay', 'paraquay': 'Paraguay',
        'uruguay': 'Uruguay',
        'guyana': 'Guyana',
        'suriname': 'Suriname',
        'french guiana': 'French Guiana',
        'trinidad': 'Trinidad and Tobago', 'trinidad & tobago': 'Trinidad and Tobago',
        'barbados': 'Barbados',
        'jamaica': 'Jamaica',
        'haiti': 'Haiti',
        'dominican republic': 'Dominican Republic',
        'cuba': 'Cuba', 'cuban': 'Cuba',
        'puerto rico': 'Puerto Rico',
        'bahamas': 'Bahamas',
        'bermuda': 'Bermuda',
        'aruba': 'Aruba',
        'curacao': 'Curacao', 'curaco': 'Curacao',
        'bonaire': 'Bonaire',
        'sint maarten': 'Sint Maarten',
        'new zealand': 'New Zealand', 'new zeland': 'New Zealand',
        'fiji': 'Fiji',
        'papua new guinea': 'Papua New Guinea',
        'solomon islands': 'Solomon Islands',
        'vanuatu': 'Vanuatu',
        'new caledonia': 'New Caledonia',
        'french polynesia': 'French Polynesia',
        'tahiti': 'Tahiti',
        'samoa': 'Samoa',
        'tonga': 'Tonga',
        'cook islands': 'Cook Islands',
        'niue': 'Niue',
        'tokelau': 'Tokelau',
        'tuvalu': 'Tuvalu',
        'kiribati': 'Kiribati',
        'marshall islands': 'Marshall Islands',
        'micronesia': 'Micronesia',
        'palau': 'Palau',
        'nauru': 'Nauru',
        'guam': 'Guam',
        'northern mariana islands': 'Northern Mariana Islands',
        'american samoa': 'American Samoa',
        'hawaii': 'Hawaii',
        'alaska': 'Alaska'
    }
    
    # Normalize country names
    def normalize_country(country_str):
        if not country_str:
            return None
        country_lower = country_str.lower().strip()
        return country_mappings.get(country_lower, country_str)
    
    # Handle different patterns
    if len(parts) == 1:
        # Single part - could be city, state, or country
        part = parts[0]
        
        # Check if it's a US state abbreviation
        if part.upper() in us_states:
            return {'city': None, 'state': part.upper(), 'country': 'United States'}
        
        # Check if it's a US state full name
        for abbr, full_name in us_states.items():
            if part.lower() == full_name.lower():
                return {'city': None, 'state': abbr, 'country': 'United States'}
        
        # Check if it's a country
        normalized_country = normalize_country(part)
        if normalized_country:
            return {'city': None, 'state': None, 'country': normalized_country}
        
        # Assume it's a city
        return {'city': part, 'state': None, 'country': None}
    
    elif len(parts) == 2:
        # Two parts - could be "City, State" or "City, Country" or "State, Country"
        part1, part2 = parts
        
        print(f"DEBUG: Processing '{location_str}' -> parts: {parts}")
        print(f"DEBUG: part1='{part1}', part2='{part2}'")
        
        # Check if part2 is a US state abbreviation
        if part2.upper() in us_states:
            print(f"DEBUG: part2 '{part2}' is a US state abbreviation")
            return {'city': part1, 'state': part2.upper(), 'country': 'United States'}
        
        # Check if part2 is a US state full name
        for abbr, full_name in us_states.items():
            if part2.lower() == full_name.lower():
                print(f"DEBUG: part2 '{part2}' matches US state full name '{full_name}' -> abbreviation '{abbr}'")
                return {'city': part1, 'state': abbr, 'country': 'United States'}
        
        # Check if part2 is a country
        normalized_country = normalize_country(part2)
        if normalized_country:
            print(f"DEBUG: part2 '{part2}' is a country: '{normalized_country}'")
            return {'city': part1, 'state': None, 'country': normalized_country}
        
        # Check if part1 is a US state and part2 is a country
        if part1.upper() in us_states:
            normalized_country = normalize_country(part2)
            if normalized_country:
                return {'city': None, 'state': part1.upper(), 'country': normalized_country}
        
        # Default: assume city, country
        print(f"DEBUG: Default case - assuming city, country")
        return {'city': part1, 'state': None, 'country': part2}
    
    elif len(parts) >= 3:
        # Three or more parts - typically "City, State, Country"
        city = parts[0]
        state = parts[1]
        country_parts = parts[2:]
        country = ', '.join(country_parts)
        
        # Check if state is a US state abbreviation
        if state.upper() in us_states:
            normalized_country = normalize_country(country)
            return {'city': city, 'state': state.upper(), 'country': normalized_country or country}
        
        # Check if state is a US state full name
        for abbr, full_name in us_states.items():
            if state.lower() == full_name.lower():
                normalized_country = normalize_country(country)
                return {'city': city, 'state': abbr, 'country': normalized_country or country}
        
        # If state doesn't match US states, it might be a region/province
        normalized_country = normalize_country(country)
        return {'city': city, 'state': state, 'country': normalized_country or country}
    
    return {'city': None, 'state': None, 'country': None}

# Test cases
test_cases = [
    "Abbeville, Louisiana",
    "Abilene, Texas", 
    "Acworth, Georgia",
    "Addison, Texas",
    "Airway Heights, Washington",
    "Akron, Ohio",
    "Alabaster, Alabama",
    "Albany, Georgia",
    "Albany, New York",
    "Albuquerque, New Mexico",
    "Aldie, Virginia",
    "Alea, Hawaii",
    "Alexandria, Virginia",
    "Algonquin, Illinois",
    "Alhambra, California",
    "Aliso Viejo, California",
    "Allen, Texas",
    "Allentown, Pennsylvania",
    "Alliance, Nebraska",
    "Allison Park, Pennsylvania",
    "Alpharetta, Georgia",
    "Alpine, New Jersey",
    "Alta Loma, California",
    "Altamonte Springs, Florida",
    "Altapena, California",
    "Alton, Illinois",
    "Amarillo, Texas",
    "Ambridge, Pa",
    "Amesburg, Massachusetts",
    "Amherst, Ohio",
    "Amory, Mississippi",
    "Anaheim, California",
    "Anchorage, Alaska",
    "Anderson, Indiana",
    "Andover, New Jersey",
    "Ankeny, Iowa",
    "Annapolis, Maryland",
    "Anoka, Minnesota",
    # Test cases for three-part logic
    "Albany, New York, USA",
    "Albany, New York, United States",
    "Albany, NY, USA",
    "Albany, NY, United States",
    "Albuquerque, New Mexico, USA",
    "Albuquerque, NM, United States",
    "Alexandria, Virginia, USA",
    "Alexandria, VA, United States",
    "Anaheim, California, USA",
    "Anaheim, CA, United States"
]

print("Testing parse_location function:")
print("=" * 50)

for test_case in test_cases:
    result = parse_location(test_case)
    print(f"'{test_case}' -> {result}")
    if result['state'] and not result['country']:
        print(f"  WARNING: Has state '{result['state']}' but no country!")
    elif result['state'] and result['country'] != 'United States':
        print(f"  WARNING: Has state '{result['state']}' but country is '{result['country']}' instead of 'United States'!")
    print() 