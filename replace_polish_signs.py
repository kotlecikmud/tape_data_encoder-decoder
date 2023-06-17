import os


def convert_text(text, convert_type):
    if convert_type == 'PL2':
        replacements_dictionary = {
            'ą': '<a>',
            'ć': '<c>',
            'ę': '<e>',
            'ł': '<l>',
            'ń': '<n>',
            'ó': '<o>',
            'ś': '<s>',
            'ź': '<zi>',
            'ż': '<z>',
            'Ą': '<A>',
            'Ć': '<C>',
            'Ę': '<E>',
            'Ł': '<L>',
            'Ń': '<N>',
            'Ó': '<O>',
            'Ś': '<S>',
            'Ź': '<ZI>',
            'Ż': '<Z>'
        }
    elif convert_type == '2PL':
        replacements_dictionary = {
            '<a>': 'ą',
            '<c>': 'ć',
            '<e>': 'ę',
            '<l>': 'ł',
            '<n>': 'ń',
            '<o>': 'ó',
            '<s>': 'ś',
            '<zi>': 'ź',
            '<z>': 'ż',
            '<A>': 'Ą',
            '<C>': 'Ć',
            '<E>': 'Ę',
            '<L>': 'Ł',
            '<N>': 'Ń',
            '<O>': 'Ó',
            '<S>': 'Ś',
            '<ZI>': 'Ź',
            '<Z>': 'Ż'
        }

    for character, replacement in replacements_dictionary.items():
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
