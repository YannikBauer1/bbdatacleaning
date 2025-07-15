import pandas as pd
import numpy as np
from datetime import datetime

def extract_year_from_date(date_str):
    """Extract year from date string, handling various formats"""
    if pd.isna(date_str) or date_str == '':
        return None
    
    try:
        # Try to parse the date
        if isinstance(date_str, str):
            # Handle different date formats
            if '-' in date_str:
                return int(date_str.split('-')[0])
            elif '/' in date_str:
                return int(date_str.split('/')[-1])  # Assume year is last part
        return None
    except:
        return None

def get_source_priority(source):
    """Return priority number for source (lower number = higher priority)"""
    source_priorities = {
        '2024': 1,
        'scorecards': 2,
        'npcnews': 3,
        'musclememory': 4
    }
    return source_priorities.get(source.lower(), 999)  # Default low priority for unknown sources

def get_place_dedup_priority(source):
    """Return priority number for place deduplication (lower number = higher priority)"""
    place_priorities = {
        'npcnews': 1,
        '2024': 2,
        'scorecards': 3,
        'musclememory': 4
    }
    return place_priorities.get(source.lower(), 999)  # Default low priority for unknown sources

def main():
    print("Reading data files...")
    
    # Read the data files
    try:
        all_clean_df = pd.read_csv('data/all/all_clean.csv')
        events_df = pd.read_csv('data/all/events.csv')
    except Exception as e:
        print(f"Error reading files: {e}")
        return
    
    print(f"Loaded {len(all_clean_df)} rows from all_clean.csv")
    print(f"Loaded {len(events_df)} rows from events.csv")
    
    # Create a mapping from competition name to competition_key
    competition_mapping = {}
    for _, row in events_df.iterrows():
        competition_key = row['competition_key']
        year = row['year']
        key = (competition_key, year)
        competition_mapping[key] = competition_key
    
    print(f"Created competition mapping with {len(competition_mapping)} entries")
    
    # Extract year from start date
    print("Extracting years from start dates...")
    all_clean_df['year'] = all_clean_df['Start Date'].apply(extract_year_from_date)
    
    # Create competition_key column
    print("Creating competition keys...")
    def get_competition_key(row):
        competition = row['Competition']
        year = row['year']
        if pd.isna(competition) or pd.isna(year):
            return competition  # Return original if we can't map
        return competition  # For now, use competition name as key
    
    all_clean_df['competition_name_key'] = all_clean_df.apply(get_competition_key, axis=1)
    
    # Rename competitor name column
    all_clean_df['athlete_name_key'] = all_clean_df['Competitor Name']
    
    # Add source priority for deduplication
    all_clean_df['source_priority'] = all_clean_df['Source'].apply(get_source_priority)
    
    # Add place deduplication priority
    all_clean_df['place_dedup_priority'] = all_clean_df['Source'].apply(get_place_dedup_priority)
    
    # Select and rename columns
    print("Selecting and ordering columns...")
    results_df = all_clean_df[[
        'year',
        'competition_name_key', 
        'athlete_name_key',
        'Judging 1',
        'Judging 2', 
        'Judging 3',
        'Judging 4',
        'Routine',
        'Total',
        'Place',
        'Division',
        'Division Subtype',
        'Division Level',
        'Source',
        'source_priority',
        'place_dedup_priority'
    ]].copy()
    
    # Remove rows with missing year
    results_df = results_df.dropna(subset=['year'])
    print(f"After removing rows with missing year: {len(results_df)} rows")
    
    # Fix rows with place 0 by setting them to the last place of that division in that competition
    print("Fixing rows with place 0...")
    
    # First, ensure Place column is numeric
    results_df['Place'] = pd.to_numeric(results_df['Place'], errors='coerce').fillna(0)
    
    # First, sort by year, competition, division, and place to ensure proper ordering
    results_df = results_df.sort_values(['year', 'competition_name_key', 'Division', 'Division Subtype', 'Place'])
    
    # Group by year, competition, division, and division subtype to find the last place for each group
    def fix_zero_places(group):
        # Find the maximum place in this group (excluding 0)
        max_place = group[group['Place'] > 0]['Place'].max()
        if pd.notna(max_place):
            # Set all places that are 0 to the max place (tied for last place)
            group.loc[group['Place'] == 0, 'Place'] = max_place
        else:
            # If all places are 0, assign sequential places starting from 1
            zero_count = (group['Place'] == 0).sum()
            if zero_count > 0:
                group.loc[group['Place'] == 0, 'Place'] = range(1, zero_count + 1)
        return group
    
    # Apply the fix to each group - include Division Subtype in grouping
    results_df = results_df.groupby(['year', 'competition_name_key', 'Division', 'Division Subtype']).apply(fix_zero_places).reset_index(drop=True)
    
    print(f"Fixed {len(results_df[results_df['Place'] == 0])} rows with place 0")
    
    # Handle duplicates based on source priority
    print("Handling duplicates based on source priority...")
    
    # Define the columns to check for duplicates (INCLUDING Place so we only deduplicate same athlete in same place)
    duplicate_columns = [
        'year', 'competition_name_key', 'athlete_name_key', 
        'Division', 'Division Subtype', 'Place'
    ]
    
    # Sort by source priority (ascending) so higher priority sources come first
    results_df = results_df.sort_values('source_priority')
    
    # Remove duplicates keeping the first occurrence (highest priority source)
    # This will only remove duplicates when the same athlete appears in the same place from different sources
    results_df = results_df.drop_duplicates(
        subset=duplicate_columns, 
        keep='first'
    )
    
    print(f"After removing duplicates: {len(results_df)} rows")
    
    # Store the deduplicated data for later comparison
    deduplicated_df = results_df.copy()
    
    # SECOND DEDUPLICATION: Check for duplicate places within each competition/year/division group
    print("Checking for duplicate places within competition/year/division groups...")
    
    # Work with the dataframe that results from Step 1 (deduplicated_df)
    # Add place deduplication priority to the deduplicated dataframe
    deduplicated_df['place_dedup_priority'] = deduplicated_df['Source'].apply(get_place_dedup_priority)
    
    # Sort by place deduplication priority (ascending) so higher priority sources come first
    deduplicated_df = deduplicated_df.sort_values('place_dedup_priority')
    
    # Group by year, competition, division, division subtype, and place
    def remove_duplicate_places(group):
        if len(group) == 1:
            return group
        
        # Check if all sources are the same
        unique_sources = group['Source'].nunique()
        if unique_sources == 1:
            # All sources are the same, keep all rows
            return group
        else:
            # Different sources, keep only the first (highest priority)
            return group.head(1)
    
    # Apply the place deduplication to each group
    place_deduplicated_df = deduplicated_df.groupby(['year', 'competition_name_key', 'Division', 'Division Subtype', 'Place']).apply(remove_duplicate_places).reset_index(drop=True)
    
    # Handle athlete place conflicts between sources
    # This happens when the same athlete appears in different places in different sources
    # For example, ashley_kaitwasser is 1st in npcnews but 2nd in scorecards
    # print("Handling athlete place conflicts between sources...")
    
    # For each competition/year/division group, determine the best source to use
    # def get_best_source_for_competition(group):
    #     if len(group) == 0:
    #         return group
        
    #     # Find the highest priority source that has data for this competition
    #     available_sources = group['Source'].unique()
    #     source_priorities = {}
        
    #     for source in available_sources:
    #         source_priority = group[group['Source'] == source]['place_dedup_priority'].iloc[0]
    #         source_priorities[source] = source_priority
        
    #     # Get the source with the highest priority (lowest number)
    #     best_source = min(source_priorities, key=source_priorities.get)
        
    #     # Get all athletes from the best source for this competition
    #     best_source_data = original_df[
    #         (original_df['year'] == group['year'].iloc[0]) &
    #         (original_df['competition_name_key'] == group['competition_name_key'].iloc[0]) &
    #         (original_df['Division'] == group['Division'].iloc[0]) &
    #         (original_df['Division Subtype'] == group['Division Subtype'].iloc[0]) &
    #         (original_df['Source'] == best_source)
    #     ]
        
    #     return best_source_data
    
    # Apply the source selection to each competition/year/division group
    # final_results_df = place_deduplicated_df.groupby(['year', 'competition_name_key', 'Division', 'Division Subtype']).apply(get_best_source_for_competition).reset_index(drop=True)
    
    # print(f"After resolving athlete place conflicts: {len(final_results_df)} rows")
    
    # Use the final results as the output
    # results_df = final_results_df.copy()
    
    # Use the place deduplicated data as the final result
    print("Using place deduplicated results as final output...")
    results_df = place_deduplicated_df.copy()
    
    print(f"After combining results: {len(results_df)} rows")
    
    # Remove the priority columns as they were only used for deduplication
    results_df = results_df.drop(['source_priority', 'place_dedup_priority'], axis=1)

    # Remove row with 2010,europa_dallas_pro,julia_ann_kulla,0,0,0,0,0,0,10,figure,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2010) & 
          (results_df['competition_name_key'] == 'europa_dallas_pro') & 
          (results_df['athlete_name_key'] == 'julia_ann_kulla') & 
          (results_df['Place'] == 10))
    ]
    # 2010,europa_phoenix_pro,antoinette_tonie_thompson,0,0,0,0,0,0,7,womensbb,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2010) & 
          (results_df['competition_name_key'] == 'europa_phoenix_pro') & 
          (results_df['athlete_name_key'] == 'antoinette_tonie_thompson') & 
          (results_df['Place'] == 7))
    ]
    # 2010,jacksonville_pro,joanne_murphy,0,0,0,0,0,0,17,figure,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2010) & 
          (results_df['competition_name_key'] == 'jacksonville_pro') & 
          (results_df['athlete_name_key'] == 'joanne_murphy') & 
          (results_df['Place'] == 17))
    ]
    # 2011,jacksonville_pro,angel_manuel_rangel_vargas,0,0,0,0,0,0,6,202_212,202,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2011) & 
          (results_df['competition_name_key'] == 'jacksonville_pro') & 
          (results_df['athlete_name_key'] == 'angel_manuel_rangel_vargas') & 
          (results_df['Place'] == 6))
    ]
    # 2011,toronto_supershow,ann_pratt,0,0,0,0,0,0,17,figure,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2011) & 
          (results_df['competition_name_key'] == 'toronto_supershow') & 
          (results_df['athlete_name_key'] == 'ann_pratt') & 
          (results_df['Place'] == 17))
    ]
    # 2012,arnold_classic,abigail_burrows,0,0,0,0,0,0,16,bikini,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2012) & 
          (results_df['competition_name_key'] == 'arnold_classic') & 
          (results_df['athlete_name_key'] == 'abigail_burrows') & 
          (results_df['Place'] == 16))
    ]
    # 2013,fort_lauderdale_pro,bernadette_marassa,24,0,0,0,0,24,5,bikini,open,pro,scorecards
    results_df = results_df[
        ~((results_df['year'] == 2013) & 
          (results_df['competition_name_key'] == 'fort_lauderdale_pro') & 
          (results_df['athlete_name_key'] == 'bernadette_marassa') & 
          (results_df['Place'] == 5))
    ]
    # 2013,houston_pro,cynthia_benoit,20,0,0,0,0,20,4,bikini,open,pro,scorecards
    results_df = results_df[
        ~((results_df['year'] == 2013) & 
          (results_df['competition_name_key'] == 'houston_pro') & 
          (results_df['athlete_name_key'] == 'cynthia_benoit') & 
          (results_df['Place'] == 4))
    ]
    # 2014,iron_games_pro,kirsten_moffett,0,0,0,0,0,0,13,bikini,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2014) & 
          (results_df['competition_name_key'] == 'iron_games_pro') & 
          (results_df['athlete_name_key'] == 'kirsten_moffett') & 
          (results_df['Place'] == 13))
    ]
    # 2016,toronto_supershow,tamara_quershi,0,0,0,0,0,0,4,womensphysique,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2016) & 
          (results_df['competition_name_key'] == 'toronto_supershow') & 
          (results_df['athlete_name_key'] == 'tamara_quershi') & 
          (results_df['Place'] == 4))
    ]
    # 2017,california_pro,bola_ojex,0,0,0,0,0,0,17,mensbb,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2017) & 
          (results_df['competition_name_key'] == 'california_pro') & 
          (results_df['athlete_name_key'] == 'bola_ojex') & 
          (results_df['Place'] == 17))
    ]
    # 2017,california_pro,omar_deckard,0,0,0,0,0,0,18,mensbb,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2017) & 
          (results_df['competition_name_key'] == 'california_pro') & 
          (results_df['athlete_name_key'] == 'omar_deckard') & 
          (results_df['Place'] == 18))
    ]
    # 2017,california_pro,big_will_harris,0,0,0,0,0,0,18,mensbb,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2017) & 
          (results_df['competition_name_key'] == 'california_pro') & 
          (results_df['athlete_name_key'] == 'big_will_harris') & 
          (results_df['Place'] == 18))
    ]
    # 2017,california_pro,john_meadows,0,0,0,0,0,0,18,mensbb,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2017) & 
          (results_df['competition_name_key'] == 'california_pro') & 
          (results_df['athlete_name_key'] == 'john_meadows') & 
          (results_df['Place'] == 18))
    ]
    # 2017,california_pro,jose_paul_sanchez_reyes,0,0,0,0,0,0,18,mensbb,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2017) & 
          (results_df['competition_name_key'] == 'california_pro') & 
          (results_df['athlete_name_key'] == 'jose_paul_sanchez_reyes') & 
          (results_df['Place'] == 18))
    ]
    # 2017,california_pro,an_nguyen,0,0,0,0,0,0,18,mensbb,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2017) & 
          (results_df['competition_name_key'] == 'california_pro') & 
          (results_df['athlete_name_key'] == 'an_nguyen') & 
          (results_df['Place'] == 18))
    ]
    # 2018,battle_in_the_desert,francesca_lauren,19,19,0,0,0,38,6,bikini,open,pro,scorecards
    results_df = results_df[
        ~((results_df['year'] == 2018) & 
          (results_df['competition_name_key'] == 'battle_in_the_desert') & 
          (results_df['athlete_name_key'] == 'francesca_lauren') & 
          (results_df['Place'] == 6))
    ]
    # 2018,indy_pro,ben_barkes,0,0,0,0,0,0,13,202_212,212,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2018) & 
          (results_df['competition_name_key'] == 'indy_pro') & 
          (results_df['athlete_name_key'] == 'ben_barkes') & 
          (results_df['Place'] == 13))
    ]
    # 2018,indy_pro,ben_barkes,41,0,0,0,0,0,15,202_212,212,pro,scorecards
    results_df = results_df[
        ~((results_df['year'] == 2018) & 
          (results_df['competition_name_key'] == 'indy_pro') & 
          (results_df['athlete_name_key'] == 'ben_barkes') & 
          (results_df['Place'] == 15))
    ]
    # 2018,indy_pro,walter_martin,35,0,0,0,0,0,15,202_212,212,pro,scorecards
    results_df = results_df[
        ~((results_df['year'] == 2018) & 
          (results_df['competition_name_key'] == 'indy_pro') & 
          (results_df['athlete_name_key'] == 'walter_martin') & 
          (results_df['Place'] == 15))
    ]
    # 2018,indy_pro,darron_glenn,37,0,0,0,0,0,15,202_212,212,pro,scorecards
    results_df = results_df[
        ~((results_df['year'] == 2018) & 
          (results_df['competition_name_key'] == 'indy_pro') & 
          (results_df['athlete_name_key'] == 'darron_glenn') & 
          (results_df['Place'] == 15))
    ]
    # 2018,olympia,wesley_vissers,0,0,0,0,0,0,16,classic,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2018) & 
          (results_df['competition_name_key'] == 'olympia') & 
          (results_df['athlete_name_key'] == 'wesley_vissers') & 
          (results_df['Place'] == 16))
    ]
    # 2018,tampa_pro,maude_exantus,0,0,0,0,0,0,5,figure,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2018) & 
          (results_df['competition_name_key'] == 'tampa_pro') & 
          (results_df['athlete_name_key'] == 'maude_exantus') & 
          (results_df['Place'] == 5))
    ]
    # 2019,romania_muscle_fest_pro,ivonne_ponce,0,0,0,0,0,0,18,figure,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2019) & 
          (results_df['competition_name_key'] == 'romania_muscle_fest_pro') & 
          (results_df['athlete_name_key'] == 'ivonne_ponce') & 
          (results_df['Place'] == 18))
    ]
    # 2015,europa_phoenix_pro,hugo_alejandro_ortiz,0,0,0,0,0,0,12,202_212,212,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2015) & 
          (results_df['competition_name_key'] == 'europa_phoenix_pro') & 
          (results_df['athlete_name_key'] == 'hugo_alejandro_ortiz') & 
          (results_df['Place'] == 12))
    ]
    # 2012,kentucky_muscle,rosalind_vanterpool,0,0,0,0,0,0,17,figure,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2012) & 
          (results_df['competition_name_key'] == 'kentucky_muscle') & 
          (results_df['athlete_name_key'] == 'rosalind_vanterpool') & 
          (results_df['Place'] == 17))
    ]
    # 2013,europa_pro,alfonso_valencia_del_rio,0,0,0,0,0,0,17,mensbb,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2013) & 
          (results_df['competition_name_key'] == 'europa_pro') & 
          (results_df['athlete_name_key'] == 'alfonso_valencia_del_rio') & 
          (results_df['Place'] == 17))
    ]
    # 2013,new_york_pro,zaher_moukahal,0,0,0,0,0,0,15,mensbb,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2013) & 
          (results_df['competition_name_key'] == 'new_york_pro') & 
          (results_df['athlete_name_key'] == 'zaher_moukahal') & 
          (results_df['Place'] == 15))
    ]
    # 2013,olympia,mindi_obrien,0,0,0,0,0,0,6,womensphysique,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2013) & 
          (results_df['competition_name_key'] == 'olympia') & 
          (results_df['athlete_name_key'] == 'mindi_obrien') & 
          (results_df['Place'] == 6))
    ]
    # 2013,olympia,venus_nguyen,0,0,0,0,0,0,9,womensphysique,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2013) & 
          (results_df['competition_name_key'] == 'olympia') & 
          (results_df['athlete_name_key'] == 'venus_nguyen') & 
          (results_df['Place'] == 9))
    ]
    # 2013,toronto_supershow,jessica_renee_fletcher,0,0,0,0,0,0,4,bikini,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2013) & 
          (results_df['competition_name_key'] == 'toronto_supershow') & 
          (results_df['athlete_name_key'] == 'jessica_renee_fletcher') & 
          (results_df['Place'] == 4))
    ]
    # 2013,toronto_supershow,janessa_roy,0,0,0,0,0,0,16,womensphysique,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2013) & 
          (results_df['competition_name_key'] == 'toronto_supershow') & 
          (results_df['athlete_name_key'] == 'janessa_roy') & 
          (results_df['Place'] == 16))
    ]
    # 2014,europa_phoenix_pro,beckie_boddie,0,0,0,0,0,0,16,figure,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2014) & 
          (results_df['competition_name_key'] == 'europa_phoenix_pro') & 
          (results_df['athlete_name_key'] == 'beckie_boddie') & 
          (results_df['Place'] == 16))
    ]
    # 2014,omaha_pro,sean_harley,0,0,0,0,0,0,15,mensphysique,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2014) & 
          (results_df['competition_name_key'] == 'omaha_pro') & 
          (results_df['athlete_name_key'] == 'sean_harley') & 
          (results_df['Place'] == 15))
    ]
    # 2014,titans_grand_prix,leonie_rose,0,0,0,0,0,0,3,womensphysique,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2014) & 
          (results_df['competition_name_key'] == 'titans_grand_prix') & 
          (results_df['athlete_name_key'] == 'leonie_rose') & 
          (results_df['Place'] == 3))
    ]
    # 2015,chicago_pro,irene_andersen,0,0,0,0,0,0,8,womensbb,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2015) & 
          (results_df['competition_name_key'] == 'chicago_pro') & 
          (results_df['athlete_name_key'] == 'irene_andersen') & 
          (results_df['Place'] == 8))
    ]
    # 2015,los_angeles_pro,linda_crossley,0,0,0,0,0,0,12,figure,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2015) & 
          (results_df['competition_name_key'] == 'los_angeles_pro') & 
          (results_df['athlete_name_key'] == 'linda_crossley') & 
          (results_df['Place'] == 12))
    ]
    # 2015,mozolani_pro,raul_carrasco_jimenez,30,0,0,0,0,0,9,202_212,212,pro,scorecards
    results_df = results_df[
        ~((results_df['year'] == 2015) & 
          (results_df['competition_name_key'] == 'mozolani_pro') & 
          (results_df['athlete_name_key'] == 'raul_carrasco_jimenez') & 
          (results_df['Place'] == 9))
    ]
    # 2015,mozolani_pro,benjamin_parra_munoz,35,0,0,0,0,0,9,202_212,212,pro,scorecards
    results_df = results_df[
        ~((results_df['year'] == 2015) & 
          (results_df['competition_name_key'] == 'mozolani_pro') & 
          (results_df['athlete_name_key'] == 'benjamin_parra_munoz') & 
          (results_df['Place'] == 9))
    ]
    # 2015,mozolani_pro,alison_maria,40,0,0,0,0,0,9,202_212,212,pro,scorecards
    results_df = results_df[
        ~((results_df['year'] == 2015) & 
          (results_df['competition_name_key'] == 'mozolani_pro') & 
          (results_df['athlete_name_key'] == 'alison_maria') & 
          (results_df['Place'] == 9))
    ]
    # 2015,olympia,jr_earnest_flowers,0,0,0,0,0,0,15,mensphysique,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2015) & 
          (results_df['competition_name_key'] == 'olympia') & 
          (results_df['athlete_name_key'] == 'jr_earnest_flowers') & 
          (results_df['Place'] == 15))
    ]
    # 2015,orlando_show_of_champions,iain_valliere,0,0,0,0,0,0,17,mensbb,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2015) & 
          (results_df['competition_name_key'] == 'orlando_show_of_champions') & 
          (results_df['athlete_name_key'] == 'iain_valliere') & 
          (results_df['Place'] == 17))
    ]
    # 2015,tampa_pro,jennifer_hernandez,0,0,0,0,0,0,16,womensphysique,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2015) & 
          (results_df['competition_name_key'] == 'tampa_pro') & 
          (results_df['athlete_name_key'] == 'jennifer_hernandez') & 
          (results_df['Place'] == 16))
    ]
    # 2016,europa_dallas_pro,matthew_mugford,0,0,0,0,0,0,8,mensphysique,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2016) & 
          (results_df['competition_name_key'] == 'europa_dallas_pro') & 
          (results_df['athlete_name_key'] == 'matthew_mugford') & 
          (results_df['Place'] == 8))
    ]
    # 2017,golden_state_pro,thomas_riley,0,0,0,0,0,0,16,mensphysique,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2017) & 
          (results_df['competition_name_key'] == 'golden_state_pro') & 
          (results_df['athlete_name_key'] == 'thomas_riley') & 
          (results_df['Place'] == 16))
    ]
    # 2018,indy_pro,joseph_mackey,0,0,0,0,0,0,11,mensbb,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2018) & 
          (results_df['competition_name_key'] == 'indy_pro') & 
          (results_df['athlete_name_key'] == 'joseph_mackey') & 
          (results_df['Place'] == 11))
    ]
    # 2018,indy_pro,wendall_floyd,0,0,0,0,0,0,15,mensbb,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2018) & 
          (results_df['competition_name_key'] == 'indy_pro') & 
          (results_df['athlete_name_key'] == 'wendall_floyd') & 
          (results_df['Place'] == 15))
    ]
    # 2018,indy_pro,derek_upshaw_morgan,0,0,0,0,0,0,14,mensbb,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2018) & 
          (results_df['competition_name_key'] == 'indy_pro') & 
          (results_df['athlete_name_key'] == 'derek_upshaw_morgan') & 
          (results_df['Place'] == 14))
    ]
    # 2018,indy_pro,mitchell_staats,0,0,0,0,0,0,13,mensbb,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2018) & 
          (results_df['competition_name_key'] == 'indy_pro') & 
          (results_df['athlete_name_key'] == 'mitchell_staats') & 
          (results_df['Place'] == 13))
    ]
    # 2018,indy_pro,michael_lynn,0,0,0,0,0,0,12,mensbb,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2018) & 
          (results_df['competition_name_key'] == 'indy_pro') & 
          (results_df['athlete_name_key'] == 'michael_lynn') & 
          (results_df['Place'] == 12))
    ]
    # 2018,mile_high_pro,kevin_reeder,0,0,0,0,0,0,15,mensphysique,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2018) & 
          (results_df['competition_name_key'] == 'mile_high_pro') & 
          (results_df['athlete_name_key'] == 'kevin_reeder') & 
          (results_df['Place'] == 15))
    ]
    # 2019,romania_muscle_fest_pro,rahel_cucchia,0,0,0,0,0,0,14,figure,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2019) & 
          (results_df['competition_name_key'] == 'romania_muscle_fest_pro') & 
          (results_df['athlete_name_key'] == 'rahel_cucchia') & 
          (results_df['Place'] == 14))
    ]
    # 2019,sacramento_pro,bruna_montenegro,0,0,0,0,0,0,13,bikini,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2019) & 
          (results_df['competition_name_key'] == 'sacramento_pro') & 
          (results_df['athlete_name_key'] == 'bruna_montenegro') & 
          (results_df['Place'] == 13))
    ]
    # 2019,tampa_hurricane_pro,maria_luisa_heeg,0,0,0,0,0,0,14,bikini,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2019) & 
          (results_df['competition_name_key'] == 'tampa_hurricane_pro') & 
          (results_df['athlete_name_key'] == 'maria_luisa_heeg') & 
          (results_df['Place'] == 14))
    ]
    # 2020,arnold_classic,patrick_moore,0,0,0,0,0,0,13,mensbb,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2020) & 
          (results_df['competition_name_key'] == 'arnold_classic') & 
          (results_df['athlete_name_key'] == 'patrick_moore') & 
          (results_df['Place'] == 13))
    ]
    # 2020,arnold_classic,valentina_mishina,0,0,0,0,0,0,10,womensphysique,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2020) & 
          (results_df['competition_name_key'] == 'arnold_classic') & 
          (results_df['athlete_name_key'] == 'valentina_mishina') & 
          (results_df['Place'] == 10))
    ]
    # 2021,chicago_pro,seth_shaw,0,0,0,0,0,0,15,mensbb,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2021) & 
          (results_df['competition_name_key'] == 'chicago_pro') & 
          (results_df['athlete_name_key'] == 'seth_shaw') & 
          (results_df['Place'] == 15))
    ]
    # 2021,olympia,sandra_grajales_romera,0,0,0,0,0,0,12,figure,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2021) & 
          (results_df['competition_name_key'] == 'olympia') & 
          (results_df['athlete_name_key'] == 'sandra_grajales_romera') & 
          (results_df['Place'] == 12))
    ]
    # 2023,hungary_fitparade_pr,catia_moreira,0,0,0,0,0,0,11,wellness,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2023) & 
          (results_df['competition_name_key'] == 'hungary_fitparade_pr') & 
          (results_df['athlete_name_key'] == 'catia_moreira') & 
          (results_df['Place'] == 11))
    ]
    # 2023,japan_pro,uchral_byambaatseren,0,0,0,0,0,0,16,bikini,open,pro,scorecards
    results_df = results_df[
        ~((results_df['year'] == 2023) & 
          (results_df['competition_name_key'] == 'japan_pro') & 
          (results_df['athlete_name_key'] == 'uchral_byambaatseren') & 
          (results_df['Place'] == 16))
    ]
    # 2023,japan_pro,pei_fen_lin,0,0,0,0,0,0,16,bikini,open,pro,scorecards
    results_df = results_df[
        ~((results_df['year'] == 2023) & 
          (results_df['competition_name_key'] == 'japan_pro') & 
          (results_df['athlete_name_key'] == 'pei_fen_lin') & 
          (results_df['Place'] == 16))
    ]
    # 2023,legions_sports_fest,laura_pyszora,0,0,0,0,0,0,7,womensphysique,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2023) & 
          (results_df['competition_name_key'] == 'legions_sports_fest') & 
          (results_df['athlete_name_key'] == 'laura_pyszora') & 
          (results_df['Place'] == 7))
    ]
    # 2023,musclecontest_goiania,fabio_campos_campos,0,0,0,0,0,0,3,mensphysique,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2023) & 
          (results_df['competition_name_key'] == 'musclecontest_goiania') & 
          (results_df['athlete_name_key'] == 'fabio_campos_campos') & 
          (results_df['Place'] == 3))
    ]
    # 2023,tahoe_pro,michelle_hurst,48,0,0,0,0,48,16,bikini,open,pro,scorecards
    results_df = results_df[
        ~((results_df['year'] == 2023) & 
          (results_df['competition_name_key'] == 'tahoe_pro') & 
          (results_df['athlete_name_key'] == 'michelle_hurst') & 
          (results_df['Place'] == 16))
    ]
    # 2023,tokyo_pro,jiaqi_wei,0,0,0,0,0,0,9,bikini,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2023) & 
          (results_df['competition_name_key'] == 'tokyo_pro') & 
          (results_df['athlete_name_key'] == 'jiaqi_wei') & 
          (results_df['Place'] == 9))
    ]
    # 2024,republic_of_texas_pro,aspen_ranz,0,0,0,0,0,0,16,bikini,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2024) & 
          (results_df['competition_name_key'] == 'republic_of_texas_pro') & 
          (results_df['athlete_name_key'] == 'aspen_ranz') & 
          (results_df['Place'] == 16))
    ]
    # 2024,spain_empro_classic,victoria_tonnesen_persson,0,0,0,0,0,0,10,figure,open,pro,npcnews
    results_df = results_df[
        ~((results_df['year'] == 2024) & 
          (results_df['competition_name_key'] == 'spain_empro_classic') & 
          (results_df['athlete_name_key'] == 'victoria_tonnesen_persson') & 
          (results_df['Place'] == 10))
    ]
    # 2019,san_marino_pro,milad_sadeghi,6,0,0,0,0,6,2,classic,open,pro,scorecards
    results_df = results_df[
        ~((results_df['year'] == 2019) & 
          (results_df['competition_name_key'] == 'san_marino_pro') & 
          (results_df['athlete_name_key'] == 'milad_sadeghi') & 
          (results_df['Place'] == 2))
    ]
    # 2019,san_marino_pro,klaus_drescher,0,0,0,0,0,0,12,classic,open,pro,musclememory
    results_df = results_df[
        ~((results_df['year'] == 2019) & 
          (results_df['competition_name_key'] == 'san_marino_pro') & 
          (results_df['athlete_name_key'] == 'klaus_drescher') & 
          (results_df['Place'] == 12))
    ]







    


    
    # Sort by year, competition name, division, division subtype, and place
    print("Sorting by year, competition name, division, division subtype, and place...")
    results_df = results_df.sort_values(['year', 'competition_name_key', 'Division', 'Division Subtype', 'Place'])
    
    # Convert numeric columns to integers
    print("Converting numeric columns to integers...")
    numeric_columns = ['year', 'Judging 1', 'Judging 2', 'Judging 3', 'Judging 4', 'Routine', 'Total', 'Place']
    
    for col in numeric_columns:
        if col in results_df.columns:
            # Fill NaN values with 0 for integer conversion
            results_df[col] = results_df[col].fillna(0)
            # Convert to integer, handling any remaining non-numeric values
            try:
                results_df[col] = pd.to_numeric(results_df[col], errors='coerce').fillna(0).astype(int)
            except:
                print(f"Warning: Could not convert column {col} to integers")
    
    print("Numeric conversion completed")
    
    # Save the results
    output_file = 'data/all/results.csv'
    print(f"Saving results to {output_file}...")
    results_df.to_csv(output_file, index=False)
    
    print(f"Successfully created {output_file} with {len(results_df)} rows")
    
    # Print some statistics
    print("\nStatistics:")
    print(f"Year range: {results_df['year'].min()} - {results_df['year'].max()}")
    print(f"Number of competitions: {results_df['competition_name_key'].nunique()}")
    print(f"Number of athletes: {results_df['athlete_name_key'].nunique()}")
    print(f"Number of divisions: {results_df['Division'].nunique()}")
    
    # Show source distribution
    print("\nSource distribution:")
    source_counts = results_df['Source'].value_counts()
    for source, count in source_counts.items():
        print(f"  {source}: {count}")

if __name__ == "__main__":
    main()
