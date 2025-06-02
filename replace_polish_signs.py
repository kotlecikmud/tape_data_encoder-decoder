import os
import re

# Define replacements_dictionary at the module level
REPLACEMENTS_DICTIONARY = {
    "\u0105": r"'\u0105'",
    "\u0107": r"'\u0107'",
    "\u0119": r"'\u0119'",
    "\u0142": r"'\u0142'",
    "\u0144": r"'\u0144'",
    "\u00F3": r"'\u00F3'",
    "\u015B": r"'\u015B'",
    "\u017A": r"'\u017A'",
    "\u017C": r"'\u017C'",
    "\u0104": r"'\u0104'",
    "\u0106": r"'\u0106'",
    "\u0118": r"'\u0118'",
    "\u0141": r"'\u0141'",
    "\u0143": r"'\u0143'",
    "\u00D3": r"'\u00D3'",
    "\u015A": r"'\u015A'",
    "\u0179": r"'\u0179'",
    "\u017B": r"'\u017B'",
}


def convert_text(text, convert_type):
    """
    Converts text by replacing Polish characters with their ASCII representations or vice versa.
    'PL2' converts Polish characters to ASCII representations.
    '2PL' converts ASCII representations back to Polish characters.
    """
    dictionary_to_use = None
    if convert_type == "PL2":
        dictionary_to_use = REPLACEMENTS_DICTIONARY
        for character, replacement in dictionary_to_use.items():
            text = text.replace(character, replacement)
    elif convert_type == "2PL":
        reversed_dictionary = {v: k for k, v in REPLACEMENTS_DICTIONARY.items()}
        # Regex to find all occurrences of "'\\uXXXX'"
        pattern = re.compile(r"'\\u[0-9A-Fa-f]{4}'")

        # Use a function for replacement to handle cases where a match might not be in the dictionary
        def replace_match(match):
            return reversed_dictionary.get(match.group(0), match.group(0))

        text = pattern.sub(replace_match, text)
    else:
        # Handle invalid convert_type if necessary, or assume valid input
        print(
            f"Warning: Invalid conversion type '{convert_type}' passed to convert_text."
        )
        return text  # Or raise an error

    return text


def process_file(input_path, output_path, conversion_type):
    """
    Reads content from input_path, converts it using convert_text,
    and writes the result to output_path with an appropriate prefix.
    Returns True on success, False on failure.
    """
    try:
        with open(input_path, "r", encoding="utf-8") as input_file:
            text = input_file.read()

        output_prefix = ""
        if conversion_type == "PL2":
            converted_text = convert_text(text, "PL2")
            output_prefix = "<--PL\n"
        elif conversion_type == "2PL":
            if text.startswith("<--PL"):  # Remove header only if converting back to PL
                text = text[len("<--PL\n") :]
            converted_text = convert_text(text, "2PL")
            output_prefix = "PL-->\n"  # Typically not needed for restored PL text, but kept for consistency if desired
        else:
            print(
                f"Error: Invalid conversion_type '{conversion_type}' for process_file."
            )
            return False

        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write(output_prefix + converted_text)

        print(f"File processing successful. Result saved in: {output_path}")
        return True
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
        return False
    except Exception as e:
        print(f"An error occurred during file processing: {e}")
        return False


if __name__ == "__main__":
    while True:
        conversion_type_choice = input(
            "Choose conversion type:\n(1) Remove_PL (PL to ASCII)\n(2) Restore_PL (ASCII to PL)\n(3) Exit\n>>> "
        )

        input_path = input("Enter the input file path: ")

        base_name = os.path.basename(input_path)
        dir_name = os.path.dirname(input_path)

        output_name = ""
        actual_conversion_type = ""

        if conversion_type_choice == "1":
            output_name = "removed_" + base_name
            actual_conversion_type = "PL2"
        elif conversion_type_choice == "2":
            output_name = "restored_" + base_name
            actual_conversion_type = "2PL"
        elif conversion_type_choice == "3":
            exit(0)
        else:
            print("Invalid conversion type selected.")
            exit()

        output_path = os.path.join(dir_name, output_name)

        if process_file(input_path, output_path, actual_conversion_type):
            print("Standalone conversion completed.")
        else:
            print("Standalone conversion failed.")
