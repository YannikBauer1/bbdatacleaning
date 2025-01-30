import pandas as pd
import numpy as np
import json
import ast
import re
import time

import os
from supabase import create_client, Client

os.environ["SUPABASE_URL"] = "https://qesnrciwmhxfhdaojwwo.supabase.co"
os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFlc25yY2l3bWh4ZmhkYW9qd3dvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTYzMjg4NjIsImV4cCI6MjAzMTkwNDg2Mn0.kMcvSSoOhK_Nfl6J02dSTktMdj7jL6MTZygKfBfCeOM"

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

supabase.auth.sign_in_with_password(
    {"email": "yannikbauer.1@gmail.com", "password": "Weisnet1"}
)

def changePersonsId():
    limit = 1000  # Number of entries to fetch per batch
    offset = 0
    while True:
        persons = supabase.table("person").select("*").range(offset, offset + limit - 1).execute().data
        if not persons:
            break
        for person in persons:
            athlete_id = person.get("athlete_id")
            if athlete_id:
                supabase.table("athlete").update({"person_id": person["id"]}).eq("id", athlete_id).execute()
                print(f"Updated athlete {athlete_id} with person_id {person['id']}")
        offset += limit

# Call the function to update the athlete table
#changePersonsId()

def addSex():
    limit = 1000  # Number of entries to fetch per batch
    offset = 0
    while True:
        persons = supabase.table("person") \
            .select("*, athlete(*, result(*, eventCategory(*, category(name))))") \
            .range(offset, offset + limit - 1) \
            .execute().data
        if not persons:
            break
        for person in persons:
            category = person.get('athlete', [{}])[0].get('result', [{}])[0].get('eventCategory', [{}]).get('category', {}).get('name')
            if "women" in category.lower():
                supabase.table("person").update({"sex": "woman"}).eq("id", person["id"]).execute()
                print(f"Updated person {person['id']} in category {category} with sex woman")
            else:
                supabase.table("person").update({"sex": "man"}).eq("id", person["id"]).execute()
                print(f"Updated person {person['id']} in category {category} with sex man")
        offset += limit

#addSex()

def changeCompetiitionsNameKey():
    limit = 1000  # Number of entries to fetch per batch
    offset = 0
    while True:
        competitions = supabase.table("competition") \
            .select("*") \
            .range(offset, offset + limit - 1) \
            .execute().data
        if not competitions:
            break
        for index, competition in enumerate(competitions):
            print(index)
            name = competition.get("name_key")
            supabase.table("competition").update({"name_key": name.lower().replace(" ", "_")}).eq("id", competition["id"]).execute()
        offset += limit

#changeCompetiitionsNameKey()

def addPersonsNameKey():
    limit = 1000  # Number of entries to fetch per batch
    offset = 0
    while True:
        persons = supabase.table("person") \
            .select("*") \
            .range(offset, offset + limit - 1) \
            .execute().data
        if not persons:
            break
        for index, person in enumerate(persons):
            name = person.get("name_short")
            if (person.get("name_key") == None):
                name_key = re.sub(r'[^a-z_]', '', name.lower().replace(" ", "_"))
                print(index, name_key)
                supabase.table("person").update({"name_key": name_key}).eq("id", person["id"]).execute()
        offset += limit

#addPersonsNameKey()

def correctFileNames():
    folder_path = "personsToAdd"
    for filename in os.listdir(folder_path):
        new_filename = filename.replace("_removebg_preview", "")
        new_filename = re.sub(r'[^a-z_]', '', new_filename.lower().replace(" ", "_").replace("-", "_"))
        if not new_filename.endswith(".png"):
            new_filename += ".png"
        elif new_filename.endswith("png"):
            new_filename = new_filename[:-3] + ".png"
        new_filename = new_filename.replace("png", "")
        new_filename = new_filename + "png"
        os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))
        print(f"Renamed {filename} to {new_filename}")

#correctFileNames()

def addPersonsImageUrl():
    base_url = "https://qesnrciwmhxfhdaojwwo.supabase.co/storage/v1/object/public/logos/persons/"
    folder_path = "images/persons"
    for filename in os.listdir(folder_path):
        name_key = filename.split(".")[0]
        person = supabase.table("person").select("*").eq("name_key", name_key).execute().data
        if len(person) == 0:
            print(f"Person {filename} not found!!!!")
        elif not person[0].get("image_url"):
            image_url = base_url + filename
            supabase.table("person").update({"image_url": image_url}).eq("name_key", name_key).execute()
            print(f"Updated person {name_key} with image_url {image_url}")

#addPersonsImageUrl()

def findDuplicatePersons():
    limit = 1000  # Number of entries to fetch per batch
    offset = 0
    persons = []
    
    while True:
        batch = supabase.table("person").select("id, name_short, name, birthplace").range(offset, offset + limit - 1).execute().data
        if not batch:
            break
        persons.extend(batch)
        offset += limit

    duplicates = []
    seen = {}

    for person in persons:
        name_short = person.get("name_short", "").lower().replace(" ", "")
        name = person.get("name", "").lower().replace(" ", "")
        person['main'] = False
        
        if name_short in seen:
            seen[name_short].append(person)
        else:
            seen[name_short] = [person]
        
        if name != name_short:
            if name in seen:
                seen[name].append(person)
            else:
                seen[name] = [person]

    for key, value in seen.items():
        if len(value) > 1:
            duplicates.append(value)

    with open("duplicate_persons.json", "w") as f:
        json.dump(duplicates, f, indent=4)

    print(f"Found {len(duplicates)} sets of duplicates. Saved to duplicate_persons.json.")

#findDuplicatePersons()

def mergeDuplicatePersons(mainPersonId, personIdsToDelete):
    mainPerson = supabase.table("person").select("*").eq("id", mainPersonId).execute().data[0]
    mainAthlete = supabase.table("athlete").select("*").eq("person_id", mainPersonId).execute().data[0]
    for personId in personIdsToDelete:
        athleteToDelete = supabase.table("athlete").select("*").eq("person_id", personId).execute().data[0]
        resultsFromAthlete = supabase.table("result").select("*").eq("athlete_id", athleteToDelete["id"]).execute().data
        for result in resultsFromAthlete:
            supabase.table("result").update({"athlete_id": mainAthlete["id"]}).eq("id", result["id"]).execute()
            print(f"Updated result {result['id']} with athlete_id {mainAthlete['id']}")
        supabase.table("athlete").delete().eq("id", athleteToDelete["id"]).execute()
        supabase.table("person").delete().eq("id", personId).execute()
        print(f"Merged person {personId} into {mainPersonId} and deleted {personId}")

#mergeDuplicatePersons("3ad7681d-e75d-476a-a6a7-12926edfb488", ["1abecbfd-856a-4d56-b2cc-a36bdd38a8d4"])

def mergeAllDuplicatePersons():
    with open("duplicate_persons.json", "r") as f:
        duplicates = json.load(f)
    
    for duplicate in duplicates:
        mainPerson = next((dup for dup in duplicate if dup["main"]), None)
        if (mainPerson):
            indexOfMainPerson = next((index for index, dup in enumerate(duplicate) if dup["id"] == mainPerson["id"]), -1)
            personIdsToDelete = [person["id"] for index, person in enumerate(duplicate) if index != indexOfMainPerson]
            mergeDuplicatePersons(mainPerson["id"], personIdsToDelete)
        else:
            comparisionArray = []
            for person in duplicate:
                personData = supabase.table("person").select("*, athlete(result!inner(eventCategory(category(name))))").eq("id", person["id"]).execute().data[0]
                categories = [result["eventCategory"]["category"]["name"] for athlete in personData["athlete"] for result in athlete["result"]]
                categoriesUnique = list(set(categories))
                person["categories"] = categoriesUnique
                if person.get("birthplace", {}).get("country") == "USA":
                    person["birthplace"]["country"] = "United States"
                comparisionArray.append(person)
            
            all_categories = [set(person["categories"]) for person in comparisionArray]
            if all(not cat1 & cat2 for i, cat1 in enumerate(all_categories) for cat2 in all_categories[i+1:]):
                #print("No common categories: ", all_categories) 
                continue
            name_shorts = [person.get("name_short") for person in comparisionArray]
            if (len(set(name_shorts)) > 1):
                #print("Different name_shorts: ", comparisionArray)
                continue
            countries = [person.get("birthplace", {}).get("country") for person in comparisionArray]
            cities = [person.get("birthplace", {}).get("city") for person in comparisionArray if person.get("birthplace", {}).get("city")]
            states = [person.get("birthplace", {}).get("state") for person in comparisionArray if person.get("birthplace", {}).get("state")]
            if len(set(countries)) > 1 or len(set(cities)) > 1 or len(set(states)) > 1:
                #print("Different countries: ", comparisionArray)
                continue
        
            def birthplace_data_count(person):
                birthplace = person.get("birthplace", {})
                return sum(1 for key in ["country", "city", "state"] if birthplace.get(key))

            newMainPerson = max(comparisionArray, key=birthplace_data_count)
            indexOfMainPerson = next((index for index, dup in enumerate(comparisionArray) if dup["id"] == newMainPerson["id"]), -1)
            personIdsToDelete = [person["id"] for index, person in enumerate(comparisionArray) if index != indexOfMainPerson]
            mergeDuplicatePersons(newMainPerson["id"], personIdsToDelete)
            
#mergeAllDuplicatePersons()

def findMixedPersons():
    limit = 1000  # Number of entries to fetch per batch
    offset = 0
    persons = []
    
    while True:
        batch = supabase.table("person").select("id, name_short, name, birthplace").range(offset, offset + limit - 1).execute().data
        if not batch:
            break
        persons.extend(batch)
        offset += limit

    mixed_persons = []

    for person in persons:
        personData = supabase.table("person").select("*, athlete(result!inner(eventCategory(category(name))))").eq("id", person["id"]).execute().data[0]
        categories = [result["eventCategory"]["category"]["name"] for athlete in personData["athlete"] for result in athlete["result"]]
        categoriesUnique = list(set(categories))

        has_mens_category = any("Men's" in category for category in categoriesUnique)
        has_womens_category = any("Women's" in category for category in categoriesUnique)
        
        if has_mens_category and has_womens_category:
            mixed_persons.append(person)

    with open("mixed_persons.json", "w") as f:
        json.dump(mixed_persons, f, indent=4)
    print(f"Found {len(mixed_persons)} persons with both Men's and Women's categories. Saved to mixed_persons.json.")
        
#findMixedPersons()

def showProblems():
    competition = supabase.table("competition").select("competitionEvent!inner(eventCategory!inner(id, category(name)))").eq("name_key", "dubai_pro").execute().data[0]
    for eventCategory in competition["competitionEvent"][0]["eventCategory"]:
        print(eventCategory)
    
    #classicId = next((event["id"] for event in competition["competitionEvent"][0]["eventCategory"] if event["category"]["name"] == "Men's Classic Physique"), None)
    #bikiniId = next((event["id"] for event in competition["competitionEvent"][0]["eventCategory"] if event["category"]["name"] == "Women's Bikini"), None)

    #print(classicId, bikiniId)

    #with open("mixed_persons.json", "r") as f:
    #    mixed_persons = json.load(f)
    #for person in mixed_persons:
    #    athlete = supabase.table("athlete").select("result!inner(id, eventCategory(id))").eq("person_id", person["id"]).execute().data[0]
    #    for result in athlete["result"]:
    #        if(result["eventCategory"]["id"] == classicId):
    #            #supabase.table("result").update({"eventCategory_id": bikiniId}).eq("id", result["id"]).execute()
    #            print(f"Updated result {result['id']}")

#showProblems()

def anotherProblemSolver():
    classicId = "7ded0c26-8cd4-427c-9402-bd20d26725e5"
    bikiniId = "0fcd0098-e518-4e84-a07d-e96c64f2685b"
    results = supabase.table("result").select("*").eq("eventCategory_id", classicId).execute().data
    for result in results:
        supabase.table("result").update({"eventCategory_id": bikiniId}).eq("id", result["id"]).execute()
        print(f"Updated result {result['id']}")
    supabase.table("eventCategory").delete().eq("id", classicId).execute()

#anotherProblemSolver()

def checkCompetitionsInNameKeys():
    with open('/Users/yannik/GitHub/bbdatacleaning/competitionNameKeys.json', 'r') as f:
        competitionNameKeys = json.load(f)

    limit = 1000 
    offset = 0
    while True:
        competitions = supabase.table("competition").select("name_key").range(offset, offset + limit - 1).execute().data
        if not competitions:
            break
        for competition in competitions:
            name_key = competition["name_key"]
            found = False
            for key, values in competitionNameKeys.items():
                if name_key in values:
                    found = True
                    break
            if not found:
                print(f"Competition name_key not found in competitionNameKeys: {name_key}")
        offset += limit
    print("Done")

#checkCompetitionsInNameKeys()

def updateCompetitionNameKeys():
    with open('/Users/yannik/GitHub/bbdatacleaning/competitionNameKeys.json', 'r') as f:
        competitionNameKeys = json.load(f)

    limit = 1000
    offset = 0
    while True:
        competitions = supabase.table("competition").select("id, name_key").range(offset, offset + limit - 1).execute().data
        if not competitions:
            break
        for competition in competitions:
            name_key = competition["name_key"]
            if name_key not in competitionNameKeys:
                found = False
                for key, values in competitionNameKeys.items():
                    if name_key in values:
                        competitionsWithKey = supabase.table("competition").select("*").eq("name_key", key).execute().data
                        if len(competitionsWithKey) == 1:
                            events = supabase.table("event").select("*").eq("competition_id", competitionsWithKey[0]["id"]).execute().data
                            if len(events) == 1:
                                supabase.table("event").update({"edition": 1}).eq("id", events[0]["id"]).execute()
                                eventsFromCompetition = supabase.table("event").select("*").eq("competition_id", competition["id"]).execute().data
                                edition = 2
                                for event in eventsFromCompetition:
                                    supabase.table("event").update({"competition_id": competitionsWithKey[0]["id"], "edition": edition}).eq("id", event["id"]).execute()
                                    edition =+ 1
                                supabase.table("competition").delete().eq("id", competition["id"]).execute()
                                print(f"Merged competition {name_key} into {key}")
                            else:
                                eventsFromCompetition = supabase.table("event").select("*").eq("competition_id", competition["id"]).execute().data
                                edition = max([event["edition"] for event in events]) + 1
                                for event in eventsFromCompetition:
                                    supabase.table("event").update({"competition_id": competitionsWithKey[0]["id"], "edition": edition}).eq("id", event["id"]).execute()
                                    edition =+ 1
                                supabase.table("competition").delete().eq("id", competition["id"]).execute()
                                print(f"Merged competition {name_key} into {key}")
                        else:
                            supabase.table("competition").update({"name_key": key}).eq("id", competition["id"]).execute()
                            print(f"Updated competition {competition['id']} name_key from {name_key} to {key}")
                        found = True
                        break
                if not found:
                    print(f"Competition name_key not found in competitionNameKeys: {name_key}")
        offset += limit
    print("Done")

#updateCompetitionNameKeys()

def cleanEventPromoters():
    limit = 1000
    offset = 0
    while True:
        events = supabase.table("event").select("id, promoter").range(offset, offset + limit - 1).execute().data
        if not events:
            break
        for event in events:
            promoter = event["promoter"]
            cleaned_promoter = re.sub(r'\s*\(.*?\)\s*', '', promoter).strip()
            if promoter != cleaned_promoter:
                supabase.table("event").update({"promoter": cleaned_promoter}).eq("id", event["id"]).execute()
                print(f"Updated event {event['id']} promoter from '{promoter}' to '{cleaned_promoter}'")
        offset += limit
    print("Done")

#cleanEventPromoters()

def updateNationality():
    limit = 1000
    offset = 0
    while True:
        persons = supabase.table("person").select("id, nationality").range(offset, offset + limit - 1).execute().data
        if not persons:
            break
        for person in persons:
            nationality = person["nationality"]
            if "USA" in nationality:
                updated_nationality = ["United States" if country == "USA" else country for country in nationality]
                supabase.table("person").update({"nationality": updated_nationality}).eq("id", person["id"]).execute()
                print(f"Updated person {person['id']} nationality from {nationality} to {updated_nationality}")
        offset += limit
    print("Done")

updateNationality()

supabase.auth.sign_out()
