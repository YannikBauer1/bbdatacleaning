import pandas as pd
import numpy as np

df = pd.read_csv('data.csv')

# return me how many rows and columns 
#print(df.shape)

# return me the data types of each column
print(df.dtypes)

# remove rows that have no name in it ( false rows )
#print(df['competitors_name'].isnull().sum())
#print("")
df = df.dropna(subset=['competitors_name'])

# in columns judging, finals, total, replace the value of - and NS and DQ with NaN
df['judging'] = df['judging'].replace(['-'], np.nan)
df['finals'] = df['finals'].replace(['-'], np.nan)
df['total'] = df['total'].replace(['-'], np.nan)
df['place'] = df['place'].replace(['-', 'NS', 'DQ'], np.nan)

# change the data type of the columns
df['judging'] = pd.to_numeric(df['judging'], errors='coerce')
df['finals'] = pd.to_numeric(df['finals'], errors='coerce')
df['total'] = pd.to_numeric(df['total'], errors='coerce')



# Replace finals with 0 if it is nothing and juding is not nothing
df['finals'] = np.where(df['finals'].isnull() & df['judging'].notnull(), 0, df['finals'])

# Check if judging + finals is equal to total
df['check'] = df['judging'] + df['finals'] == df['total']

# print how many falses are in the check column
#print(df['check'].value_counts())
#print("")

# show me the rows that have false in the check column, show the columns judging, finals, total and competitors_name which have not nathing at the place column
#print(df[(df['check'] == False) & (df['place'].notnull())][['judging', 'finals', 'total', 'place', 'competitors_name']])
#print("")
#print(df[df['check'] == False][['judging', 'finals', 'total', 'place', 'competitors_name']])

indexes = df[(df['check'] == False) & (df['place'].notnull())].index
#print(indexes)
#print("")

#for index in indexes:
#    start = max(index - 4, 0)
#    end = min(index + 5, len(df))
#    print(index, start, end)
#    print(df.loc[start:end][['judging', 'finals', 'total', 'place']])
#    print("")

# replace of the row 645 the columsn finals with 0
df.loc[645, 'finals'] = 0.0
df.loc[3122, 'total'] = 39.0
df.loc[3404, 'judging'] = 9.0
df.loc[3689, 'total'] = 17.0

df['check'] = df['judging'] + df['finals'] == df['total']
#print(df[(df['check'] == False) & (df['place'].notnull())][['judging', 'finals', 'total', 'place', 'competitors_name']])
#print("")


# rename the column competition_type into category
df = df.rename(columns={'competition_type': 'category'})

# make all the values of the category column uppercase
df['category'] = df['category'].str.upper()

# if " - OPEN" is in the category column, remove it
df['category'] = df['category'].str.replace(' - OPEN', '')

# if category is "BIKINI" replace it with "WOMEN'S BIKINI"
df['category'] = df['category'].replace('BIKINI', 'WOMEN\'S BIKINI')
# if category is "CLASSIC PHYSIQUE" replace it with "MEN'S CLASSIC PHYSIQUE"
df['category'] = df['category'].replace('CLASSIC PHYSIQUE', 'MEN\'S CLASSIC PHYSIQUE')


# Filter out rows with "MASTERS" or "WHEELCHAIR" in the category column
df_filtered = df[~df['category'].str.contains("WHEELCHAIR")]
df_filtered = df_filtered[~df_filtered['category'].str.contains("MASTERS")]

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
    "WOMEN'S WELLNESS": "Women's Wellness"
}
# Translate the categories using the dictionary
df_filtered['category'] = df_filtered['category'].map(category_translation)


# show me how many unique values are in the category column
#unique_categories = sorted(df_filtered['category'].unique())
#for category in unique_categories:
#    print(category)


def parse_country(entry):
    parts = entry.split(',')
    if len(parts) == 2:
        city = parts[0].strip() if parts[0].strip() else ""
        state = parts[1].strip()
        country = 'United States'
    else:
        city = ""
        state = ""
        country = parts[0].strip()
    return {"city": city, "state": state, "country": country}

# Apply the function to the "country" column
df_filtered['country'] = df_filtered['country'].apply(parse_country)

# print the columns country as a list
#print(df_filtered['country'].tolist())

# delete the column check
df_filtered = df_filtered.drop(columns=['check'])

# save the dataframe to a new csv file
df_filtered.to_csv('data_cleaned.csv', index=False)