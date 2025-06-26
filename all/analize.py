import pandas as pd
import os
import json

def get_unique_divisions():
    """
    Read the all_clean.csv file and return all unique division names.
    
    Returns:
        list: A list of unique division names sorted alphabetically
    """
    # Path to the CSV file - adjust based on current working directory
    csv_path = "data/all/all_clean.csv"
    
    # Check if file exists
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at: {csv_path}")
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Get unique values from the Division column
        unique_divisions = df['Division'].unique()
        
        # Remove any NaN values and sort alphabetically
        unique_divisions = sorted([div for div in unique_divisions if pd.notna(div)])
        
        return unique_divisions
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def create_divisions_json():
    """
    Create a JSON file where each division name is a key with an array containing that division name.
    
    Returns:
        str: Path to the created JSON file
    """
    divisions = get_unique_divisions()
    
    if not divisions:
        print("No divisions found. Cannot create JSON file.")
        return None
    
    # Create dictionary where each division is a key with an array containing the division name
    # Sort alphabetically by division name
    divisions_dict = {division: [division] for division in sorted(divisions)}
    
    # Define output file path
    output_path = "all/divisions.json"
    
    try:
        # Write to JSON file with nice formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(divisions_dict, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully created JSON file: {output_path}")
        print(f"Contains {len(divisions_dict)} divisions")
        return output_path
        
    except Exception as e:
        print(f"Error writing JSON file: {e}")
        return None

def print_unique_divisions():
    """
    Print all unique division names to the console.
    """
    divisions = get_unique_divisions()
    
    if divisions:
        print(f"Found {len(divisions)} unique divisions:")
        print("-" * 50)
        for i, division in enumerate(divisions, 1):
            print(f"{i:3d}. {division}")
    else:
        print("No divisions found or error occurred.")

if __name__ == "__main__":
    # Example usage
    print_unique_divisions()
    
    # Create JSON file
    print("\n" + "="*50)
    create_divisions_json()
