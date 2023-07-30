import os
import re

def convert_text(text, convert_type):
    replacements_dictionary = {
        'ą': r"'\u0105'",
        'ć': r"'\u0107'",
        'ę': r"'\u0119'",
        'ł': r"'\u0142'",
        'ń': r"'\u0144'",
        'ó': r"'\u00F3'",
        'ś': r"'\u015B'",
        'ź': r"'\u017A'",
        'ż': r"'\u017C'",
        'Ą': r"'\u0104'",
        'Ć': r"'\u0106'",
        'Ę': r"'\u0118'",
        'Ł': r"'\u0141'",
        'Ń': r"'\u0143'",
        'Ó': r"'\u00D3'",
        'Ś': r"'\u015A'",
        'Ź': r"'\u0179'",
        'Ż': r"'\u017B'"
    }

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
