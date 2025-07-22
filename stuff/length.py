import json

def count_keys_in_json(file_path):
    """Count the number of keys in a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        if isinstance(data, dict):
            key_count = len(data.keys())
            print(f"Number of keys in {file_path}: {key_count}")
            return key_count
        else:
            print(f"Error: The JSON file does not contain a dictionary/object")
            return None
            
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Count keys in athletes.json
    count_keys_in_json("athletes.json")
