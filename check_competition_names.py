import pandas as pd
import json

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

def find_missing_name_keys():
    # Read the CSV file
    df = pd.read_csv('data_clean/sidebar/2025_Schedule.csv')
    
    # Read the competition name keys
    with open('competitionNameKeys.json', 'r') as f:
        competitionNameKeys = json.load(f)
    
    # Find competitions without name keys
    missing_keys = []
    for index, row in df.iterrows():
        name = row["name"]
        if pd.isna(row["name_key"]) or row["name_key"] == "":
            found = False
            for key, values in competitionNameKeys.items():
                if name in values:
                    found = True
                    break
            if not found:
                missing_keys.append({
                    'name': name,
                    'eventName': row['eventName'],
                    'url': row['url'],
                    'start_date': row['start_date'],
                    'location': row['location']
                })
    
    # Print the results
    print("\nCompetitions without name keys:")
    print("--------------------------------")
    for comp in missing_keys:
        print(f"Name: {comp['name']}")
        print(f"Event Name: {comp['eventName']}")
        print(f"URL: {comp['url']}")
        print(f"Date: {comp['start_date']}")
        print(f"Location: {comp['location']}")
        print("--------------------------------")
    
    print(f"\nTotal competitions without name keys: {len(missing_keys)}")

if __name__ == "__main__":
    # Read the CSV file
    df = pd.read_csv('data_clean/sidebar/2025_Schedule.csv')
    
    # Check competition names
    checkCompetitionNames(df)
    
    # Order competition name keys
    orderCompetitionNameKeys()
    
    # Find missing name keys
    find_missing_name_keys() 