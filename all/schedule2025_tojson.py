import csv
import json

def csv_to_json():
    # Read the CSV file
    csv_file_path = 'data/clean/schedule2025.csv'
    json_file_path = 'data/clean/schedule2025.json'
    
    competitions = {}
    
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            competition_key = row['competition_key']
            
            # Create the competition object with the requested fields
            competition_data = {
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'year': row['year'],
                'name': row['name'],
                'url': row['url']
            }
            
            competitions[competition_key] = competition_data
    
    # Write the JSON file
    with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(competitions, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"Successfully converted CSV to JSON. Output saved to {json_file_path}")
    print(f"Total competitions processed: {len(competitions)}")

if __name__ == "__main__":
    csv_to_json()
