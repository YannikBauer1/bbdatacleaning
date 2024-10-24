import pandas as pd
import numpy as np

df = pd.read_csv('data.csv')

# return me how many rows and columns 
#print(df.shape)

# return me the data types of each column
#print(df.dtypes)

# remove rows that have no name in it ( false rows )
print(df['competitors_name'].isnull().sum())
print("")
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
print(df['check'].value_counts())
print("")

# show me the rows that have false in the check column, show the columns judging, finals, total and competitors_name which have not nathing at the place column
print(df[(df['check'] == False) & (df['place'].notnull())][['judging', 'finals', 'total', 'place', 'competitors_name']])
print("")
#print(df[df['check'] == False][['judging', 'finals', 'total', 'place', 'competitors_name']])

indexes = df[(df['check'] == False) & (df['place'].notnull())].index
print(indexes)
print("")

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
print(df[(df['check'] == False) & (df['place'].notnull())][['judging', 'finals', 'total', 'place', 'competitors_name']])
print("")