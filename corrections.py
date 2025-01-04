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
changePersonsId()

response = supabase.auth.sign_out()