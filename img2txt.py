"""
img2txt.py
Filip Pawlowski 2023
filippawlowski2012@gmail.com
"""

import os
import time
import math
import threading
from PIL import Image

__version__ = "1.1"


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

color_codes = {
    "ff0000": "R",  # Red
    "ffff00": "Y",  # Yellow
    "00ff00": "G",  # Green
    "0000ff": "B",  # Blue1
    "00ffff": "C",  # Cyan
    "ff00ff": "M",  # Violet
    "ffffff": "W",  # White
    "000000": "D",  # Black
    "ff8000": "O",  # Orange
    "0080ff": "N",  # Blue2
    "800080": "P"  # Magenta
}


def encode(image_path):
    loading_animation.start()

    image = Image.open(image_path)
    image = image.convert("RGB")
    width, height = image.size

    quantized_data = []
    current_color = None
    color_count = 0

    for y in range(height):
        for x in range(width):
            rgb = image.getpixel((x, y))
            closest_color = min(color_codes.keys(),
                                key=lambda c: math.dist(rgb, tuple((int(c[i:i + 2], 16)) for i in (0, 2, 4))))
            hex_code = closest_color

            color = color_codes[hex_code]
            if color == current_color:
                color_count += 1
            else:
                if current_color:
                    quantized_data.append((color_count, current_color))
                current_color = color
                color_count = 1

    quantized_data.append((color_count, current_color))

    file_name_in = os.path.splitext(os.path.basename(image_path))[0]
    output_filename = file_name_in + '_encoded.txt'
    output_filepath = os.path.join(os.path.dirname(image_path), output_filename)
    with open(output_filepath, "w") as f:
        f.write(f"#---\n{width}x{height}x{file_name_in}\n#---\n")
        for count, color in quantized_data:
            f.write(f"{count}{color}")
        f.write("\n#---\n")

    loading_animation.stop()

    print(f"Quantized image saved to {output_filepath}")


def decode(txt_path):
    loading_animation.start()

    with open(txt_path, "r") as f:
        lines = f.readlines()

    width, height, file_name_out = lines[1].strip().split("x")
    width = int(width)
    height = int(height)

    encoded_data = lines[3].strip()
    decoded_data = ""

    i = 0
    while i < len(encoded_data):
        count_str = ""
        while encoded_data[i].isdigit():
            count_str += encoded_data[i]
            i += 1

        color = encoded_data[i]
        count = int(count_str)
        decoded_data += count * color
        i += 1

    image = Image.new("RGB", (width, height))
    pixels = []
    for char in decoded_data:
        hex_code = [key for key, value in color_codes.items() if value == char][0]
        rgb = tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))
        pixels.append(rgb)

    image.putdata(pixels)

    output_filename = file_name_out + ".png"
    output_filepath = os.path.join(os.path.dirname(txt_path), output_filename)
    image.save(output_filepath)

    loading_animation.stop()

    print(f'Decoded image saved to {output_filepath}')

    return output_filename


output_filename = ''

while True:
    # Menu wyboru opcji
    choice = input(f"img2wav {__version__}\nChoose option (1-3):\n1) Encode\n2) Decode\n3) Exit\n>>>")

    if choice == "1":
        image_path = input("Provide the path to the image file: ")
        encode(image_path)

    elif choice == "2":
        txt_path = input("Enter the path to the txt file: ")
        decode(txt_path)

    elif choice == "3":
        break

    else:
        print("Invalid choice.")
