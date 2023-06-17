# base64encoder.py
# Filip Pawlowski 2023
# filippawlowski2012@gmail.com

import os
import base64

def read_file(file_path):
    with open(file_path, 'rb') as file:
        binary_data = file.read()
    return binary_data

def write_base64_data(base64_data, output_path):
    with open(output_path, 'w') as file:
        file.write(base64_data)

def write_file(binary_data, output_path):
    with open(output_path, 'wb') as file:
        file.write(binary_data)

def main():
    # Define file path
    file_path = input('Provide file path: ')

    # Extract file name from the file path
    file_name = os.path.basename(file_path)

    user_choice = input('1 - Encode\n2 - Decode: ')

    # Read binary data from the file
    binary_data = read_file(file_path)

    if user_choice == '1':
        # Encode binary data to Base64
        base64_data = base64.b64encode(binary_data).decode('utf-8')

        # Write Base64 data to a file
        base64_data_output_path = f'{file_name}_base64_data.txt'
        write_base64_data(base64_data, base64_data_output_path)
        print("Base64 data saved as:", base64_data_output_path)

    elif user_choice == '2':
        # Decode Base64 data back to binary
        decoded_data = base64.b64decode(binary_data)

        # Write binary data back to a file
        output_path = 'reconstructed_file.file'
        write_file(decoded_data, output_path)
        print("Reconstructed file saved as:", output_path)

if __name__ == '__main__':
    main()