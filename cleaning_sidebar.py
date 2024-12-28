import pandas as pd
import numpy as np
import re
import ast

def showStat(df):
    print('-------------Dataframe Stats--------------')
    print(df.shape) # return me how many rows and columns 
    print(df.dtypes) # return me the data types of each column
    print("\n")
    print("\n")

def parse_dates(date_str):
    date_obj = pd.to_datetime(date_str + " 2024", format="%B %d %Y", errors="coerce")
    if pd.isnull(date_obj):
        return None
    return date_obj.strftime("%d.%m.%Y")

def parse_country(entry):
    if pd.isna(entry):
        return {"city": "", "state": "", "country": ""}
    # Use regular expressions to split the entry into city, state, and country
    parts = entry.split(',')
    city = parts[0].strip() if parts[0].strip() else ""
    state = ""
    country = ""
    if len(parts) == 2:
        if "Florida" in parts[1] or "florida" in parts[1]:
            state = "FL"
            country = 'United States'
        elif "Texas" in parts[1] or "texas" in parts[1]:
            state = "TX"
            country = 'United States'
        elif "Tennessee" in parts[1] or "tennessee" in parts[1]:
            state = "TN"
            country = 'United States'
        elif "California" in parts[1] or "california" in parts[1]:
            state = "CA"
            country = 'United States'
        elif "New York" in parts[1] or "new york" in parts[1]:
            state = "NY"
            country = 'United States'
        elif "Nevada" in parts[1] or "nevada" in parts[1]:
            state = "NV"
            country = 'United States'
        elif "Georgia" in parts[1] or "georgia" in parts[1]:
            state = "GA"
            country = 'United States'
        elif "Arizona" in parts[1] or "arizona" in parts[1]:
            state = "AZ"
            country = 'United States'
        elif "Virginia" in parts[1] or "virginia" in parts[1]:
            state = "VA"
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

def generalCleaning(df):
    print('-------------General Cleaning--------------')

    # remove fist column
    df = df.drop(columns=['Unnamed: 0'])

    # make start_date and end_date to date
    df["start_date"] = df["start_date"].astype(str).apply(parse_dates)
    df["end_date"] = df["end_date"].astype(str).apply(parse_dates)

    # set end_date to start_date when end_date is None
    df["end_date"] = df["end_date"].fillna(df["start_date"])

    # create a new column 'name' from the URL
    df["eventName"] = df["url"].apply(lambda x: x.split('/')[-2])
    df["eventName"] = df["eventName"].str.replace('-', ' ').str.title()

    # create a new column 'generalName' by removing "2024" and any trailing " 2" or similar
    df["name"] = df["eventName"].str.replace(r'2024', '', regex=True).str.strip()

    # Apply parse_country to the 'location' column
    df['location'] = df['location'].astype(str).apply(parse_country)

    # Handle NaN values in the 'divisions' column
    df["divisions"] = df["divisions"].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])

    # remove rows where devision_type is Masters
    df = df[~(df['division_type'] == "Masters")]


    print(df)
    return df

def generalCleaning2(df):
    print('-------------General Cleaning--------------')
    # remove rows that have no name in it ( false rows )
    #print(df['competitors_name'].isnull().sum())
    df = df.dropna(subset=['competitors_name'])

    df['judging'] = df['judging'].replace(['-'], np.nan)
    df['finals'] = df['finals'].replace(['-'], np.nan)
    df['total'] = df['total'].replace(['-'], np.nan)
    df['place'] = df['place'].replace(['-', 'NS', 'DQ'], np.nan)

    df['judging'] = pd.to_numeric(df['judging'], errors='coerce')
    df['finals'] = pd.to_numeric(df['finals'], errors='coerce')
    df['total'] = pd.to_numeric(df['total'], errors='coerce')

    df = df.rename(columns={'competition_type': 'category'})
    df['category'] = df['category'].apply(str)
    df['category'] = df['category'].str.upper()
    df['category'] = df['category'].str.replace(' - OPEN', '')
    df['category'] = df['category'].str.replace(r' . OPEN', '', regex=True)
    df['category'] = df['category'].replace('BIKINI', 'WOMEN\'S BIKINI') 
    df['category'] = df['category'].replace('CLASSIC PHYSIQUE', 'MEN\'S CLASSIC PHYSIQUE') 

    df = df[~df['category'].str.contains("MASTERS")] # Filter rows with "MASTERS"

    category_translation = {
        "MEN'S 212 BODYBUILDING": "Men's 212 Bodybuilding",
        "MEN'S BODYBUILDING": "Men's Bodybuilding",
        "MEN'S CLASSIC PHYSIQUE": "Men's Classic Physique",
        "MEN'S PHYSIQUE": "Men's Physique",
        "WOMEN'S BIKINI": "Women's Bikini",
        "WOMEN'S BODYBUILDING": "Women's Bodybuilding",
        "WOMEN'S FIGURE": "Women's Figure",
        "WOMEN'S FITNESS": "Women's Fitness",
        "WOMEN'S PHYSIQUE": "Women's Physique",
        "WOMEN'S WELLNESS": "Women's Wellness",
        "MEN'S WHEELCHAIR": "Men's Wheelchair",
        "MEN’S 212 BODYBUILDING": "Men's 212 Bodybuilding",
        "MEN’S BODYBUILDING": "Men's Bodybuilding",
        "MEN’S CLASSIC PHYSIQUE": "Men's Classic Physique",
        "MEN’S PHYSIQUE": "Men's Physique",
        "WOMEN’S BIKINI": "Women's Bikini",
        "WOMEN’S BODYBUILDING": "Women's Bodybuilding",
        "WOMEN’S FIGURE": "Women's Figure",
        "WOMEN’S FITNESS": "Women's Fitness",
        "WOMEN’S PHYSIQUE": "Women's Physique",
        "WOMEN’S WELLNESS": "Women's Wellness",
        "MEN’S WHEELCHAIR": "Men's Wheelchair"
    }
    df['category'] = df['category'].map(category_translation)
    #print(df['category'])

    # show me how many unique values are in the category column
    print("Unique categories Verify:")
    unique_categories = sorted(df['category'].unique())
    for category in unique_categories:
        print(category)
    print("\n")

    def parse_country(entry):
        # Use regular expressions to split the entry into city, state, and country
        match = re.match(r'^(.*?)(?:,([A-Z]{2}))?(?:,([^,]+))?$', entry)
        if match:
            city = match.group(1).strip() if match.group(1) else ""
            state = match.group(2).strip() if match.group(2) else ""
            country = match.group(3).strip() if match.group(3) else ""
        else:
            city = ""
            state = ""
            country = entry.strip()
        return {"city": city, "state": state, "country": country}
    df['country'] = df['country'].apply(parse_country)

    # print the columns country as a list
    #print(df_filtered['country'].tolist())
    print("\n")
    print("\n")
    return df


def verification(df):
    print('-------------Verification--------------')
    df['finals'] = np.where(df['finals'].isnull() & df['judging'].notnull(), 0, df['finals']) # Replace finals with 0 if it is nothing and juding is not nothing
    df['check'] = df['judging'] + df['finals'] == df['total'] # Check if judging + finals is equal to total
    print(df['check'].value_counts()) # how many falses are in check column

    # show me the rows that have false in the check column, show the columns judging, finals, total and competitors_name which have not nathing at the place column
    print("Rows with Check false and place not null:")
    print(df[(df['check'] == False) & (df['place'].notnull())][['judging', 'finals', 'total', 'place', 'competitors_name']])
    print("Rows with Check false:")
    print(df[df['check'] == False][['judging', 'finals', 'total', 'place', 'competitors_name']])

    indexes = df[(df['check'] == False) & (df['place'].notnull())].index
    print("Indexes of false rows:")
    print(indexes)
    print("")

    print("False rows with 4 rows before and 4 rows after:")
    for index in indexes:
        start = max(index - 4, 0)
        end = min(index + 5, len(df))
        print(index, start, end)
        print(df.loc[start:end][['judging', 'finals', 'total', 'place']])
        print("")

    print("\n")
    print("\n")


def corrections_2024_imgs_1(df):
    # replace of the row 645 the columsn finals with 0
    df.loc[645, 'finals'] = 0.0
    df.loc[3122, 'total'] = 39.0
    df.loc[3404, 'judging'] = 9.0
    df.loc[3689, 'total'] = 17.0

    #df['check'] = df['judging'] + df['finals'] == df['total']
    #print(df[(df['check'] == False) & (df['place'].notnull())][['judging', 'finals', 'total', 'place', 'competitors_name']])
    #print("")

    #df = df.drop(columns=['check'])   
    #print("\n")
    #print("\n")
    return df


df = pd.read_csv('data_raw/sidebar/2024.csv')
showStat(df)
df = generalCleaning(df)
#verification(df)
#df = corrections_2024_imgs_1(df)

df.to_csv('data_clean/sidebar/2024.csv', index=False)