"""
img2txt.py
Filip Pawlowski 2023
filippawlowski2012@gmail.com
"""

__version__ = "00.02.00.00"

import os
import time
import math
import threading
from PIL import Image

SEPARATOR = "####"
MODES = {
    "1": "MONO",
    "2": "MONO_EXTENDED",
    "3": "COLOR",
    "4": "COLOR_EXTENDED",
    "5": "RGB_SPLIT"
}


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


def encode_channel(channel, width, height, mode='MONO_EXTENDED'):
    """
    Encode a single image channel with quantization and progress tracking.
    """
    start_time = time.time()
    total_pixels = width * height
    quantized_data = []
    current_color = None
    color_count = 0
    color_codes = COLOR_MODES[mode]
    processed_pixels = 0

    for y in range(height):
        for x in range(width):
            pixel_value = channel.getpixel((x, y))
            hex_code = find_closest_color((pixel_value, pixel_value, pixel_value), mode)
            color = color_codes[hex_code]

            if color == current_color:
                color_count += 1
            else:
                if current_color:
                    quantized_data.append((color_count, current_color))
                current_color = color
                color_count = 1

            # Calculate progress and performance
            processed_pixels += 1
            current_time = time.time()
            elapsed_time = current_time - start_time
            pixels_per_second = processed_pixels / elapsed_time if elapsed_time > 0 else 0

            # Estimate time remaining
            remaining_pixels = total_pixels - processed_pixels
            estimated_time_left = remaining_pixels / pixels_per_second if pixels_per_second > 0 else 0

            # Format output
            progress = (processed_pixels / total_pixels) * 100
            print(
                f"Encoding {color} channel: {progress:.2f}% | {pixels_per_second:.0f} px/sec | Est. {format_time(estimated_time_left)} left",
                end="\r")

    quantized_data.append((color_count, current_color))
    return quantized_data


def encode(image_path, mode='COLOR'):
    """
    Encode image with specified color mode.

    Args:
        image_path (str): Path to the input image
        mode (str): Color mode to use
    """
    loading_animation.start()

    # Validate mode
    if mode not in COLOR_MODES and mode != "RGB_SPLIT":
        print(f"Invalid mode. Choose from {list(COLOR_MODES.keys()) + ['RGB_SPLIT']}")
        return

    image = Image.open(image_path)
    image = image.convert("RGB")
    width, height = image.size

    # Prepare output filename
    file_name_in = os.path.splitext(os.path.basename(image_path))[0]
    output_filename = f"{file_name_in}_encoded_{mode}.txt"
    output_filepath = os.path.join(os.path.dirname(image_path), output_filename)

    if mode == "RGB_SPLIT":
        print("Splitting image into RGB channels...")
        # Split image into RGB channels
        r, g, b = image.split()

        # Encode each channel separately
        red_data = encode_channel(r, width, height)
        green_data = encode_channel(g, width, height)
        blue_data = encode_channel(b, width, height)

        print("writing file...")
        with open(output_filepath, "w") as f:
            # Write header with channel information
            f.write(
                f"{SEPARATOR}\n{width}{SEPARATOR}{height}{SEPARATOR}{file_name_in}{SEPARATOR}RGB_SPLIT\n{SEPARATOR}\n")

            # Write Red channel data
            f.write("R")  # Red channel marker
            for count, color in red_data:
                f.write(f"{count}{color}")

            # Write Green channel data
            f.write("\nG")  # Green channel marker
            for count, color in green_data:
                f.write(f"{count}{color}")

            # Write Blue channel data
            f.write("\nB")  # Blue channel marker
            for count, color in blue_data:
                f.write(f"{count}{color}")

            f.write(f"\n{SEPARATOR}\n")

    else:
        # Existing encoding logic
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

        print("writing file...")
        with open(output_filepath, "w") as f:
            f.write(f"{SEPARATOR}\n{width}{SEPARATOR}{height}{SEPARATOR}{file_name_in}{SEPARATOR}{mode}\n{SEPARATOR}\n")
            for count, color in quantized_data:
                f.write(f"{count}{color}")
            f.write(f"\n{SEPARATOR}\n")

    loading_animation.stop()
    print(f"\nQuantized image saved to {output_filepath}")


def encode(image_path, mode='COLOR'):
    """
    Encode image with specified color mode.

    Args:
        image_path (str): Path to the input image
        mode (str): Color mode to use
    """
    start_time = time.time()
    loading_animation.start()

    # Validate mode
    if mode not in COLOR_MODES and mode != "RGB_SPLIT":
        print(f"Invalid mode. Choose from {list(COLOR_MODES.keys()) + ['RGB_SPLIT']}")
        return

    image = Image.open(image_path)
    image = image.convert("RGB")
    width, height = image.size
    total_pixels = width * height
    processed_pixels = 0

    # Prepare output filename
    file_name_in = os.path.splitext(os.path.basename(image_path))[0]
    output_filename = f"{file_name_in}_encoded_{mode}.txt"
    output_filepath = os.path.join(os.path.dirname(image_path), output_filename)

    def format_time(seconds):
        """Format time in hours, minutes, seconds."""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes} min {secs} sec"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours} hr {minutes} min"

    if mode == "RGB_SPLIT":
        print("Splitting image into RGB channels...")
        # Split image into RGB channels
        r, g, b = image.split()

        # Encode each channel separately
        red_data = encode_channel(r, width, height)
        green_data = encode_channel(g, width, height)
        blue_data = encode_channel(b, width, height)

        print("\nwriting file...")
        with open(output_filepath, "w") as f:
            # Write header with channel information
            f.write(
                f"{SEPARATOR}\n{width}{SEPARATOR}{height}{SEPARATOR}{file_name_in}{SEPARATOR}RGB_SPLIT\n{SEPARATOR}\n")

            # Write Red channel data
            f.write("R")  # Red channel marker
            for count, color in red_data:
                f.write(f"{count}{color}")

            # Write Green channel data
            f.write("\nG")  # Green channel marker
            for count, color in green_data:
                f.write(f"{count}{color}")

            # Write Blue channel data
            f.write("\nB")  # Blue channel marker
            for count, color in blue_data:
                f.write(f"{count}{color}")

            f.write(f"\n{SEPARATOR}\n")

    else:
        # Existing encoding logic with enhanced progress tracking
        quantized_data = []
        current_color = None
        color_count = 0
        color_codes = COLOR_MODES[mode]
        processed_pixels = 0

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

                # Calculate progress and performance
                processed_pixels += 1
                current_time = time.time()
                elapsed_time = current_time - start_time
                pixels_per_second = processed_pixels / elapsed_time if elapsed_time > 0 else 0

                # Estimate time remaining
                remaining_pixels = total_pixels - processed_pixels
                estimated_time_left = remaining_pixels / pixels_per_second if pixels_per_second > 0 else 0

                # Format output
                progress = (processed_pixels / total_pixels) * 100
                print(
                    f"Encoding {mode} mode: {progress:.2f}% | {pixels_per_second:.0f} px/sec | Est. {format_time(estimated_time_left)} left",
                    end="\r")

        quantized_data.append((color_count, current_color))

        print("\nwriting file...")
        with open(output_filepath, "w") as f:
            f.write(f"{SEPARATOR}\n{width}{SEPARATOR}{height}{SEPARATOR}{file_name_in}{SEPARATOR}{mode}\n{SEPARATOR}\n")
            for count, color in quantized_data:
                f.write(f"{count}{color}")
            f.write(f"\n{SEPARATOR}\n")

    loading_animation.stop()

    # Final performance summary
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nEncoding completed in {format_time(total_time)}")
    print(f"Quantized image saved to {output_filepath}")


def decode(txt_path):
    """Decode an encoded text file back to an image with detailed progress tracking"""
    start_time = time.time()

    with open(txt_path, "r") as f:
        lines = f.readlines()

    # Parse the header
    header = lines[1].strip().split("####")
    width, height, file_name_out, mode = header[0], header[1], header[2], header[3]
    width = int(width)
    height = int(height)
    total_pixels = width * height

    # Decode RGB_SPLIT mode
    if mode == "RGB_SPLIT":
        # Initialize separate channel arrays
        red_pixels = []
        green_pixels = []
        blue_pixels = []

        total_length = len(lines[3])
        current_channel = None
        processed_pixels = 0

        # Parse RGB channel data
        for line in lines[3:]:
            if line.strip() == SEPARATOR.strip():
                break

            if line.startswith('R'):
                current_channel = 'R'
                line = line[1:]
            elif line.startswith('G'):
                current_channel = 'G'
                line = line[1:]
            elif line.startswith('B'):
                current_channel = 'B'
                line = line[1:]

            if not current_channel:
                continue

            # Similar decoding logic to original decode function
            i = 0
            while i < len(line):
                # Extract count (digits)
                count_str = ""
                while i < len(line) and line[i].isdigit():
                    count_str += line[i]
                    i += 1

                if i >= len(line):
                    break

                # Extract color code
                color = line[i:i + 2]
                i += 2

                try:
                    count = int(count_str) if count_str else 1
                    count = min(count, width * height)
                except ValueError:
                    print(f"Warning: Invalid count value '{count_str}'. Skipping.")
                    continue

                # Map color code to intensity
                intensity_map = {
                    "MA": 0, "ME": 17, "MF": 34, "MG": 51, "MH": 68,
                    "MB": 85, "MI": 102, "MJ": 119, "MK": 136, "ML": 153,
                    "MC": 170, "MN": 187, "MP": 204, "MR": 221, "MS": 238, "MD": 255
                }

                intensity = intensity_map.get(color, 0)

                # Current time calculations
                current_time = time.time()
                elapsed_time = current_time - start_time
                processed_pixels += count
                pixels_per_second = processed_pixels / elapsed_time if elapsed_time > 0 else 0
                remaining_pixels = total_pixels - processed_pixels
                estimated_time_left = remaining_pixels / pixels_per_second if pixels_per_second > 0 else 0

                # Progress output
                progress = (processed_pixels / total_pixels) * 100
                print(
                    f"Decoding {current_channel} channel: {progress:.2f}% | {pixels_per_second:.0f} px/sec | Est. {format_time(estimated_time_left)} left",
                    end="\r")

                # Append to the correct channel
                if current_channel == 'R':
                    red_pixels.extend([intensity] * count)
                elif current_channel == 'G':
                    green_pixels.extend([intensity] * count)
                elif current_channel == 'B':
                    blue_pixels.extend([intensity] * count)

        # Truncate or pad channels
        total_pixels = width * height
        red_pixels = red_pixels[:total_pixels] + [0] * (total_pixels - len(red_pixels)) if len(
            red_pixels) < total_pixels else red_pixels[:total_pixels]
        green_pixels = green_pixels[:total_pixels] + [0] * (total_pixels - len(green_pixels)) if len(
            green_pixels) < total_pixels else green_pixels[:total_pixels]
        blue_pixels = blue_pixels[:total_pixels] + [0] * (total_pixels - len(blue_pixels)) if len(
            blue_pixels) < total_pixels else blue_pixels[:total_pixels]

        # Combine channels
        pixels = list(zip(red_pixels, green_pixels, blue_pixels))

        # Create and save the image
        image = Image.new("RGB", (width, height))
        image.putdata(pixels)

        output_filename = f"{file_name_out}_{mode}.png"
        output_filepath = os.path.join(os.path.dirname(txt_path), output_filename)
        image.save(output_filepath)

        print(f'\nDecoded image saved to {output_filepath}')
        return output_filename

    # Existing decoding logic for other modes
    # ... (rest of the original decode function remains the same)


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
            \n5-RGB_SPLIT\
            \n>>> ")

            selected_mode = MODES.get(mode, "COLOR")
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
