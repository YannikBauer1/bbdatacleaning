import pandas as pd
import numpy as np
import json
import ast


import os
from supabase import create_client, Client

os.environ["SUPABASE_URL"] = "https://qesnrciwmhxfhdaojwwo.supabase.co"
os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFlc25yY2l3bWh4ZmhkYW9qd3dvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTYzMjg4NjIsImV4cCI6MjAzMTkwNDg2Mn0.kMcvSSoOhK_Nfl6J02dSTktMdj7jL6MTZygKfBfCeOM"

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

#persons = supabase.table("person").select("*").execute().data
#athetes = supabase.table("athlete").select("*").execute().data

df = pd.read_csv('data_cleaned.csv')

# return tme the data types of each column
print(df.dtypes)

# change the type of the column country to be an object
df['country'] = df['country'].apply(ast.literal_eval)

# pritn me the column country
print(df['country'])

def createAthletes():
  for index, row in df.iterrows():
      person_name = row["competitors_name"]

      persons = supabase.table("person").select("*").execute().data
      existing_persons = set([person["name"] for person in persons]) | set([person["name_long"] for person in persons])
      if person_name not in existing_persons:
          createdPerson = supabase.table("person").insert({"name": person_name, "name_long": person_name, "birthplace": row["country"], "nationality": [row["country"]["country"]]}).execute()
          createdAthlete = supabase.table("athlete").insert({"name": person_name, "active": True, "person_id": createdPerson.data[0]["id"]}).execute()
          updatedPerson = supabase.table("person").update({"athlete_id": createdAthlete.data[0]["id"]}).eq("id", createdPerson.data[0]["id"]).execute()

createAthletes()





#response = (
#    supabase.table("person")
#    .insert({"name": "Denmark"})
#    .execute()
#)

