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

response = supabase.auth.sign_in_with_password(
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

addPersonsImageUrl()

response = supabase.auth.sign_out()


