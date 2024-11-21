"""
img2txt.py
Filip Pawlowski 2023
filippawlowski2012@gmail.com
"""

__version__ = "00.02.02.00"

import os
import time
import math
import threading
from PIL import Image

SEPARATOR = "####"
MODES = {
    "1": "MONO2",
    "2": "MONO8",
    "3": "COLOR8",
    "4": "RGB_SPLIT"
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
    # Monochrome
    "MONO2": {
        "000000": "A",  # Black
        "555555": "B",  # Dark Gray
        "AAAAAA": "C",  # Light Gray
        "FFFFFF": "D"  # White
    },
    # Monochrome 8-bit grayscale (0 to 255)
    "MONO8": {
        "000000": "A",  # Black
        "010101": "B",  # Very Dark Gray
        "020202": "C",  # Dark Gray
        "030303": "D",  # Darker Medium Gray
        "040404": "E",  # Medium Dark Gray
        "050505": "F",  # Medium Gray
        "060606": "G",  # Medium Light Gray
        "070707": "H",  # Light Medium Gray
        "080808": "I",  # Light Gray
        "090909": "J",  # Lighter Gray
        "0A0A0A": "K",  # Very Light Gray
        "0B0B0B": "L",  # Almost White
        "0C0C0C": "M",  # Nearly White
        "0D0D0D": "N",  # Off White
        "0E0E0E": "O",  # Near White
        "0F0F0F": "P",  # Lightest Gray
        "101010": "Q",  # Very Light Grayscale
        "111111": "R",  # Super Light Gray
        "121212": "S",  # Almost Full White
        "131313": "T",  # Pale Gray
        "141414": "U",  # Pale Grayscale
        "151515": "V",  # Very Pale
        "161616": "W",  # Nearly White
        "171717": "X"   # Pure White
    },
    # Simple Color
    "COLOR8": {
        "FF0000": "R",  # Red
        "00FF00": "G",  # Green
        "0000FF": "B",  # Blue
        "FFFF00": "Y",  # Yellow
        "00FFFF": "C",  # Cyan
        "FF00FF": "M",  # Magenta
        "FFFFFF": "W",  # White
        "000000": "D"  # Black
    }
}


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def find_closest_color(rgb, color_mode):
    """Find the closest color in the selected color mode."""
    color_codes = COLOR_MODES[color_mode]
    return min(color_codes.keys(),
               key=lambda c: math.dist(rgb, tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))))


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


def encode_channel(channel, width, height, ch_name, mode='MONO16', ):
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
                f"Encoding {ch_name}[{color}] : {progress:.2f}% | {pixels_per_second:.0f} px/sec | Est. {format_time(estimated_time_left)} left",
                end="\r")

    quantized_data.append((color_count, current_color))
    return quantized_data


def encode(image_path, mode='COLOR8'):
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

    if mode == "RGB_SPLIT":
        print("Splitting image into RGB channels...")
        # Split image into RGB channels
        r, g, b = image.split()

        # Encode each channel separately
        red_data = encode_channel(r, width, height, "Red")
        green_data = encode_channel(g, width, height, "Green")
        blue_data = encode_channel(b, width, height, "Blue")

        print("\nwriting file...")
        with open(output_filepath, "w") as f:
            # Write header with channel information
            f.write(
                f"{SEPARATOR}\n{width}{SEPARATOR}{height}{SEPARATOR}{file_name_in}{SEPARATOR}RGB_SPLIT\n{SEPARATOR}\n")

            # Write Red channel data
            f.write("X")  # Red channel marker
            for count, color in red_data:
                f.write(f"{count}{color}")

            # Write Green channel data
            f.write("\nY")  # Green channel marker
            for count, color in green_data:
                f.write(f"{count}{color}")

            # Write Blue channel data
            f.write("\nZ")  # Blue channel marker
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
    """Decode an encoded text file back to an image with detailed progress tracking."""
    start_time = time.time()

    # Load and parse the encoded file
    with open(txt_path, "r") as f:
        lines = f.readlines()

    # Parse header
    if len(lines) < 4:
        raise ValueError("Encoded file is malformed or incomplete.")

    header = lines[1].strip().split("####")
    if len(header) != 4:
        raise ValueError("Header format is incorrect or missing required fields.")

    width, height, file_name_out, mode = int(header[0]), int(header[1]), header[2], header[3]

    # Map intensity codes to RGB/Grayscale values
    intensity_map = {
        "A": 0, "B": 85, "C": 170, "D": 255, "E": 34, "F": 51, "G": 68, "H": 102, "I": 119,
        "J": 136, "K": 153, "L": 187, "N": 204, "P": 221, "R": 238, "S": 255
    }

    if mode == "RGB_SPLIT":
        # Initialize data for each channel
        red_data, green_data, blue_data = [], [], []
        current_channel = None

        # Process the encoded data
        for line in lines[3:]:
            if line.strip() == "####":
                break  # End of data marker

            if line.startswith("X"):
                current_channel = red_data
                line = line[1:]  # Remove channel marker
            elif line.startswith("Y"):
                current_channel = green_data
                line = line[1:]  # Remove channel marker
            elif line.startswith("Z"):
                current_channel = blue_data
                line = line[1:]  # Remove channel marker
            else:
                # If the channel is undefined, skip this line
                if current_channel is None:
                    print(f"Skipping line: {line.strip()}")
                    continue

            # Decode current channel
            i = 0
            while i < len(line):
                # Extract run-length count
                count_str = ""
                while i < len(line) and line[i].isdigit():
                    count_str += line[i]
                    i += 1

                # Extract color code
                if i >= len(line):
                    break  # Avoid out-of-bounds access
                color = line[i]
                i += 1

                count = int(count_str) if count_str else 1
                intensity = intensity_map.get(color, 0)

                # Add decoded pixels to the current channel
                current_channel.extend([intensity] * count)

        # Ensure all channels have the correct number of pixels
        total_pixels = width * height
        red_data = red_data[:total_pixels] + [0] * (total_pixels - len(red_data))
        green_data = green_data[:total_pixels] + [0] * (total_pixels - len(green_data))
        blue_data = blue_data[:total_pixels] + [0] * (total_pixels - len(blue_data))

        # Combine channels into RGB tuples
        pixels = list(zip(red_data, green_data, blue_data))

        # Create the image
        image = Image.new("RGB", (width, height))
        image.putdata(pixels)

    elif mode in ["MONO4", "MONO16", "COLOR8"]:
        # For grayscale or simple color modes
        pixels = []

        # Process the encoded data
        encoded_data = lines[3].strip()
        i = 0
        while i < len(encoded_data):
            # Extract run-length count
            count_str = ""
            while i < len(encoded_data) and encoded_data[i].isdigit():
                count_str += encoded_data[i]
                i += 1

            # Extract color code
            if i >= len(encoded_data):
                break  # Avoid out-of-bounds access
            color = encoded_data[i]
            i += 1

            count = int(count_str) if count_str else 1
            if mode.startswith("MONO"):
                intensity = intensity_map.get(color, 0)
                pixels.extend([(intensity, intensity, intensity)] * count)
            elif mode == "COLOR8":
                hex_color = {
                    "R": (255, 0, 0), "G": (0, 255, 0), "B": (0, 0, 255),
                    "Y": (255, 255, 0), "C": (0, 255, 255), "M": (255, 0, 255),
                    "W": (255, 255, 255), "D": (0, 0, 0)
                }.get(color, (0, 0, 0))
                pixels.extend([hex_color] * count)

        # Truncate or pad the pixels
        total_pixels = width * height
        pixels = pixels[:total_pixels] + [(0, 0, 0)] * (total_pixels - len(pixels))

        # Create the image
        image = Image.new("RGB", (width, height))
        image.putdata(pixels)

    else:
        raise ValueError(f"Unsupported mode: {mode}")

    # Save the image
    output_filename = f"{file_name_out}_{mode}.png"
    output_filepath = os.path.join(os.path.dirname(txt_path), output_filename)
    image.save(output_filepath)

    end_time = time.time()
    print(f"Decoded image saved to {output_filepath}")
    print(f"Decoding completed in {format_time(end_time - start_time)}")
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
            \n1-MONO2\
            \n2-MONO8\
            \n3-COLOR8\
            \n4-RGB_SPLIT\
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
