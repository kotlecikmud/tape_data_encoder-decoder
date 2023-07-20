import json

def display_files_tree(data, indent=0):
    for entry in data:
        print("  " * indent + f"Cassette: {entry['cassette']}")
        print("  " * indent + f"Base: {entry['base']}")
        print("  " * indent + f"Section: {entry['section']}")
        for side_data in entry['data']:
            print("  " * indent + f"Side: {side_data['label']}")
            for file_info in side_data['files']:
                if file_info['name']:
                    print("  " * (indent + 1) + f"Index: {file_info['index']}, File: {file_info['name']}")
            print()  # Empty line for readability

def main():
    try:
        with open("tape_index.json", "r") as file:
            tape_data = json.load(file)
            display_files_tree(tape_data['entries'])
    except FileNotFoundError:
        print("Error: The file 'tape_index.json' was not found.")
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON data from the file.")

if __name__ == "__main__":
    main()
