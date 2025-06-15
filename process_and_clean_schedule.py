import pandas as pd
import numpy as np
import re
import json
import os
from pathlib import Path

def showStat(df):
    print('-------------Dataframe Stats--------------')
    print(df.shape)  # return me how many rows and columns 
    print(df.dtypes)  # return me the data types of each column
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
        if "Florida" in parts[1] or "florida" in parts[1] or "FL" == parts[1].strip():
            state = "FL"
            country = 'United States'
        elif "Texas" in parts[1] or "texas" in parts[1] or "TX" == parts[1].strip():
            state = "TX"
            country = 'United States'
        elif "Tennessee" in parts[1] or "tennessee" in parts[1] or "TN" == parts[1].strip():
            state = "TN"
            country = 'United States'
        elif "California" in parts[1] or "california" in parts[1] or "CA" == parts[1].strip():
            state = "CA"
            country = 'United States'
        elif "New York" in parts[1] or "new york" in parts[1] or "NY" == parts[1].strip():
            state = "NY"
            country = 'United States'
        elif "Nevada" in parts[1] or "nevada" in parts[1] or "NV" == parts[1].strip():
            state = "NV"
            country = 'United States'
        elif "Georgia" in parts[1] or "georgia" in parts[1] or "GA" == parts[1].strip():
            state = "GA"
            country = 'United States'
        elif "Arizona" in parts[1] or "arizona" in parts[1] or "AZ" == parts[1].strip():
            state = "AZ"
            country = 'United States'
        elif "Virginia" in parts[1] or "virginia" in parts[1] or "VA" == parts[1].strip():
            state = "VA"
            country = 'United States'
        elif "Oklahoma" in parts[1] or "oklahoma" in parts[1] or "OK" == parts[1].strip():
            state = "OK"
            country = 'United States'
        elif "Illinois" in parts[1] or "illinois" in parts[1] or "IL" == parts[1].strip():
            state = "IL"
            country = 'United States'
        elif "New Jersey" in parts[1] or "new jersey" in parts[1] or "NJ" == parts[1].strip():
            state = "NJ"
            country = 'United States'
        elif "Pennsylvania" in parts[1] or "pennsylvania" in parts[1] or "PA" == parts[1].strip():
            state = "PA"
            country = 'United States'
        elif "Ohio" in parts[1] or "ohio" in parts[1] or "OH" == parts[1].strip():
            state = "OH"
            country = 'United States'
        elif "Michigan" in parts[1] or "michigan" in parts[1] or "MI" == parts[1].strip():
            state = "MI"
            country = 'United States'
        elif "North Carolina" in parts[1] or "north carolina" in parts[1] or "NC" == parts[1].strip():
            state = "NC"
            country = 'United States'
        elif "South Carolina" in parts[1] or "south carolina" in parts[1] or "SC" == parts[1].strip():
            state = "SC"
            country = 'United States'
        elif "Alabama" in parts[1] or "alabama" in parts[1] or "AL" == parts[1].strip():
            state = "AL"
            country = 'United States'
        elif "Mississippi" in parts[1] or "mississippi" in parts[1] or "MS" == parts[1].strip():
            state = "MS"
            country = 'United States'
        elif "Louisiana" in parts[1] or "louisiana" in parts[1] or "LA" == parts[1].strip():
            state = "LA"
            country = 'United States'
        elif "Colorado" in parts[1] or "colorado" in parts[1] or "CO" == parts[1].strip():
            state = "CO"
            country = 'United States'
        elif "Washington" in parts[1] or "washington" in parts[1] or "WA" == parts[1].strip():
            state = "WA"
            country = 'United States'
        elif "Oregon" in parts[1] or "oregon" in parts[1] or "OR" == parts[1].strip():
            state = "OR"
            country = 'United States'
        elif "Utah" in parts[1] or "utah" in parts[1] or "UT" == parts[1].strip():
            state = "UT"
            country = 'United States'
        elif "Montana" in parts[1] or "montana" in parts[1] or "MT" == parts[1].strip():
            state = "MT"
            country = 'United States'
        elif "Wyoming" in parts[1] or "wyoming" in parts[1] or "WY" == parts[1].strip():
            state = "WY"
            country = 'United States'
        elif "Idaho" in parts[1] or "idaho" in parts[1] or "ID" == parts[1].strip():
            state = "ID"
            country = 'United States'
        elif "New Mexico" in parts[1] or "new mexico" in parts[1] or "NM" == parts[1].strip():
            state = "NM"
            country = 'United States'
        elif "Kansas" in parts[1] or "kansas" in parts[1] or "KS" == parts[1].strip():
            state = "KS"
            country = 'United States'
        elif "Missouri" in parts[1] or "missouri" in parts[1] or "MO" == parts[1].strip():
            state = "MO"
            country = 'United States'
        elif "Arkansas" in parts[1] or "arkansas" in parts[1] or "AR" == parts[1].strip():
            state = "AR"
            country = 'United States'
        elif "Wisconsin" in parts[1] or "wisconsin" in parts[1] or "WI" == parts[1].strip():
            state = "WI"
            country = 'United States'
        elif "Minnesota" in parts[1] or "minnesota" in parts[1] or "MN" == parts[1].strip():
            state = "MN"
            country = 'United States'
        elif "Iowa" in parts[1] or "iowa" in parts[1] or "IA" == parts[1].strip():
            state = "IA"
            country = 'United States'
        elif "Nebraska" in parts[1] or "nebraska" in parts[1] or "NE" == parts[1].strip():
            state = "NE"
            country = 'United States'
        elif "South Dakota" in parts[1] or "south dakota" in parts[1] or "SD" == parts[1].strip():
            state = "SD"
            country = 'United States'
        elif "North Dakota" in parts[1] or "north dakota" in parts[1] or "ND" == parts[1].strip():
            state = "ND"
            country = 'United States'
        elif "Maine" in parts[1] or "maine" in parts[1] or "ME" == parts[1].strip():
            state = "ME"
            country = 'United States'
        elif "Vermont" in parts[1] or "vermont" in parts[1] or "VT" == parts[1].strip():
            state = "VT"
            country = 'United States'
        elif "New Hampshire" in parts[1] or "new hampshire" in parts[1] or "NH" == parts[1].strip():
            state = "NH"
            country = 'United States'
        elif "Massachusetts" in parts[1] or "massachusetts" in parts[1] or "MA" == parts[1].strip():
            state = "MA"
            country = 'United States'
        elif "Connecticut" in parts[1] or "connecticut" in parts[1] or "CT" == parts[1].strip():
            state = "CT"
            country = 'United States'
        elif "Rhode Island" in parts[1] or "rhode island" in parts[1] or "RI" == parts[1].strip():
            state = "RI"
            country = 'United States'
        elif "Delaware" in parts[1] or "delaware" in parts[1] or "DE" == parts[1].strip():
            state = "DE"
            country = 'United States'
        elif "Maryland" in parts[1] or "maryland" in parts[1] or "MD" == parts[1].strip():
            state = "MD"
            country = 'United States'
        elif "West Virginia" in parts[1] or "west virginia" in parts[1] or "WV" == parts[1].strip():
            state = "WV"
            country = 'United States'
        elif "Kentucky" in parts[1] or "kentucky" in parts[1] or "KY" == parts[1].strip():
            state = "KY"
            country = 'United States'
        elif "Indiana" in parts[1] or "indiana" in parts[1] or "IN" == parts[1].strip():
            state = "IN"
            country = 'United States'
        elif "Hawaii" in parts[1] or "hawaii" in parts[1] or "HI" == parts[1].strip():
            state = "HI"
            country = 'United States'
        elif "Alaska" in parts[1] or "alaska" in parts[1] or "AK" == parts[1].strip():
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
    elif len(parts) == 1:
        country = parts[0].strip()
        city = ""
    else:
        country = parts[0].strip()
    return {"city": city, "state": state, "country": country}

def parsePromoter(promoter):
    return re.sub(r'\s*\(.*?\)\s*', '', promoter).strip()

def generalCleaning(df):
    print('-------------General Cleaning--------------')
    print("Columns in dataframe:", df.columns.tolist())
    print("First row:", df.iloc[0].to_dict())

    # Filter out competitions with 'natural' in their name
    df = df[~df['competition'].str.lower().str.contains('natural', na=False)]

    # Filter out competitions that have 'masters' in division_type but don't have 'open'
    df = df[~((df['competition_subtype'].str.lower().str.contains('masters', na=False)) & 
              (~df['competition_subtype'].str.lower().str.contains('open', na=False)))]

    # Only keep competitions that have 'OPEN' in their subtype
    #df = df[df['competition_subtype'].str.contains('OPEN', na=False)]

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
            # Get the URL part and remove the year prefix
            url_part = row['comp_url'].split('/')[-2]
            url_part = re.sub(r'^2025-', '', url_part)  # Remove 2025- prefix
            return url_part.replace('-', '_').lower()
        else:
            # For non-IFBB URLs, also use competition name
            name = str(row['competition']).lower()
            name = re.sub(r'2025\s*', '', name)  # Remove 2025
            name = re.sub(r'\s+', '_', name)     # Replace spaces with underscores
            name = re.sub(r'[^a-z0-9_-]', '', name)  # Remove any special characters
            return name

    # Create eventName before renaming columns
    df["eventName"] = df.apply(create_event_name, axis=1)
    
    # Create name_key from eventName
    df["name_key"] = df["eventName"].apply(parse_name)

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

    # Make divisions unique by converting to set and back to list
    def make_divisions_unique(div_list):
        if isinstance(div_list, list):
            return list(set(div_list))
        return []

    df['divisions'] = df['divisions'].apply(make_divisions_unique)

    return df

def process_and_clean_schedule():
    # Create necessary directories if they don't exist
    os.makedirs('data_raw/sidebar', exist_ok=True)
    os.makedirs('data_clean/sidebar', exist_ok=True)

    # Read the CSV file
    input_path = 'data_raw/sidebar/pro_schedule_2025.csv'
    output_path = 'data_raw/sidebar/2025_Schedule_unique.csv'
    final_output_path = 'data_clean/sidebar/2025_Schedule.csv'

    # Read the initial CSV
    df = pd.read_csv(input_path)

    # Process the CSV (equivalent to processSchedule.js functionality)
    print('-------------Initial Processing--------------')
    print(f"Processing {len(df)} rows (excluding header)")

    # Filter out competitions with 'NATURAL' and 'MASTERS' in subtype but don't have 'OPEN'
    df = df[~df['competition'].str.upper().str.contains('NATURAL', na=False)]
    df = df[~((df['competition_subtype'].str.upper().str.contains('MASTERS', na=False)) & 
              (~df['competition_subtype'].str.upper().str.contains('OPEN', na=False)))]

    # Convert to string first
    df['competition'] = df['competition'].astype(str)
    # Then clean up whitespace
    df['competition'] = df['competition'].apply(lambda x: re.sub(r'\s+', ' ', x).strip())

    # Group by competition name and aggregate competition types
    grouped = df.groupby('competition').agg({
        'comp_url': 'first',
        'date': 'first',
        'location': 'first',
        'competition_subtype': 'first',
        'competition_type': lambda x: list(set(x)),  # Convert to set to remove duplicates, then back to list
        'promoter': 'first'
    }).reset_index()

    # Save the intermediate processed file
    grouped.to_csv(output_path, index=False)
    print(f"Found {len(grouped)} unique competitions after filtering")
    print(f"Removed {len(df) - len(grouped)} competitions (duplicates and filtered)")
    print(f"Intermediate output written to: {output_path}")

    # Now perform the detailed cleaning
    df = generalCleaning(grouped)

    # Reorder columns to match the desired format and sort by start_date
    df = df[['eventName', 
             'name', 'name_key', 'url', 'start_date', 'end_date', 'location', 'comp_type', 'divisions', 
             'division_type', 'promoter', 'promoter_website', 'year']]

    # Clean up division_type to only show 'open' if it contains 'open'
    df['division_type'] = 'open'

    # Sort by start_date
    df = df.sort_values('name_key')

    # Save the final cleaned file
    df.to_csv(final_output_path, index=False)
    print(f"Final cleaned output written to: {final_output_path}")

if __name__ == "__main__":
    process_and_clean_schedule() 