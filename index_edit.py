import json
import argparse


def display_files_tree(data, indent=0):
    for entry in data:
        base = entry['base']
        if base is None:
            continue

        print("  " * indent + f"Cassette: {entry['cassette']}")
        print("  " * indent + f"Base: {base}")
        data_type = entry['data_type']
        if data_type is not None:
            print("  " * indent + f"data_type: {data_type}")

        for side_data in entry['data']:
            print("  " * indent + f"Side: {side_data['label']}")
            for file_info in side_data['files']:
                index = file_info['index']
                file_name = file_info['name']
                if index is not None and file_name is not None:
                    print("  " * (indent + 1) + f"Index: {index}, File: {file_name}")
            print()  # Empty line for readability


def export_tape_data(data, tape_number=None):
    for entry in data:
        if tape_number is None or entry['cassette'] == str(tape_number):
            base = entry['base']
            if base is None:
                print(f"Error: Cassette {entry['cassette']} has a None base and cannot be exported.")
                continue

            file_name = f"tape_{entry['cassette']}_data.txt"
            with open(file_name, "w") as export_file:
                export_file.write(f"Cassette: {entry['cassette']}\n")
                export_file.write(f"Base: {base}\n")
                data_type = entry['data_type']
                if data_type is not None:
                    export_file.write(f"data_type: {data_type}\n")

                for side_data in entry['data']:
                    export_file.write(f"Side: {side_data['label']}\n")
                    for file_info in side_data['files']:
                        index = file_info['index']
                        file_name = file_info['name']
                        if index is not None and file_name is not None:
                            export_file.write(f"Index: {index}, File: {file_name}\n")
                    export_file.write("\n")  # Empty line for readability
            print(f"Data for Cassette {entry['cassette']} has been exported to '{file_name}'.")


def insert_file_data(data, tape_number, index_range, file_name):
    for entry in data:
        if entry['cassette'] == str(tape_number):
            base = entry['base']
            if base is None:
                print(f"Error: Cassette {tape_number} has a None base and cannot be inserted.")
                return

            start_index, end_index = map(int, index_range.split('-'))
            for side_data in entry['data']:
                for index in range(start_index, end_index + 1):
                    new_file_entry = {"index": str(index), "name": file_name}
                    side_data['files'].append(new_file_entry)
            print(f"File '{file_name}' inserted into Cassette {tape_number}, Index Range: {start_index}-{end_index}.")
            return
    print(f"Error: Cassette {tape_number} not found in the data.")


def main():
    parser = argparse.ArgumentParser(description="Tape Index Parser")
    parser.add_argument("--export", nargs='?', const=None, type=int,
                        help="Export data associated with a tape specified by number. If no tape number is provided, export all tapes.")
    parser.add_argument("--insert", nargs=3, metavar=('TAPE_NUMBER', 'INDEX_RANGE', 'FILE_NAME'),
                        help="Insert file data into tape")
    args = parser.parse_args()

    try:
        with open("tape_index.json", "r") as file:
            tape_data = json.load(file)
            if args.export is not None:
                export_tape_data(tape_data['entries'], args.export)
            elif args.insert:
                tape_number, index_range, file_name = args.insert
                insert_file_data(tape_data['entries'], tape_number, index_range, file_name)
            else:
                display_files_tree(tape_data['entries'])
    except FileNotFoundError:
        print("Error: The file 'tape_index.json' was not found.")
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON data from the file.")


if __name__ == "__main__":
    main()
