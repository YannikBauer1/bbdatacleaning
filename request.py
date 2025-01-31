import pandas as pd
import numpy as np
import json
import ast
import re
import time
from datetime import datetime

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

def createAthletes(df):
  for index, row in df.iterrows():
      print(index)
      person_name = row["competitors_name"].replace(",", "")
      country = row["country"]
      persons = supabase.table("person").select("*").or_(f"name.eq.{person_name},name_long.eq.{person_name}").execute().data
      persons = [person for person in persons if person["birthplace"] == country]
      category = supabase.table("category").select("*").eq("name", row["category"]).execute().data
      if len(category) == 0:
         print("Category not found")
         exit()
      if len(persons) == 0:
          createdPerson = supabase.table("person").insert({"name": person_name, "name_long": person_name, "birthplace": row["country"], "nationality": [row["country"]["country"]]}).execute()
          createdAthlete = supabase.table("athlete").insert({"name": person_name, "active": True, "category_id": category[0]["id"]}).execute()
          updatedPerson = supabase.table("person").update({"athlete_id": createdAthlete.data[0]["id"]}).eq("id", createdPerson.data[0]["id"]).execute()
          print(person_name)

def format_date(date_str):
    if pd.isna(date_str):
        return None
    try:
        return pd.to_datetime(date_str, format="%d.%m.%Y").isoformat()
    except ValueError:
        return pd.to_datetime(date_str).isoformat()

def createCompetition(df):
    def format_date2(date_str):
        return datetime.strptime(date_str, "%d.%m.%Y").date()

    for index, row in df.iterrows():
        name_key = row["name_key"]
        competitions = supabase.table("competition").select("*").eq("name_key", name_key).execute().data

        name = name_key.replace('_', ' ').title()
        start_date = format_date(row["start_date"])
        end_date = format_date(row["end_date"])
        if pd.notna(row["promoter_website"]):
            socials = {"website": row["promoter_website"]}
        else:
            socials = {}
        if pd.notna(row["promoter"]):
            promoter = row["promoter"]
        else:
            promoter = ""
        if pd.notna(row["location"]):
            location = row["location"]
        else:
            location = ""

        if (len(competitions) == 0):
            supabase.table("competition").insert({"name_key": name_key, "name_short": name, "name": name, "organization": row["comp_type"], "socials": socials}).execute()
            print(name_key, " inserted Competition")
        
        competition = supabase.table("competition").select("*").eq("name_key", name_key).execute().data[0]
        events = supabase.table("event").select("*").eq("competition_id", competition["id"]).eq("year", row["year"]).execute().data

        fetchedIdentifieres = [
            [event["year"], format_date(event["start_date"]), format_date(event["end_date"])]
            for event in events ]
        identifier = [row["year"], start_date, end_date]

        if not identifier in fetchedIdentifieres:
            if len(events) == 0:
                newEvent = supabase.table("event").insert({"location": location, "start_date": start_date ,"end_date":end_date, "promoter": promoter, "competition_id": competition["id"], "year": row["year"]}).execute()
                print(name_key, " inserted first Event")
            elif len(events) == 1:
                supabase.table("event").update({"edition": 1}).eq("id", events[0]["id"]).execute()
                newEvent = supabase.table("event").insert({"edition": 2, "location": location, "start_date": start_date ,"end_date":end_date, "promoter": promoter, "competition_id": competition["id"], "year": row["year"]}).execute()
                print(name_key, " inserted second Event & updated editition")
            else:
                newEvent = supabase.table("event").insert({"edition": len(events) + 1, "location": location, "start_date": start_date ,"end_date":end_date, "promoter": promoter, "competition_id": competition["id"], "year": row["year"]}).execute()
                print(name_key, " inserted next Event")
            for division in row["divisions"]:
                category = supabase.table("category").select("*").eq("name", division).execute().data[0]
                supabase.table("division").insert({"event_id": newEvent["id"], "category_id": category["id"]}).execute()
                print(name_key, " inserted Division ", division)

def createResults(df):
    #for index, row in df.iterrows():
    for index, row in df.iloc[1900:].iterrows():
        print(index)
        #time.sleep(1)

        competition = row["competition"].replace('-', ' ').title()
        
        category = supabase.table("category").select("*").eq("name", row["category"]).execute().data
        competitionEvent = supabase.table("competitionEvent").select("*").or_(f"name.eq.{competition},name_key.eq.{competition}").execute().data
        #print(row)
        #print(competitionEvent)
        eventCategories = supabase.table("eventCategory").select("*").eq("competitionEvent_id", competitionEvent[0]["id"]).eq("category_id", category[0]["id"]).execute().data

        if len(eventCategories) == 0:
            createdEventCategory = supabase.table("eventCategory").insert({"competitionEvent_id": competitionEvent[0]["id"], "category_id": category[0]["id"]}).execute()
            eventCategory_id = createdEventCategory.data[0]["id"]
            print(row["category"])
        else:
            eventCategory_id = eventCategories[0]["id"]

        person_name = row["competitors_name"].replace(",", "")
        country = row["country"]
        persons = supabase.table("person").select("*").or_(f"name.eq.{person_name},name_long.eq.{person_name}").execute().data
        persons = [person for person in persons if person["birthplace"] == country]
        athlete_id = persons[0]["athlete_id"]

        results = supabase.table("result").select("*").eq("eventCategory_id", eventCategory_id).eq("athlete_id", athlete_id).execute().data

        if len(results) == 0:
            createdResult = supabase.table("result").insert({
                "eventCategory_id": eventCategory_id, 
                "athlete_id": athlete_id, 
                "prejudging": int(float(row["judging"])) if pd.notna(row["judging"]) else None, 
                "finals": int(float(row["finals"])) if pd.notna(row["finals"]) else None, 
                "total": int(float(row["total"])) if pd.notna(row["total"]) else None, 
                "place": int(float(row["place"])) if pd.notna(row["place"]) else None
            }).execute()
            print(person_name)

def deleteEventsForYear(year):
    limit = 1000
    offset = 0
    while True:
        events = supabase.table("event").select("id").eq("year", year).range(offset, offset + limit - 1).execute().data
        if not events:
            break
        for event in events:
            supabase.table("event").delete().eq("id", event["id"]).execute()
            print(f"Deleted event {event['id']} for year {year}")
        offset += limit
    print(f"Done deleting events for year {year}")
#deleteEventsForYear(2025)

#df = pd.read_csv('data_clean/2024/tables_2.csv')
#df['country'] = df['country'].apply(ast.literal_eval)

df = pd.read_csv('data_clean/sidebar/2025.csv')
df['location'] = df['location'].apply(ast.literal_eval)
df['divisions'] = df['divisions'].apply(ast.literal_eval)

#df = pd.read_csv('data_clean/2024/tables_1.csv')
#df['country'] = df['country'].apply(ast.literal_eval)

#print(df.shape)
#print(df.dtypes)    

#createAthletes(df)
createCompetition(df)
#createResults(df)


supabase.auth.sign_out()
