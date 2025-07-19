import pandas as pd
import os
import json

def get_olympia_top3():
    """
    Extract all unique top 3 finishers from Olympia competitions.
    
    Returns:
        list: List of unique athlete keys who have placed in the top 3 at Olympia
    """
    # Path to the results.csv file
    results_path = "data/clean/results.csv"
    
    # Check if file exists
    if not os.path.exists(results_path):
        print(f"Error: {results_path} not found")
        return []
    
    try:
        # Read the CSV file
        df = pd.read_csv(results_path)
        
        # Filter for Olympia competitions (case insensitive)
        olympia_results = df[df['competition_name_key'].str.lower() == 'olympia']
        
        # Filter for top 3 finishers (place <= 3)
        olympia_top3 = olympia_results[olympia_results['Place'] <= 3]
        
        # Get unique athlete keys
        unique_top3 = olympia_top3['athlete_name_key'].unique().tolist()
        
        # Sort alphabetically for better readability
        unique_top3.sort()
        
        print(f"Found {len(unique_top3)} unique athletes who placed in top 3 at Olympia:")
        for i, athlete in enumerate(unique_top3, 1):
            print(f"{i:2d}. {athlete}")
        
        return unique_top3
        
    except Exception as e:
        print(f"Error reading or processing the file: {e}")
        return []

def get_olympia_top3_by_year():
    """
    Extract all Olympia top 3 finishers with their years and placements.
    
    Returns:
        dict: Dictionary with athlete keys as keys and list of (year, place) tuples as values
    """
    # Path to the results.csv file
    results_path = "data/clean/results.csv"
    
    # Check if file exists
    if not os.path.exists(results_path):
        print(f"Error: {results_path} not found")
        return {}
    
    try:
        # Read the CSV file
        df = pd.read_csv(results_path)
        
        # Filter for Olympia competitions (case insensitive)
        olympia_results = df[df['competition_name_key'].str.lower() == 'olympia']
        
        # Filter for top 3 finishers (place <= 3)
        olympia_top3 = olympia_results[olympia_results['Place'] <= 3]
        
        # Group by athlete and get their years and placements
        top3_by_year = {}
        for _, row in olympia_top3.iterrows():
            athlete = row['athlete_name_key']
            year = row['year']
            place = row['Place']
            
            if athlete not in top3_by_year:
                top3_by_year[athlete] = []
            top3_by_year[athlete].append((year, place))
        
        # Sort by year for each athlete
        for athlete in top3_by_year:
            top3_by_year[athlete].sort(key=lambda x: x[0])
        
        print(f"Found {len(top3_by_year)} unique athletes who placed in top 3 at Olympia:")
        for athlete, placements in sorted(top3_by_year.items()):
            placement_str = ", ".join([f"{year}({place})" for year, place in placements])
            print(f"{athlete}: {placement_str}")
        
        return top3_by_year
        
    except Exception as e:
        print(f"Error reading or processing the file: {e}")
        return {}

def get_arnold_classic_top3():
    """
    Extract all unique top 3 finishers from Arnold Classic competitions.
    
    Returns:
        list: List of unique athlete keys who have placed in the top 3 at Arnold Classic
    """
    # Path to the results.csv file
    results_path = "data/clean/results.csv"
    
    # Check if file exists
    if not os.path.exists(results_path):
        print(f"Error: {results_path} not found")
        return []
    
    try:
        # Read the CSV file
        df = pd.read_csv(results_path)
        
        # Filter for Arnold Classic competitions (case insensitive)
        arnold_results = df[df['competition_name_key'].str.lower() == 'arnold_classic']
        
        # Filter for top 3 finishers (place <= 3)
        arnold_top3 = arnold_results[arnold_results['Place'] <= 3]
        
        # Get unique athlete keys
        unique_top3 = arnold_top3['athlete_name_key'].unique().tolist()
        
        # Sort alphabetically for better readability
        unique_top3.sort()
        
        print(f"Found {len(unique_top3)} unique athletes who placed in top 3 at Arnold Classic:")
        for i, athlete in enumerate(unique_top3, 1):
            print(f"{i:2d}. {athlete}")
        
        return unique_top3
        
    except Exception as e:
        print(f"Error reading or processing the file: {e}")
        return []

def get_arnold_classic_top3_by_year():
    """
    Extract all Arnold Classic top 3 finishers with their years and placements.
    
    Returns:
        dict: Dictionary with athlete keys as keys and list of (year, place) tuples as values
    """
    # Path to the results.csv file
    results_path = "data/clean/results.csv"
    
    # Check if file exists
    if not os.path.exists(results_path):
        print(f"Error: {results_path} not found")
        return {}
    
    try:
        # Read the CSV file
        df = pd.read_csv(results_path)
        
        # Filter for Arnold Classic competitions (case insensitive)
        arnold_results = df[df['competition_name_key'].str.lower() == 'arnold_classic']
        
        # Filter for top 3 finishers (place <= 3)
        arnold_top3 = arnold_results[arnold_results['Place'] <= 3]
        
        # Group by athlete and get their years and placements
        top3_by_year = {}
        for _, row in arnold_top3.iterrows():
            athlete = row['athlete_name_key']
            year = row['year']
            place = row['Place']
            
            if athlete not in top3_by_year:
                top3_by_year[athlete] = []
            top3_by_year[athlete].append((year, place))
        
        # Sort by year for each athlete
        for athlete in top3_by_year:
            top3_by_year[athlete].sort(key=lambda x: x[0])
        
        print(f"Found {len(top3_by_year)} unique athletes who placed in top 3 at Arnold Classic:")
        for athlete, placements in sorted(top3_by_year.items()):
            placement_str = ", ".join([f"{year}({place})" for year, place in placements])
            print(f"{athlete}: {placement_str}")
        
        return top3_by_year
        
    except Exception as e:
        print(f"Error reading or processing the file: {e}")
        return {}

def get_all_top3_athletes_with_details():
    """
    Get all unique athletes who have placed in the top 3 at either Olympia or Arnold Classic
    with their division and year information.
    
    Returns:
        list: List of strings in format "name - division - year"
    """
    # Path to the results.csv file
    results_path = "data/clean/results.csv"
    
    # Check if file exists
    if not os.path.exists(results_path):
        print(f"Error: {results_path} not found")
        return []
    
    try:
        # Read the CSV file
        df = pd.read_csv(results_path)
        
        # Filter for Olympia and Arnold Classic competitions (case insensitive)
        olympia_results = df[df['competition_name_key'].str.lower() == 'olympia']
        arnold_results = df[df['competition_name_key'].str.lower() == 'arnold_classic']
        
        # Combine results
        combined_results = pd.concat([olympia_results, arnold_results])
        
        # Filter for top 3 finishers (place <= 3)
        top3_results = combined_results[combined_results['Place'] <= 3]
        
        # Create formatted strings
        athlete_details = []
        for _, row in top3_results.iterrows():
            name = row['athlete_name_key']
            division = row['Division']
            year = row['year']
            formatted_entry = f"{name} - {division} - {year}"
            athlete_details.append(formatted_entry)
        
        # Remove duplicates and sort
        unique_details = list(set(athlete_details))
        unique_details.sort()
        
        print(f"\nCombined unique athlete placements from both competitions: {len(unique_details)}")
        return unique_details
        
    except Exception as e:
        print(f"Error reading or processing the file: {e}")
        return []

def get_all_top3_athletes():
    """
    Get all unique athletes who have placed in the top 3 at either Olympia or Arnold Classic.
    
    Returns:
        list: List of unique athlete keys
    """
    olympia_athletes = get_olympia_top3()
    arnold_athletes = get_arnold_classic_top3()
    
    # Combine and remove duplicates
    all_athletes = list(set(olympia_athletes + arnold_athletes))
    all_athletes.sort()
    
    print(f"\nCombined unique athletes from both competitions: {len(all_athletes)}")
    return all_athletes

def save_top3_athletes_to_json():
    """
    Get all unique top 3 athletes from both competitions and save to JSON file.
    
    Returns:
        str: Path to the saved JSON file
    """
    all_athletes = get_all_top3_athletes_with_details()
    
    # Save to JSON file
    output_file = "all/top3_athletes.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_athletes, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved {len(all_athletes)} unique athlete placements to: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"Error saving to JSON: {e}")
        return None

def get_olympia_winners():
    """
    Extract all unique Olympia winners from the results.csv file.
    
    Returns:
        list: List of unique athlete keys who have won the Olympia competition
    """
    # Path to the results.csv file
    results_path = "data/clean/results.csv"
    
    # Check if file exists
    if not os.path.exists(results_path):
        print(f"Error: {results_path} not found")
        return []
    
    try:
        # Read the CSV file
        df = pd.read_csv(results_path)
        
        # Filter for Olympia competitions (case insensitive)
        olympia_results = df[df['competition_name_key'].str.lower() == 'olympia']
        
        # Filter for winners (place = 1)
        olympia_winners = olympia_results[olympia_results['Place'] == 1]
        
        # Get unique athlete keys
        unique_winners = olympia_winners['athlete_name_key'].unique().tolist()
        
        # Sort alphabetically for better readability
        unique_winners.sort()
        
        print(f"Found {len(unique_winners)} unique Olympia winners:")
        for i, winner in enumerate(unique_winners, 1):
            print(f"{i:2d}. {winner}")
        
        return unique_winners
        
    except Exception as e:
        print(f"Error reading or processing the file: {e}")
        return []

def get_olympia_winners_by_year():
    """
    Extract all Olympia winners with their winning years.
    
    Returns:
        dict: Dictionary with athlete keys as keys and list of winning years as values
    """
    # Path to the results.csv file
    results_path = "data/clean/results.csv"
    
    # Check if file exists
    if not os.path.exists(results_path):
        print(f"Error: {results_path} not found")
        return {}
    
    try:
        # Read the CSV file
        df = pd.read_csv(results_path)
        
        # Filter for Olympia competitions (case insensitive)
        olympia_results = df[df['competition_name_key'].str.lower() == 'olympia']
        
        # Filter for winners (place = 1)
        olympia_winners = olympia_results[olympia_results['Place'] == 1]
        
        # Group by athlete and get their winning years
        winners_by_year = {}
        for _, row in olympia_winners.iterrows():
            athlete = row['athlete_name_key']
            year = row['year']
            
            if athlete not in winners_by_year:
                winners_by_year[athlete] = []
            winners_by_year[athlete].append(year)
        
        # Sort years for each athlete
        for athlete in winners_by_year:
            winners_by_year[athlete].sort()
        
        print(f"Found {len(winners_by_year)} unique Olympia winners:")
        for athlete, years in sorted(winners_by_year.items()):
            print(f"{athlete}: {years}")
        
        return winners_by_year
        
    except Exception as e:
        print(f"Error reading or processing the file: {e}")
        return {}

if __name__ == "__main__":
    print("=== Olympia Top 3 Finishers (Unique Athlete Keys) ===")
    olympia_top3 = get_olympia_top3()
    
    print("\n=== Olympia Top 3 Finishers by Year ===")
    olympia_top3_by_year = get_olympia_top3_by_year()
    
    print("\n=== Arnold Classic Top 3 Finishers (Unique Athlete Keys) ===")
    arnold_top3 = get_arnold_classic_top3()
    
    print("\n=== Arnold Classic Top 3 Finishers by Year ===")
    arnold_top3_by_year = get_arnold_classic_top3_by_year()
    
    print("\n=== Combined Unique Top 3 Athletes ===")
    all_athletes = get_all_top3_athletes()
    
    print("\n=== Combined Unique Top 3 Athletes with Details ===")
    all_athletes_with_details = get_all_top3_athletes_with_details()
    
    print("\n=== Saving to JSON ===")
    json_file = save_top3_athletes_to_json()
    
    print("\n=== Olympia Winners (Unique Athlete Keys) ===")
    winners = get_olympia_winners()
    
    print("\n=== Olympia Winners by Year ===")
    winners_by_year = get_olympia_winners_by_year()
