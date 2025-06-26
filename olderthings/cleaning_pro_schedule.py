import pandas as pd
import numpy as np
import re
import ast
import json

def showStat(df):
    print('-------------Dataframe Stats--------------')
    print(df.shape) # return me how many rows and columns 
    print(df.dtypes) # return me the data types of each column
    print("\n")
    print("\n")

def parse_dates(date_str):
    if pd.isna(date_str) or date_str == 'nan':
        return None, None
    
    try:
        date_str = str(date_str).strip()
        
        # First check if it's a date range with different months (e.g., "Feb 27 - Mar 2")
        if ' - ' in date_str:
            start_date, end_date = date_str.split(' - ')
            
            # Parse start date
            start_month, start_day = start_date.strip().split(' ')
            start_month_num = pd.to_datetime(start_month, format='%b').month
            start_day = int(start_day.strip())
            
            # Parse end date
            if (len(end_date.strip().split(' ')) == 2):     
                end_month, end_day = end_date.strip().split(' ')
                end_month_num = pd.to_datetime(end_month, format='%b').month
                end_day = int(end_day.strip())
            else:
                end_day = int(end_date.strip())
                end_month_num = start_month_num
                end_month = start_month
            
            # Format dates
            start_date_str = f"{start_day:02d}.{start_month_num:02d}.2025"
            end_date_str = f"{end_day:02d}.{end_month_num:02d}.2025"
            return start_date_str, end_date_str
        
        # Then check if it's a date range in the same month (e.g., "Apr 4-6")
        elif '-' in date_str and not ' - ' in date_str:
            start_date, end_date = date_str.split('-')

            # Parse start date
            start_month, start_day = start_date.strip().split(' ')
            start_month_num = pd.to_datetime(start_month, format='%b').month
            start_day = int(start_day.strip())
            
            # Parse end date
            if (len(end_date.strip().split(' ')) == 2): 
                end_month, end_day = end_date.strip().split(' ')
                end_month_num = pd.to_datetime(end_month, format='%b').month
                end_day = int(end_day.strip())
            else:
                end_day = int(end_date.strip())
                end_month_num = start_month_num
                end_month = start_month
            
            # Format dates
            start_date_str = f"{start_day:02d}.{start_month_num:02d}.2025"
            end_date_str = f"{end_day:02d}.{end_month_num:02d}.2025"
            return start_date_str, end_date_str
        
        # Finally, handle single dates (e.g., "May 2")
        else:
            try:
                # Parse the date
                parts = date_str.split()
                if len(parts) != 2:
                    return None, None
                    
                month, day = parts
                month_num = pd.to_datetime(month, format='%b').month
                day = int(day.strip())
                
                # Format date
                date_str = f"{day:02d}.{month_num:02d}.2025"
                return date_str, date_str
            except:
                # Try pandas parsing as fallback
                date_obj = pd.to_datetime(date_str + " 2025", format="%b %d %Y", errors="coerce")
                if pd.isnull(date_obj):
                    return None, None
                date_str = date_obj.strftime("%d.%m.%Y")
                return date_str, date_str
            
    except Exception as e:
        print(f"Error parsing date: {date_str}, Error: {e}")
        return None, None

def parse_name(name):
    if pd.isna(name):
        return pd.isna
    with open('competitionNameKeys.json', 'r') as f:
        competitionNameKeys = json.load(f)
    found = False
    for key, values in competitionNameKeys.items():
        if name in values:
            found = True
            return key
    if not found:
        print(name)

def parse_country(entry):
    if pd.isna(entry):
        return {"city": "", "state": "", "country": ""}
    # Use regular expressions to split the entry into city, state, and country
    parts = entry.split(',')
    city = parts[0].strip() if parts[0].strip() else ""
    state = ""
    country = ""
    if len(parts) == 2:
        if "Florida" in parts[1] or "florida" in parts[1] or "FL" == parts[1]:
            state = "FL"
            country = 'United States'
        elif "Texas" in parts[1] or "texas" in parts[1] or "TX" == parts[1]:
            state = "TX"
            country = 'United States'
        elif "Tennessee" in parts[1] or "tennessee" in parts[1] or "TN" == parts[1]:
            state = "TN"
            country = 'United States'
        elif "California" in parts[1] or "california" in parts[1] or "CA" == parts[1]:
            state = "CA"
            country = 'United States'
        elif "New York" in parts[1] or "new york" in parts[1] or "NY" == parts[1]:
            state = "NY"
            country = 'United States'
        elif "Nevada" in parts[1] or "nevada" in parts[1] or "NV" == parts[1]:
            state = "NV"
            country = 'United States'
        elif "Georgia" in parts[1] or "georgia" in parts[1] or "GA" == parts[1]:
            state = "GA"
            country = 'United States'
        elif "Arizona" in parts[1] or "arizona" in parts[1] or "AZ" == parts[1]:
            state = "AZ"
            country = 'United States'
        elif "Virginia" in parts[1] or "virginia" in parts[1] or "VA" == parts[1]:
            state = "VA"
            country = 'United States'
        elif "Oklahoma" in parts[1] or "oklahoma" in parts[1] or "OK" == parts[1]:
            state = "OK"
            country = 'United States'
        elif "Illinois" in parts[1] or "illinois" in parts[1] or "IL" == parts[1]:
            state = "IL"
            country = 'United States'
        elif "New Jersey" in parts[1] or "new jersey" in parts[1] or "NJ" == parts[1]:
            state = "NJ"
            country = 'United States'
        elif "Pennsylvania" in parts[1] or "pennsylvania" in parts[1] or "PA" == parts[1]:
            state = "PA"
            country = 'United States'
        elif "Ohio" in parts[1] or "ohio" in parts[1] or "OH" == parts[1]:
            state = "OH"
            country = 'United States'
        elif "Michigan" in parts[1] or "michigan" in parts[1] or "MI" == parts[1]:
            state = "MI"
            country = 'United States'
        elif "North Carolina" in parts[1] or "north carolina" in parts[1] or "NC" == parts[1]:
            state = "NC"
            country = 'United States'
        elif "South Carolina" in parts[1] or "south carolina" in parts[1] or "SC" == parts[1]:
            state = "SC"
            country = 'United States'
        elif "Alabama" in parts[1] or "alabama" in parts[1] or "AL" == parts[1]:
            state = "AL"
            country = 'United States'
        elif "Mississippi" in parts[1] or "mississippi" in parts[1] or "MS" == parts[1]:
            state = "MS"
            country = 'United States'
        elif "Louisiana" in parts[1] or "louisiana" in parts[1] or "LA" == parts[1]:
            state = "LA"
            country = 'United States'
        elif "Colorado" in parts[1] or "colorado" in parts[1] or "CO" == parts[1]:
            state = "CO"
            country = 'United States'
        elif "Washington" in parts[1] or "washington" in parts[1] or "WA" == parts[1]:
            state = "WA"
            country = 'United States'
        elif "Oregon" in parts[1] or "oregon" in parts[1] or "OR" == parts[1]:
            state = "OR"
            country = 'United States'
        elif "Utah" in parts[1] or "utah" in parts[1] or "UT" == parts[1]:
            state = "UT"
            country = 'United States'
        elif "Montana" in parts[1] or "montana" in parts[1] or "MT" == parts[1]:
            state = "MT"
            country = 'United States'
        elif "Wyoming" in parts[1] or "wyoming" in parts[1] or "WY" == parts[1]:
            state = "WY"
            country = 'United States'
        elif "Idaho" in parts[1] or "idaho" in parts[1] or "ID" == parts[1]:
            state = "ID"
            country = 'United States'
        elif "New Mexico" in parts[1] or "new mexico" in parts[1] or "NM" == parts[1]:
            state = "NM"
            country = 'United States'
        elif "Kansas" in parts[1] or "kansas" in parts[1] or "KS" == parts[1]:
            state = "KS"
            country = 'United States'
        elif "Missouri" in parts[1] or "missouri" in parts[1] or "MO" == parts[1]:
            state = "MO"
            country = 'United States'
        elif "Arkansas" in parts[1] or "arkansas" in parts[1] or "AR" == parts[1]:
            state = "AR"
            country = 'United States'
        elif "Wisconsin" in parts[1] or "wisconsin" in parts[1] or "WI" == parts[1]:
            state = "WI"
            country = 'United States'
        elif "Minnesota" in parts[1] or "minnesota" in parts[1] or "MN" == parts[1]:
            state = "MN"
            country = 'United States'
        elif "Iowa" in parts[1] or "iowa" in parts[1] or "IA" == parts[1]:
            state = "IA"
            country = 'United States'
        elif "Nebraska" in parts[1] or "nebraska" in parts[1] or "NE" == parts[1]:
            state = "NE"
            country = 'United States'
        elif "South Dakota" in parts[1] or "south dakota" in parts[1] or "SD" == parts[1]:
            state = "SD"
            country = 'United States'
        elif "North Dakota" in parts[1] or "north dakota" in parts[1] or "ND" == parts[1]:
            state = "ND"
            country = 'United States'
        elif "Maine" in parts[1] or "maine" in parts[1] or "ME" == parts[1]:
            state = "ME"
            country = 'United States'
        elif "Vermont" in parts[1] or "vermont" in parts[1] or "VT" == parts[1]:
            state = "VT"
            country = 'United States'
        elif "New Hampshire" in parts[1] or "new hampshire" in parts[1] or "NH" == parts[1]:
            state = "NH"
            country = 'United States'
        elif "Massachusetts" in parts[1] or "massachusetts" in parts[1] or "MA" == parts[1]:
            state = "MA"
            country = 'United States'
        elif "Connecticut" in parts[1] or "connecticut" in parts[1] or "CT" == parts[1]:
            state = "CT"
            country = 'United States'
        elif "Rhode Island" in parts[1] or "rhode island" in parts[1] or "RI" == parts[1]:
            state = "RI"
            country = 'United States'
        elif "Delaware" in parts[1] or "delaware" in parts[1] or "DE" == parts[1]:
            state = "DE"
            country = 'United States'
        elif "Maryland" in parts[1] or "maryland" in parts[1] or "MD" == parts[1]:
            state = "MD"
            country = 'United States'
        elif "West Virginia" in parts[1] or "west virginia" in parts[1] or "WV" == parts[1]:
            state = "WV"
            country = 'United States'
        elif "Kentucky" in parts[1] or "kentucky" in parts[1] or "KY" == parts[1]:
            state = "KY"
            country = 'United States'
        elif "Indiana" in parts[1] or "indiana" in parts[1] or "IN" == parts[1] :
            state = "IN"
            country = 'United States'
        elif "Hawaii" in parts[1] or "hawaii" in parts[1] or "HI" == parts[1]:
            state = "HI"
            country = 'United States'
        elif "Alaska" in parts[1] or "alaska" in parts[1] or "AK" == parts[1]:
            state = "AK"
            country = 'United States'
        elif "United States" in parts[1] or "united states" in parts[1]:
            state = parts[1][:2].strip()
            country = 'United States'
        else:
            country = parts[1].strip()
    elif len(parts) == 3:
        state = parts[1].strip()
        country = parts[2].strip()
    else:
        country = parts[0].strip()
    return {"city": city, "state": state, "country": country}

def parsePromoter(promoter):
    return re.sub(r'\s*\(.*?\)\s*', '', promoter).strip()

def groupByUrl(df):
    # For rows without URL, create a composite key using competition name and date
    df['grouping_key'] = df.apply(lambda row: 
        row['comp_url'] if pd.notna(row['comp_url']) 
        else f"{row['competition']}_{row['date']}", axis=1)
    
    grouped = df.groupby('grouping_key').agg({
        'comp_url': 'first',  # Keep the original URL (or NaN)
        'date': 'first',
        'location': 'first',
        'competition_subtype': 'first',
        'competition_type': lambda x: list(x),
        'promoter': 'first',
        'competition': 'first'
    }).reset_index()
    
    # Drop the temporary grouping key
    grouped = grouped.drop('grouping_key', axis=1)
    return grouped

def generalCleaning(df):
    print('-------------General Cleaning--------------')
    print("Columns in dataframe:", df.columns.tolist())
    print("First row:", df.iloc[0].to_dict())

    # Filter out competitions with 'natural' in their name
    df = df[~df['competition'].str.lower().str.contains('natural', na=False)]

    # Filter out competitions that have 'masters' in division_type but don't have 'open'
    df = df[~((df['competition_subtype'].str.lower().str.contains('masters', na=False)) & 
              (~df['competition_subtype'].str.lower().str.contains('open', na=False)))]

    # Clean up competition names by removing 'masters' and anything after it
    df['competition'] = df['competition'].apply(lambda x: str(x).split('masters')[0].strip() if pd.notna(x) and 'masters' in str(x).lower() else x)

    # Create eventName based on URL or competition name
    def create_event_name(row):
        if pd.isna(row['comp_url']) or str(row['comp_url']).strip() == '':
            # For entries without URL, create a slug from the competition name
            name = str(row['competition']).lower()
            name = re.sub(r'2025\s*', '', name)  # Remove 2025
            name = re.sub(r'\s+', '_', name)     # Replace spaces with underscores
            name = re.sub(r'[^a-z0-9_-]', '', name)  # Remove any special characters
            return name
        elif 'ifbbpro.com' in str(row['comp_url']).lower():
            return row['comp_url'].split('/')[-2].replace('-', '_').lower()
        else:
            # For non-IFBB URLs, also use competition name
            name = str(row['competition']).lower()
            name = re.sub(r'2025\s*', '', name)  # Remove 2025
            name = re.sub(r'\s+', '_', name)     # Replace spaces with underscores
            name = re.sub(r'[^a-z0-9_-]', '', name)  # Remove any special characters
            return name

    # Create eventName before renaming columns
    df["eventName"] = df.apply(create_event_name, axis=1)
    
    # Clean up all name fields to remove 'masters' and anything after it
    df['competition'] = df['competition'].apply(lambda x: str(x).split('masters')[0].strip() if pd.notna(x) and 'masters' in str(x).lower() else x)
    df['competition'] = df['competition'].apply(lambda x: str(x).replace(' + MASTERS', '').strip() if pd.notna(x) else x)
    
    # Remove age-related numbers and slashes from competition name
    df['competition'] = df['competition'].apply(lambda x: re.sub(r'\s*\d+/\d+\s*', '', str(x)) if pd.notna(x) else x)
    df['competition'] = df['competition'].apply(lambda x: re.sub(r'\s*\d+\s*', '', str(x)) if pd.notna(x) else x)
    df['competition'] = df['competition'].apply(lambda x: re.sub(r'/', '', str(x)) if pd.notna(x) else x)
    
    df['eventName'] = df['eventName'].apply(lambda x: str(x).split('masters')[0].strip() if pd.notna(x) and 'masters' in str(x).lower() else x)
    df['eventName'] = df['eventName'].apply(lambda x: str(x).replace('__', '_').strip() if pd.notna(x) else x)
    df['eventName'] = df['eventName'].apply(lambda x: str(x).rstrip('_') if pd.notna(x) else x)
    
    df["name"] = df["eventName"].str.replace(r'2025_', '', regex=True).str.lower().str.strip()
    df["name"] = df["name"].apply(lambda x: str(x).split('masters')[0].strip() if pd.notna(x) and 'masters' in str(x).lower() else x)
    df["name"] = df["name"].apply(lambda x: str(x).replace('__', '_').strip() if pd.notna(x) else x)
    df["name"] = df["name"].apply(lambda x: str(x).rstrip('_') if pd.notna(x) else x)
    
    df["name_key"] = df["name"].apply(parse_name)

    # Now rename columns to match the desired format
    df = df.rename(columns={
        'comp_url': 'url',
        'date': 'start_date',
        'competition_subtype': 'division_type',
        'competition_type': 'divisions',
        'competition': 'name'
    })

    # Process dates - ensure date column is string type before processing
    df["start_date"] = df["start_date"].astype(str)
    df["start_date"], df["end_date"] = zip(*df["start_date"].apply(parse_dates))

    # Add missing columns
    df['comp_type'] = 'IFBB Pro'
    df['promoter_website'] = ''
    df['year'] = 2025

    df['location'] = df['location'].astype(str).apply(parse_country)
    df['promoter'] = df['promoter'].apply(parsePromoter)

    return df

# Read and process the CSV
df = pd.read_csv('data_raw/sidebar/pro_schedule_2025_unique.csv')

showStat(df)

#df = groupByUrl(df)

df = generalCleaning(df)

# Reorder columns to match the desired format
df = df[['url', 'start_date', 'end_date', 'location', 'comp_type', 'divisions', 
         'division_type', 'promoter', 'promoter_website', 'year', 'eventName', 
         'name', 'name_key']]

# Clean up division_type to only show 'open' if it contains 'open'
df['division_type'] = df['division_type'].apply(lambda x: 'open' if pd.notna(x) and 'open' in str(x).lower() else x)

# Sort by start_date
df = df.sort_values('start_date')

df.to_csv('data_clean/sidebar/pro_schedule_2025.csv', index=False) 