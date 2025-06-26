from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import re
from datetime import datetime

def get_full_schedule_df(soup):

    table_comp_names = ['men-open-bodybuilding','men-212-bodybuilding', 'men-classic-physique', 
                    'men-physique', 'men-wheelchair', 'women-bodybuilding', 'women-fitness', 
                    'women-figure', 'women-bikini', 'women-physique', 'women-wellness']
    
    comp_types = ["Men\'s Bodybuilding", "Men\'s 212 Bodybuilding", "Men\'s Classic Physique", 
                "Men\'s Physique", "Men\'s Wheelchair", "Women\'s Bodybuilding", 
                "Women\'s Fitness", "Women\'s Figure", "Women\'s Bikini", "Women\'s Physique",
                "Women\'s Wellness"]
    
    full_schedule_df = pd.DataFrame()
    comp_data_list = []

    def clean_competition_name(name):
        if not name:
            return name
        
        # Clean specific cases
        if "2025 MEXICO GRAND BATTLE PRO/AM2025 TOKYO PRO" in name:
            name = "2025 MEXICO GRAND BATTLE PRO/AM"
        elif "2025 OLYMPIAQ" in name:
            name = "2025 OLYMPIA"
        
        return name.strip()

    for i in range(len(comp_types)):
        tab_content_specific_table = soup.find_all('table', id = f'tablepress-2024-{table_comp_names[i]}')[0]

        table_body = tab_content_specific_table.find_all('tbody')[0]

        for row in table_body.find_all('tr'):
            columns = row.find_all("td")
                
            # Get competition name and subtype
            competition_name = None
            comp_url = None
            competition_subtype = None
            first_column = columns[0]
            
            # First get the URL if it exists
            if first_column.find('a') is not None:
                a_tag = first_column.find('a')
                comp_url = a_tag['href']
                
                # Check if there's a <div> inside the <a> tag
                if a_tag.find('div') is not None:
                    # Get text before the <div> inside <a> tag
                    text_parts = []
                    for content in a_tag.contents:
                        if content.name == 'div':
                            break
                        if isinstance(content, str):
                            text_parts.append(content.strip())
                    competition_name = ' '.join(text_parts).strip()
                    
                    # Get subtype from <div> inside <a> tag
                    competition_subtype = a_tag.find('div').get_text(strip=True)
                else:
                    # No <div> inside <a> tag, get all text
                    competition_name = a_tag.get_text(strip=True)
            
            if competition_name and not competition_subtype:
                if first_column.find('div') is not None:
                    competition_subtype = first_column.find('div').get_text(strip=True)

            # If no name found yet, check for <div> outside <a> tag
            if not competition_name:
                # Get all text before the <div>
                text_parts = []
                for content in first_column.contents:
                    if content.name == 'div':
                        break
                    if isinstance(content, str):
                        text_parts.append(content.strip())
                competition_name = ' '.join(text_parts).strip()
                
                # Get subtype from <div> outside <a> tag
                if first_column.find('div') is not None:
                    competition_subtype = first_column.find('div').get_text(strip=True)
            
            # If still no name, try getting all text content
            if not competition_name:
                competition_name = first_column.get_text(strip=True)
                # Remove the subtype if it's at the end
                if first_column.find('div') is not None:
                    subtype_text = first_column.find('div').get_text(strip=True)
                    competition_name = competition_name.replace(subtype_text, '').strip()
            
            # Skip if we still don't have a competition name
            if not competition_name:
                continue
            
            # Clean the competition name
            competition_name = clean_competition_name(competition_name)
            
            # Get other columns
            date = columns[1].get_text(strip=True)
            location = columns[2].get_text(strip=True)
            promoter = columns[3].get_text(strip=True)

            # Create row with all data
            row_data = [
                competition_name,
                date,
                location,
                promoter,
                comp_url,
                competition_subtype
            ]
            
            # Print when processing the specific competitions
            if "OKLAHOMA SHOWDOWN" in competition_name or "RISING PHOENIX" in competition_name:
                print(f"Processing competition: {competition_name}")
                print(f"Date from website: '{date}'")
                print(f"Row data: {row_data}")
                print("---")
            
            if comp_types[i] == "Men\'s Wheelchair":
                print(row_data)
            comp_data_list.append(row_data)

        comp_types_df = pd.DataFrame(comp_data_list)
        comp_types_df.columns = ['competition', 'date', 'location', 'promoter', 'comp_url', 'competition_subtype']
        comp_types_df['competition_type'] = comp_types[i]

        full_schedule_df = pd.concat([full_schedule_df,comp_types_df])
        comp_data_list = []

    return(full_schedule_df.reset_index(drop = True))


def parse_html(url: str):
    """Parse html from url to access its elements
    Args:
        url (str): URL for the PRO schedule website
    """
    try:
        html = requests.get(url)
        full_html = html.text
        soup = BeautifulSoup(full_html, 'html.parser')
    except Exception as e:
        print(f"Error {e}")

    return(soup)

def parse_date_range(date_str):
    """
    Parse date string and return start_date and end_date.
    
    Args:
        date_str (str): Date string in various formats like "Oct 4", "Dec 6-7", "Feb 27 - Mar 2", "Sept 13"
    
    Returns:
        tuple: (start_date, end_date) where both are strings in YYYY-MM-DD format
    """
    if not date_str or pd.isna(date_str):
        return None, None
    
    date_str = str(date_str).strip()
    
    # Normalize "Sept" to "Sep" for consistency
    date_str = date_str.replace("Sept", "Sep")
    
    # Handle single date (e.g., "Oct 4", "Sep 13")
    if '-' not in date_str:
        try:
            # Add year 2025 if not present
            if '2025' not in date_str and '2024' not in date_str:
                date_str = f"2025 {date_str}"
            parsed_date = datetime.strptime(date_str, "%Y %b %d")
            return parsed_date.strftime("%Y-%m-%d"), None
        except ValueError:
            return None, None
    
    # Handle date ranges
    # Pattern for same month ranges (e.g., "Dec 6-7")
    same_month_pattern = r'(\w{3})\s+(\d{1,2})-(\d{1,2})'
    same_month_match = re.match(same_month_pattern, date_str)
    
    if same_month_match:
        month, start_day, end_day = same_month_match.groups()
        year = "2025"  # Default to 2025
        if "2024" in date_str:
            year = "2024"
        
        try:
            start_date = datetime.strptime(f"{year} {month} {start_day}", "%Y %b %d")
            end_date = datetime.strptime(f"{year} {month} {end_day}", "%Y %b %d")
            return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        except ValueError:
            return None, None
    
    # Pattern for cross-month ranges (e.g., "Feb 27 - Mar 2")
    cross_month_pattern = r'(\w{3})\s+(\d{1,2})\s*-\s*(\w{3})\s+(\d{1,2})'
    cross_month_match = re.match(cross_month_pattern, date_str)
    
    if cross_month_match:
        start_month, start_day, end_month, end_day = cross_month_match.groups()
        year = "2025"  # Default to 2025
        if "2024" in date_str:
            year = "2024"
        
        try:
            start_date = datetime.strptime(f"{year} {start_month} {start_day}", "%Y %b %d")
            end_date = datetime.strptime(f"{year} {end_month} {end_day}", "%Y %b %d")
            return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        except ValueError:
            return None, None
    
    # If no pattern matches, return None
    return None, None

def parse_location(location_str):
    """
    Parse location string into city, state, country.
    Handles formats like:
    - "Las Vegas, NV"
    - "Toronto, Canada"
    - "Johannesburg, South Africa"
    - "South Korea"
    - "Anaheim, CA"
    - "Palmerston, New Zealand"
    - "Italy"
    Returns (city, state, country)
    """
    if not location_str or pd.isna(location_str):
        return None, None, None
    
    location_str = str(location_str).strip()
    
    # Remove quotes if present
    location_str = location_str.replace('"', '')
    
    # Split by comma
    parts = [p.strip() for p in location_str.split(',')]
    
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    elif len(parts) == 2:
        city, state_or_country = parts
        if len(state_or_country) == 2 and state_or_country.isupper():
            return city, state_or_country, 'United States'  # Use full country name
        else:
            return city, None, state_or_country
    elif len(parts) == 1:
        return None, None, parts[0]
    else:
        return None, None, location_str

def main(url: str):
    soup = parse_html(url = url)

    full_schedule_df = get_full_schedule_df(soup= soup)
    print(full_schedule_df)

    # Group contests by name and aggregate the data
    grouped_df = full_schedule_df.groupby('competition').agg({
        'date': 'first',
        'location': 'first', 
        'promoter': 'first',
        'comp_url': 'first',
        'competition_type': lambda x: list(set(x)),  # Remove duplicates
        'competition_subtype': lambda x: list(set([item for item in x if item is not None]))  # Remove duplicates and None values
    }).reset_index()
    
    # Convert lists to strings for CSV compatibility
    grouped_df['competition_type'] = grouped_df['competition_type'].apply(lambda x: ', '.join(x))
    grouped_df['competition_subtype'] = grouped_df['competition_subtype'].apply(lambda x: ', '.join(x) if x else '')
    
    # Parse dates into start_date and end_date
    date_parsing_results = grouped_df['date'].apply(parse_date_range)
    grouped_df['Start Date'] = [result[0] for result in date_parsing_results]
    grouped_df['End Date'] = [result[1] for result in date_parsing_results]
    
    # Parse location into city, state, country
    location_results = grouped_df['location'].apply(parse_location)
    grouped_df['Location City'] = [result[0] for result in location_results]
    grouped_df['Location State'] = [result[1] for result in location_results]
    grouped_df['Location Country'] = [result[2] for result in location_results]
    
    # Remove the original date and location columns
    grouped_df = grouped_df.drop(['date', 'location'], axis=1)
    
    # Rename columns to more descriptive names
    grouped_df = grouped_df.rename(columns={
        'competition': 'Competition Name',
        'promoter': 'Promoter Name',
        'competition_type': 'Division',
        'competition_subtype': 'Division Type',
        'comp_url': 'Competition URL'
    })

    print("Grouped schedule:")
    print(grouped_df)

    # Save the grouped schedule to a CSV file
    output_file = os.path.join('data', 'schedule.csv')
    grouped_df.to_csv(output_file, index=False)
    print(f"Grouped schedule saved to {output_file}")

    # This data should eventually be compared with what is already on supabase.

    return(grouped_df)


if __name__ == '__main__':
    url = 'https://www.ifbbpro.com/schedule/'
    main(url = url)