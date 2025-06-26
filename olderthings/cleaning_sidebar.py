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
    date_obj = pd.to_datetime(date_str + " 2025", format="%B %d %Y", errors="coerce")
    if pd.isnull(date_obj):
        return None
    return date_obj.strftime("%d.%m.%Y")

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

def parsePromoter(promoter):
    return re.sub(r'\s*\(.*?\)\s*', '', promoter).strip()

def groupByUrl(df):
    grouped = df.groupby('url').agg({
        'start_date': 'first',
        'end_date': 'first',
        'location': 'first',
        'comp_type': 'first',
        'divisions': lambda x: list(x),
        'division_type': 'first',
        'promoter': 'first',
        'promoter_website': 'first'
    }).reset_index()
    return grouped

def generalCleaning(df):
    print('-------------General Cleaning--------------')

    # remove fist column
    #df = df.drop(columns=['Unnamed: 0'])
    df = df[~(df['division_type'] == "Masters")]
    df = df[~(df['division_type'] == "Natural")]
    df = df[~(df['division_type'] == "Natural and Masters")]

    df["start_date"] = df["start_date"].astype(str).apply(parse_dates)
    df["end_date"] = df["end_date"].astype(str).apply(parse_dates)
    df["end_date"] = df["end_date"].fillna(df["start_date"])

    df["year"] = 2025

    df["eventName"] = df["url"].apply(lambda x: x.split('/')[-2]).str.replace('-', '_').str.lower()
    df["name"] = df["eventName"].str.replace(r'2025_', '', regex=True).str.lower().str.strip()
    df["name_key"] = df["name"].apply(parse_name)

    df['location'] = df['location'].astype(str).apply(parse_country)
    df['promoter'] = df['promoter'].apply(parsePromoter)

    #def safe_literal_eval(val):
    #    try:
    #        return ast.literal_eval(val)
    #    except (ValueError, SyntaxError):
    #        return val
    #df["divisions"] = df["divisions"].apply(lambda x: safe_literal_eval(x) if pd.notna(x).all() else [])

    #print(df)
    return df

def checkCompetitionNames(df):
    with open('competitionNameKeys.json', 'r') as f:
        competitionNameKeys = json.load(f)
    for index, row in df.iterrows():
        name = row["name"]
        found = False
        for key, values in competitionNameKeys.items():
            if name in values:
                found = True
                break
        if not found:
            print(name)
    print("Done checking competition names")

def orderCompetitionNameKeys():
    with open('competitionNameKeys.json', 'r') as f:
        competitionNameKeys = json.load(f)
    orderedKeys = {key: sorted(values) for key, values in sorted(competitionNameKeys.items())}
    with open("competitionNameKeys.json", 'w') as f:
        json.dump(orderedKeys, f, indent=4)
    print(f"Ordered competitionNameKeys")


#df = pd.read_csv('data_raw/sidebar/2025.csv')

#showStat(df)

#df = groupByUrl(df)

#df = generalCleaning(df)

#df.to_csv('data_clean/sidebar/2025.csv', index=False)
