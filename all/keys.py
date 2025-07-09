import json
import os
import re

def update_competitor_names_with_longest():
    """
    Updates the competitor_names.json file so that the longest name in each array becomes the key.
    This helps standardize the naming by using the most complete version of each name.
    """
    
    # Path to the competitor names file
    file_path = os.path.join('keys', 'competitor_names.json')
    
    # Read the current JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        competitor_data = json.load(f)
    
    # Create new dictionary with longest names as keys
    updated_data = {}
    changes_made = 0
    
    for current_key, name_array in competitor_data.items():
        if not name_array:  # Skip empty arrays
            continue
            
        # Find the longest name in the array
        longest_name = max(name_array, key=len)
        
        # If the longest name is different from the current key, update it
        if longest_name != current_key:
            changes_made += 1
            print(f"Updating: '{current_key}' -> '{longest_name}'")
        
        # Use the longest name as the new key
        updated_data[longest_name] = name_array
    
    # Write the updated data back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nProcess completed! {changes_made} keys were updated.")
    print(f"Total entries: {len(updated_data)}")
    
    return updated_data

def preview_changes():
    """
    Preview what changes would be made without actually updating the file.
    """
    
    file_path = os.path.join('keys', 'competitor_names.json')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        competitor_data = json.load(f)
    
    changes = []
    
    for current_key, name_array in competitor_data.items():
        if not name_array:
            continue
            
        longest_name = max(name_array, key=len)
        
        if longest_name != current_key:
            changes.append({
                'old_key': current_key,
                'new_key': longest_name,
                'names': name_array
            })
    
    print(f"Would update {len(changes)} keys:")
    print("-" * 50)
    
    for i, change in enumerate(changes[:10]):  # Show first 10 changes
        print(f"{i+1}. '{change['old_key']}' -> '{change['new_key']}'")
        print(f"   Names: {change['names']}")
        print()
    
    if len(changes) > 10:
        print(f"... and {len(changes) - 10} more changes")
    
    return changes

def clean_competitor_names():
    """
    Cleans up competitor name keys by:
    - Converting to lowercase
    - Replacing whitespace with underscores
    - Removing commas, periods, quotes, backticks, etc.
    - Removing parentheses but keeping numbers inside them
    
    Note: Only the keys are cleaned, the names in the arrays remain unchanged.
    """
    
    # Path to the competitor names file
    file_path = os.path.join('keys', 'competitor_names.json')
    
    # Read the current JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        competitor_data = json.load(f)
    
    # Create new dictionary with cleaned keys
    cleaned_data = {}
    changes_made = 0
    
    for current_key, name_array in competitor_data.items():
        # Clean only the key
        cleaned_key = clean_name(current_key)
        
        # Keep the original names in the array unchanged
        cleaned_names = name_array
        
        # If the cleaned key is different from the current key, note the change
        if cleaned_key != current_key:
            changes_made += 1
            print(f"Cleaning key: '{current_key}' -> '{cleaned_key}'")
        
        # Use the cleaned key but keep original names
        cleaned_data[cleaned_key] = cleaned_names
    
    # Write the cleaned data back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nProcess completed! {changes_made} keys were cleaned.")
    print(f"Total entries: {len(cleaned_data)}")
    
    return cleaned_data

def clean_name(name):
    """
    Cleans a single name according to the specified rules.
    """
    # Convert to lowercase
    cleaned = name.lower()
    
    # Remove parentheses but keep numbers inside them
    # This regex finds (number) and replaces with just the number
    cleaned = re.sub(r'\((\d+)\)', r'\1', cleaned)
    
    # Replace whitespace with underscores
    cleaned = re.sub(r'\s+', '_', cleaned)
    
    # Replace hyphens with underscores
    cleaned = cleaned.replace('-', '_')
    
    # Remove specific punctuation characters: commas, periods, quotes, backticks
    # Also remove other common punctuation that might cause issues
    cleaned = re.sub(r'[,\.\'"`!@#$%^&*()\[\]{}|\\:;<>?/~`]', '', cleaned)
    
    # Remove any remaining parentheses (in case there were any without numbers)
    cleaned = cleaned.replace('(', '').replace(')', '')
    
    # Remove any multiple consecutive underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    
    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    
    return cleaned

def replace_hyphens_with_underscores():
    """
    Replaces hyphens with underscores in competitor name keys.
    Only affects the keys, not the names in the arrays.
    """
    
    # Path to the competitor names file
    file_path = os.path.join('keys', 'competitor_names.json')
    
    # Read the current JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        competitor_data = json.load(f)
    
    # Create new dictionary with hyphens replaced
    updated_data = {}
    changes_made = 0
    
    for current_key, name_array in competitor_data.items():
        # Replace hyphens with underscores in the key
        updated_key = current_key.replace('-', '_')
        
        # If the key changed, note the change
        if updated_key != current_key:
            changes_made += 1
            print(f"Replacing hyphens: '{current_key}' -> '{updated_key}'")
        
        # Use the updated key but keep original names
        updated_data[updated_key] = name_array
    
    # Write the updated data back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nProcess completed! {changes_made} keys had hyphens replaced with underscores.")
    print(f"Total entries: {len(updated_data)}")
    
    return updated_data

def preview_hyphen_replacement():
    """
    Preview what hyphen replacement would look like without actually updating the file.
    """
    
    file_path = os.path.join('keys', 'competitor_names.json')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        competitor_data = json.load(f)
    
    print("Preview of hyphen replacement:")
    print("-" * 60)
    
    changes = []
    
    for current_key, name_array in competitor_data.items():
        updated_key = current_key.replace('-', '_')
        
        if updated_key != current_key:
            changes.append({
                'old_key': current_key,
                'new_key': updated_key,
                'names': name_array[:3]  # Show first 3 names
            })
    
    # Show first 20 changes
    for i, change in enumerate(changes[:20]):
        print(f"{i+1}. '{change['old_key']}' -> '{change['new_key']}'")
        print(f"   Names: {change['names']}")
        print()
    
    if len(changes) > 20:
        print(f"... and {len(changes) - 20} more changes")
    
    print(f"Total keys that would be changed: {len(changes)}")
    
    return changes

def clean_multiple_underscores():
    """
    Replaces multiple consecutive underscores with single underscores in competitor name keys.
    Only affects the keys, not the names in the arrays.
    """
    
    # Path to the competitor names file
    file_path = os.path.join('keys', 'competitor_names.json')
    
    # Read the current JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        competitor_data = json.load(f)
    
    # Create new dictionary with cleaned underscores
    updated_data = {}
    changes_made = 0
    
    for current_key, name_array in competitor_data.items():
        # Replace multiple consecutive underscores with single underscore
        updated_key = re.sub(r'_+', '_', current_key)
        
        # If the key changed, note the change
        if updated_key != current_key:
            changes_made += 1
            print(f"Cleaning underscores: '{current_key}' -> '{updated_key}'")
        
        # Use the updated key but keep original names
        updated_data[updated_key] = name_array
    
    # Write the updated data back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nProcess completed! {changes_made} keys had multiple underscores cleaned.")
    print(f"Total entries: {len(updated_data)}")
    
    return updated_data

def preview_multiple_underscore_cleaning():
    """
    Preview what multiple underscore cleaning would look like without actually updating the file.
    """
    
    file_path = os.path.join('keys', 'competitor_names.json')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        competitor_data = json.load(f)
    
    print("Preview of multiple underscore cleaning:")
    print("-" * 60)
    
    changes = []
    
    for current_key, name_array in competitor_data.items():
        updated_key = re.sub(r'_+', '_', current_key)
        
        if updated_key != current_key:
            changes.append({
                'old_key': current_key,
                'new_key': updated_key,
                'names': name_array[:3]  # Show first 3 names
            })
    
    # Show first 20 changes
    for i, change in enumerate(changes[:20]):
        print(f"{i+1}. '{change['old_key']}' -> '{change['new_key']}'")
        print(f"   Names: {change['names']}")
        print()
    
    if len(changes) > 20:
        print(f"... and {len(changes) - 20} more changes")
    
    print(f"Total keys that would be changed: {len(changes)}")
    
    return changes

def preview_name_cleaning():
    """
    Preview what the key cleaning would look like without actually updating the file.
    Only the keys are cleaned, the names in arrays remain unchanged.
    """
    
    file_path = os.path.join('keys', 'competitor_names.json')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        competitor_data = json.load(f)
    
    print("Preview of key cleaning (names in arrays remain unchanged):")
    print("-" * 80)
    
    # Show first 20 examples
    count = 0
    for current_key, name_array in competitor_data.items():
        if count >= 20:
            break
            
        cleaned_key = clean_name(current_key)
        
        print(f"Key: '{current_key}' -> '{cleaned_key}'")
        print(f"Names (unchanged): {name_array[:3]}")
        print()
        count += 1
    
    print(f"... and {len(competitor_data) - 20} more entries would be processed")

def clean_competitor_name_keys():
    """
    Cleans the keys in competitor_names.json by:
    - Converting to lowercase
    - Replacing whitespace with underscores
    - Removing . , ( ) ' ` characters
    - Replacing hyphens with underscores
    - Removing multiple consecutive underscores
    
    Only affects the keys, not the values in the arrays.
    """
    
    # Path to the competitor names file
    file_path = os.path.join('keys', 'competitor_names.json')
    
    # Read the current JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        competitor_data = json.load(f)
    
    # Create new dictionary with cleaned keys
    cleaned_data = {}
    changes_made = 0
    
    for current_key, name_array in competitor_data.items():
        # Clean the key according to specifications
        cleaned_key = clean_competitor_key(current_key)
        
        # If the cleaned key is different from the current key, note the change
        if cleaned_key != current_key:
            changes_made += 1
            print(f"Cleaning key: '{current_key}' -> '{cleaned_key}'")
        
        # Use the cleaned key but keep original names in array
        cleaned_data[cleaned_key] = name_array
    
    # Write the cleaned data back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nProcess completed! {changes_made} keys were cleaned.")
    print(f"Total entries: {len(cleaned_data)}")
    
    return cleaned_data

def clean_competitor_key(key):
    """
    Cleans a single competitor key according to the specified rules:
    - Convert to lowercase
    - Replace whitespace with underscores
    - Remove . , ( ) ' ` characters
    - Replace hyphens with underscores
    - Remove multiple consecutive underscores
    """
    # Convert to lowercase
    cleaned = key.lower()
    
    # Replace hyphens with underscores
    cleaned = cleaned.replace('-', '_')
    
    # Replace whitespace with underscores
    cleaned = re.sub(r'\s+', '_', cleaned)
    
    # Remove specific punctuation characters: . , ( ) ' `
    cleaned = re.sub(r'[.,()\'`]', '', cleaned)
    
    # Remove any multiple consecutive underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    
    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    
    return cleaned

def preview_competitor_key_cleaning():
    """
    Preview what the competitor key cleaning would look like without actually updating the file.
    """
    
    file_path = os.path.join('keys', 'competitor_names.json')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        competitor_data = json.load(f)
    
    print("Preview of competitor key cleaning:")
    print("-" * 80)
    
    changes = []
    
    for current_key, name_array in competitor_data.items():
        cleaned_key = clean_competitor_key(current_key)
        
        if cleaned_key != current_key:
            changes.append({
                'old_key': current_key,
                'new_key': cleaned_key,
                'names': name_array[:3]  # Show first 3 names
            })
    
    # Show first 20 changes
    for i, change in enumerate(changes[:20]):
        print(f"{i+1}. '{change['old_key']}' -> '{change['new_key']}'")
        print(f"   Names: {change['names']}")
        print()
    
    if len(changes) > 20:
        print(f"... and {len(changes) - 20} more changes")
    
    print(f"Total keys that would be changed: {len(changes)}")
    
    return changes

def clean_competition_name_keys():
    """
    Cleans the keys in competition_names.json by:
    - Converting to lowercase
    - Replacing whitespace with underscores
    - Removing . , ( ) ' ` characters
    - Replacing hyphens with underscores
    - Removing multiple consecutive underscores
    
    Only affects the keys, not the values in the arrays.
    """
    
    # Path to the competition names file
    file_path = os.path.join('keys', 'competition_names.json')
    
    # Read the current JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        competition_data = json.load(f)
    
    # Create new dictionary with cleaned keys
    cleaned_data = {}
    changes_made = [0]  # Use a list to allow modification in nested function
    
    def clean_nested_keys(data):
        """Recursively clean keys in nested dictionaries"""
        if isinstance(data, dict):
            cleaned_dict = {}
            for key, value in data.items():
                # Clean the key
                cleaned_key = clean_competition_key(key)
                
                # If the cleaned key is different from the current key, note the change
                if cleaned_key != key:
                    changes_made[0] += 1
                    print(f"Cleaning key: '{key}' -> '{cleaned_key}'")
                
                # Recursively clean nested dictionaries
                if isinstance(value, dict):
                    cleaned_dict[cleaned_key] = clean_nested_keys(value)
                else:
                    cleaned_dict[cleaned_key] = value
            return cleaned_dict
        else:
            return data
    
    # Clean all keys recursively
    cleaned_data = clean_nested_keys(competition_data)
    
    # Write the cleaned data back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nProcess completed! {changes_made[0]} keys were cleaned.")
    print(f"Total entries processed.")
    
    return cleaned_data

def clean_competition_key(key):
    """
    Cleans a single competition key according to the specified rules:
    - Convert to lowercase
    - Replace whitespace with underscores
    - Remove . , ( ) ' ` characters
    - Replace hyphens with underscores
    - Remove multiple consecutive underscores
    """
    # Convert to lowercase
    cleaned = key.lower()
    
    # Replace hyphens with underscores
    cleaned = cleaned.replace('-', '_')
    
    # Replace whitespace with underscores
    cleaned = re.sub(r'\s+', '_', cleaned)
    
    # Remove specific punctuation characters: . , ( ) ' `
    cleaned = re.sub(r'[.,()\'`]', '', cleaned)
    
    # Remove any multiple consecutive underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    
    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    
    return cleaned

def preview_competition_key_cleaning():
    """
    Preview what the competition key cleaning would look like without actually updating the file.
    """
    
    file_path = os.path.join('keys', 'competition_names.json')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        competition_data = json.load(f)
    
    print("Preview of competition key cleaning:")
    print("-" * 80)
    
    changes = []
    
    def preview_nested_keys(data, path=""):
        """Recursively preview key changes in nested dictionaries"""
        if isinstance(data, dict):
            for key, value in data.items():
                cleaned_key = clean_competition_key(key)
                current_path = f"{path}.{key}" if path else key
                
                if cleaned_key != key:
                    changes.append({
                        'path': current_path,
                        'old_key': key,
                        'new_key': cleaned_key
                    })
                
                # Recursively check nested dictionaries
                if isinstance(value, dict):
                    preview_nested_keys(value, current_path)
    
    # Preview all key changes
    preview_nested_keys(competition_data)
    
    # Show first 20 changes
    for i, change in enumerate(changes[:20]):
        print(f"{i+1}. '{change['old_key']}' -> '{change['new_key']}'")
        print(f"   Path: {change['path']}")
        print()
    
    if len(changes) > 20:
        print(f"... and {len(changes) - 20} more changes")
    
    print(f"Total keys that would be changed: {len(changes)}")
    
    return changes

if __name__ == "__main__":
    print("Previewing changes...")
    # Uncomment the line below to preview changes first
    # preview_changes()
    
    # Uncomment the line below to preview name cleaning first
    # preview_name_cleaning()
    
    # Uncomment the line below to preview hyphen replacement first
    # preview_hyphen_replacement()
    
    # Uncomment the line below to preview multiple underscore cleaning first
    # preview_multiple_underscore_cleaning()
    
    # Uncomment the line below to preview competitor key cleaning first
    # preview_competitor_key_cleaning()
    
    # Uncomment the line below to preview competition key cleaning first
    # preview_competition_key_cleaning()
    
    # Run the actual update
    # update_competitor_names_with_longest()
    
    # Run the name cleaning (includes hyphen replacement)
    # clean_competitor_names()
    
    # Run only hyphen replacement
    #replace_hyphens_with_underscores()
    
    # Run multiple underscore cleaning
    # clean_multiple_underscores()
    
    # Run competitor key cleaning (new function)
    # clean_competitor_name_keys()
    
    # Run competition key cleaning (new function)
    clean_competition_name_keys()
