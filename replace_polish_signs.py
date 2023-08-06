import os
import re


def convert_text(text, convert_type):
    replacements_dictionary = {
        '\u0105': r"'\u0105'",
        '\u0107': r"'\u0107'",
        '\u0119': r"'\u0119'",
        '\u0142': r"'\u0142'",
        '\u0144': r"'\u0144'",
        '\u00F3': r"'\u00F3'",
        '\u015B': r"'\u015B'",
        '\u017A': r"'\u017A'",
        '\u017C': r"'\u017C'",
        '\u0104': r"'\u0104'",
        '\u0106': r"'\u0106'",
        '\u0118': r"'\u0118'",
        '\u0141': r"'\u0141'",
        '\u0143': r"'\u0143'",
        '\u00D3': r"'\u00D3'",
        '\u015A': r"'\u015A'",
        '\u0179': r"'\u0179'",
        '\u017B': r"'\u017B'"
    }
    
    dictionary = None
    if convert_type == 'PL2':
        dictionary = replacements_dictionary
    elif convert_type == '2PL':
        dictionary = {v: k for k, v in replacements_dictionary.items()}
        pattern = re.compile(r"'\\u[0-9A-Fa-f]{4}'")
        matches = pattern.findall(text)
        for match in matches:
            text = text.replace(match, dictionary.get(match, match))
        return text

    for character, replacement in dictionary.items():
        text = text.replace(character, replacement)

    return text


conversion_type = input("Choose conversion type:\
\n(1) Remove_PL\
\n(2) Restore_PL\
\n>>>")

input_path = input("Enter the input file path: ")
input_name = os.path.basename(input_path)

conversion_map = {
    '1_Remove_PL': 'removed_',
    '1': 'removed_',
    '2_Restore_PL': 'restored_',
    '2': 'restored_'
}

if conversion_type in conversion_map:
    prefix = conversion_map[conversion_type]
    output_name = prefix + input_name

    with open(input_path, 'r', encoding='utf-8') as input_file:
        text = input_file.read()

    if conversion_type in ['1_Remove_PL', '1']:
        converted_text = convert_text(text, 'PL2')
        output_prefix = "<--PL\n"
    elif conversion_type in ['2_Restore_PL', '2']:
        if text.startswith("<--PL"):
            text = text[6:]  # Remove the header "<--PL"
        converted_text = convert_text(text, '2PL')
        output_prefix = "PL-->\n"

    output_path = os.path.join(os.path.dirname(input_path), output_name)
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(output_prefix + converted_text)

    print("Conversion completed. Result saved in the file:", output_path)
