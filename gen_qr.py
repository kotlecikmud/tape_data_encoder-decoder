# gen_qr.py
# v.17.06.2023.01
# Filip Pawlowski 2023
# filippawlowski2012@gmail.com

import os, qrcode, warnings


def generate_qr_code(data, qr_code_path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)
        qr_code_img = qr.make_image(fill_color="black", back_color="white")

    qr_code_img.save(qr_code_path)
    print("QR Code has been generated and saved.")


def generate_qr_code_from_file():
    file_path = input("Enter the file path: ")
    if not os.path.isfile(file_path):
        print("The specified file does not exist.")
        return

    file_directory = os.path.dirname(file_path)
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    qr_code_path = os.path.join(file_directory, f"{file_name}_qr.png")

    with open(file_path, "rb") as file:
        file_data = file.read()

    generate_qr_code(file_data, qr_code_path)


def generate_qr_code_from_text():
    text = input("Enter the text: ")
    qr_code_path = input('output_path: ')
    generate_qr_code(text, qr_code_path)


while True:
    choice = input("Choose an option (1-3):\
    \n1. Generate from file\
    \n2. Generate from text\
    \n3. Exit\
    \n>>> ")

    if choice == "1":
        generate_qr_code_from_file()
    elif choice == "2":
        generate_qr_code_from_text()
    elif choice == "3":
        print("Program terminated.")
        break
    else:
        print("Invalid choice. Please select an option from 1 to 3.")
