"""
img2txt.py
Filip Pawlowski 2023
filippawlowski2012@gmail.com
"""

__version__ = "00.01.02.00"

import os
import time
import math
import threading
from PIL import Image

SEPARATOR = "####"


class LoadingAnimation:
    def __init__(self):
        self.animation_signs = ['|....', '.|...', '..|..', '...|.', '....|', '...|.', '..|..', '.|...']
        self.sign_index = 0
        self.finished = False

    def start(self):
        self.finished = False
        self._animate_thread = threading.Thread(target=self._animate)
        self._animate_thread.start()

    def stop(self):
        self.finished = True
        self._animate_thread.join()

    def _animate(self):
        while not self.finished:
            print(self.animation_signs[self.sign_index % len(self.animation_signs)], end='\r')
            time.sleep(0.1)
            self.sign_index += 1


# Instantiate LoadingAnimation class
loading_animation = LoadingAnimation()

# Color Mode Dictionaries
COLOR_MODES = {
    # Monochromatic 2-bit (Black, Dark Gray, Light Gray, White)
    "MONO": {
        "000000": "MA",  # Black
        "555555": "MB",  # Dark Gray
        "AAAAAA": "MC",  # Light Gray
        "FFFFFF": "MD"  # White
    },
    # 8-bit RGB/CMY/White/Black
    "COLOR": {
        "FF0000": "CR",  # Red
        "00FF00": "CG",  # Green
        "0000FF": "CB",  # Blue
        "FFFF00": "CY",  # Yellow
        "00FFFF": "CC",  # Cyan
        "FF00FF": "CM",  # Magenta
        "FFFFFF": "CW",  # White
        "000000": "CD"  # Black
    },
    # Extended Monochrome - 16 shades of grayscale
    "MONO_EXTENDED": {
        "000000": "MA",  # Black
        "111111": "ME",  # Very Dark Gray
        "222222": "MF",  # Dark Gray
        "333333": "MG",  # Darker Medium Gray
        "444444": "MH",  # Medium Dark Gray
        "555555": "MB",  # Medium Gray
        "666666": "MI",  # Medium Light Gray
        "777777": "MJ",  # Light Medium Gray
        "888888": "MK",  # Light Gray
        "999999": "ML",  # Lighter Gray
        "AAAAAA": "MC",  # Very Light Gray
        "BBBBBB": "MN",  # Almost White
        "CCCCCC": "MP",  # Nearly White
        "DDDDDD": "MR",  # Off White
        "EEEEEE": "MS",  # Near White
        "FFFFFF": "MD"  # Pure White
    },
    # Extended 20-color palette
    "COLOR_EXTENDED": {
        "FF0000": "CR",  # Red
        "FFFF00": "CY",  # Yellow
        "00FF00": "CG",  # Green
        "0000FF": "CB",  # Blue
        "00FFFF": "CC",  # Cyan
        "FF00FF": "CM",  # Violet
        "FFFFFF": "CW",  # White
        "000000": "CD",  # Black
        "FF8000": "CO",  # Orange
        "0080FF": "CM",  # Blue2
        "800080": "CP",  # Magenta
        "808080": "CH",  # Gray
        "FFC0CB": "CK",  # Pink
        "A52A2A": "CA",  # Brown
        "008000": "CE",  # Dark Green
        "4B0082": "CI",  # Indigo
        "FFA500": "CF",  # Bright Orange
        "808000": "CJ",  # Olive
        "C71585": "CL",  # Medium Violet Red
        "40E0D0": "CT"  # Turquoise
    }
}


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def find_closest_color(rgb, color_mode):
    """Find the closest color in the selected color mode."""
    color_codes = COLOR_MODES[color_mode]
    return min(color_codes.keys(),
               key=lambda c: math.dist(rgb, tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))))


def encode(image_path, mode='COLOR'):
    """
    Encode image with specified color mode.

    Args:
        image_path (str): Path to the input image
        mode (str): Color mode to use - 'MONO', 'RGB_CMY', or 'EXTENDED'
    """
    loading_animation.start()

    # Validate mode
    if mode not in COLOR_MODES:
        print(f"Invalid mode. Choose from {list(COLOR_MODES.keys())}")
        return

    image = Image.open(image_path)
    image = image.convert("RGB")
    width, height = image.size
    total_pixels = width * height

    quantized_data = []
    current_color = None
    color_count = 0
    color_codes = COLOR_MODES[mode]

    for y in range(height):
        for x in range(width):
            rgb = image.getpixel((x, y))
            hex_code = find_closest_color(rgb, mode)
            color = color_codes[hex_code]

            if color == current_color:
                color_count += 1
            else:
                if current_color:
                    quantized_data.append((color_count, current_color))
                current_color = color
                color_count = 1

            # Calculate and print progress
            current_pixel = y * width + x + 1
            progress = (current_pixel / total_pixels) * 100
            print(f"Encoding progress: {progress:.2f}%", end="\r")

    quantized_data.append((color_count, current_color))

    file_name_in = os.path.splitext(os.path.basename(image_path))[0]
    output_filename = f"{file_name_in}_encoded_{mode}.txt"
    output_filepath = os.path.join(os.path.dirname(image_path), output_filename)

    print("writing file...")
    with open(output_filepath, "w") as f:
        f.write(f"{SEPARATOR}\n{width}{SEPARATOR}{height}{SEPARATOR}{file_name_in}{SEPARATOR}{mode}\n{SEPARATOR}\n")
        for count, color in quantized_data:
            f.write(f"{count}{color}")
        f.write(f"\n{SEPARATOR}\n")

    loading_animation.stop()
    print(f"\nQuantized image saved to {output_filepath}")


def decode(txt_path):
    """Decode an encoded text file back to an image"""
    with open(txt_path, "r") as f:
        lines = f.readlines()

    # Parse the header
    header = lines[1].strip().split("####")
    width, height, file_name_out, mode = header[0], header[1], header[2], header[3]
    width = int(width)
    height = int(height)

    # Validate mode
    if mode not in COLOR_MODES:
        print(f"Invalid mode. Choose from {list(COLOR_MODES.keys())}")
        return

    color_codes = COLOR_MODES[mode]

    # Parse the encoded data
    encoded_data = lines[3].strip()
    decoded_data = []

    total_length = len(encoded_data)
    i = 0

    while i < total_length:
        # Extract count (digits) and color code
        count_str = ""
        while i < total_length and encoded_data[i].isdigit():
            count_str += encoded_data[i]
            i += 1

        if i >= total_length:
            break

        # Handle multi-character color codes
        color = encoded_data[i:i + 2]
        i += 2

        try:
            count = int(count_str) if count_str else 1
            count = min(count, width * height)
        except ValueError:
            print(f"Warning: Invalid count value '{count_str}'. Skipping.")
            continue

        decoded_data.extend([color] * count)

        # Print progress
        progress = (i / total_length) * 100
        print(f"Decoding progress: {progress:.2f}%", end="\r")

    print("Truncate or pad to match the total pixel count")
    total_pixels = width * height
    if len(decoded_data) > total_pixels:
        decoded_data = decoded_data[:total_pixels]
    elif len(decoded_data) < total_pixels:
        last_color = decoded_data[-1] if decoded_data else list(color_codes.values())[0]
        decoded_data.extend([last_color] * (total_pixels - len(decoded_data)))

    print("Map color codes to RGB values")
    pixels = []
    for char in decoded_data:
        matching_hex = next((hex_code for hex_code, code in color_codes.items() if code == char), "000000")
        rgb = tuple(int(matching_hex[i:i + 2], 16) for i in (0, 2, 4))
        pixels.append(rgb)

    print("Create and save the image")
    image = Image.new("RGB", (width, height))
    image.putdata(pixels)

    output_filename = f"{file_name_out}_{mode}.png"
    output_filepath = os.path.join(os.path.dirname(txt_path), output_filename)
    image.save(output_filepath)

    print(f'\nDecoded image saved to {output_filepath}')
    return output_filename


def main():
    while True:
        # Menu selection
        # clear_terminal()
        choice = input(f"img2txt {__version__}\nChoose option (1-4):\n"
                       "1) Encode Image\n"
                       "2) Decode Encoded File\n"
                       "3) Exit\n>>>")

        if choice == "1":
            image_path = input("Provide the path to the image file: ")
            mode = input("Choose color mode (default=COLOR):\
            \n1-MONO\
            \n2-MONO_EXTENDED\
            \n3-COLOR\
            \n4-COLOR_EXTENDED\
            \n>>> ")

            modes = {
                "1": "MONO",
                "2": "MONO_EXTENDED",
                "3": "COLOR",
                "4": "COLOR_EXTENDED"
            }

            selected_mode = modes.get(mode, "COLOR")
            encode(image_path, selected_mode)

        elif choice == "2":
            txt_path = input("Enter the path to the txt file: ")
            decode(txt_path)

        elif choice == "3":
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
