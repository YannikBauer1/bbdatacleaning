import json
import csv
import os

def generate_competition_csv(json_file_path, output_csv_path):
    """
    Generate a CSV file from competition names JSON data.
    
    Args:
        json_file_path (str): Path to the competition names JSON file
        output_csv_path (str): Path where the CSV file will be saved
    
    Returns:
        None
    """
    # Read the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # List to store all competition entries
    competitions = []
    
    # Recursively traverse the JSON structure to find all competition arrays
    def extract_competitions(obj, current_path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{current_path}.{key}" if current_path else key
                extract_competitions(value, new_path)
        elif isinstance(obj, list):
            # This is a competition array
            if obj:  # Only process non-empty arrays
                # Find the shortest and longest names
                name_short = min(obj, key=len)
                name_long = max(obj, key=len)
                
                # Get the key from the path (last part after the last dot)
                name_key = current_path.split('.')[-1]
                
                # Create the formatted name (replace underscores with spaces and title case)
                name = name_key.replace('_', ' ').title()
                
                competitions.append({
                    'name_key': name_key,
                    'name_short': name_short,
                    'name_long': name_long,
                    'name': name
                })
    
    # Extract all competitions
    extract_competitions(data)
    
    # Write to CSV
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name_key', 'name_short', 'name_long', 'name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Write data
        for competition in competitions:
            writer.writerow(competition)
    
    print(f"CSV file generated successfully: {output_csv_path}")
    print(f"Total competitions processed: {len(competitions)}")

if __name__ == "__main__":
    # Define file paths
    json_file = "keys/competition_names.json"
    csv_file = "data/all/competition_names.csv"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    
    # Generate the CSV file
    generate_competition_csv(json_file, csv_file)
