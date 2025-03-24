# gen_qr.py
# v.24.03.2025.01b
# Filip Pawlowski 2023
# filippawlowski2012@gmail.com

import os
import qrcode
import warnings


def generate_qr_code(data, qr_code_path):
    """
    Generates a QR code from the given data and saves it to the specified path.

    Args:
        data (str or bytes): The data to encode in the QR code.
        qr_code_path (str): The file path to save the generated QR code image.
    """
    qr = qrcode.QRCode(
        version=1,  # Controls the size of the QR Code
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
        box_size=10,  # Size of each box in the QR code
        border=4,  # Thickness of the border (minimum is 4)
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Suppress warnings while generating the image
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)
        qr_code_img = qr.make_image(fill_color="black", back_color="white")

    # Save the QR code to the specified path
    qr_code_img.save(qr_code_path)
    print(f"QR Code has been generated and saved to {qr_code_path}")


def generate_qr_code_from_file():
    """
    Prompts the user to enter a file path and generates a QR code from the file's content.
    """
    file_path = input("Enter the file path: ").strip()
    if not os.path.isfile(file_path):
        print("The specified file does not exist.")
        return

    # Derive the output file path for the QR code
    file_directory = os.path.dirname(file_path)
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    qr_code_path = os.path.join(file_directory, f"{file_name}_qr.png")

    # Read the file's content
    with open(file_path, "r", encoding="utf-8") as file:
        file_data = file.read()

    generate_qr_code(file_data, qr_code_path)


def generate_qr_code_from_text():
    """
    Prompts the user to enter text and a file path to generate a QR code.
    """
    text = input("Enter the text: ").strip()
    qr_code_path = input("Enter the output file path for the QR code (e.g., 'output.png'): ").strip()

    if not qr_code_path:
        print("You must specify an output file path.")
        return

    generate_qr_code(text, qr_code_path)


# Main program loop
def main():
    while True:
        print("\nChoose an option (1-3):")
        print("1. Generate from file")
        print("2. Generate from text")
        print("3. Exit")

        choice = input(">>> ").strip()

        if choice == "1":
            generate_qr_code_from_file()
        elif choice == "2":
            generate_qr_code_from_text()
        elif choice == "3":
            print("Program terminated.")
            break
        else:
            print("Invalid choice. Please select an option from 1 to 3.")


if __name__ == "__main__":
    main()
