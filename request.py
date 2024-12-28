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

def createCompetition(df):
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

df = pd.read_csv('data_clean/2024/tables_2.csv')

# change the type of the column country to be an object
df['country'] = df['country'].apply(ast.literal_eval)

# print the number of rows in the df
print(df.shape)


#createAthletes(df)
