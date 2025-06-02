"""
img2txt.py
Filip Pawlowski 2023
filippawlowski2012@gmail.com
"""

__version__ = "00.03.00.00"

import os
import time
import math
import threading
from PIL import Image

ROW_START_MARKER = b"\xAA\xBB\xCC\xDD"
ROW_END_MARKER = b"\xDD\xCC\xBB\xAA"
SEPARATOR = b"\x00\xFF\x00\xFF"

MODES = {"1": "MONO2", "2": "MONO4", "3": "MONO8", "4": "RGB4", "5": "RGB8"}


class LoadingAnimation:
    def __init__(self):
        self.animation_signs = [
            "|....",
            ".|...",
            "..|..",
            "...|.",
            "....|",
            "...|.",
            "..|..",
            ".|...",
        ]
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
            print(
                self.animation_signs[self.sign_index % len(self.animation_signs)],
                end="\r",
            )
            time.sleep(0.1)
            self.sign_index += 1


# Instantiate LoadingAnimation class
loading_animation = LoadingAnimation()

COLOR_MODES = {
    # Monochrome 2-bit (4 levels of gray)
    "MONO2": {
        "00": b"\x00",  # Black
        "01": b"\x01",  # Dark Gray
        "10": b"\x02",  # Light Gray
        "11": b"\x03",  # White
    },
    "MONO4": {
        "0000": b"\x00",  # Black
        "1111": b"\x01",  # Very Dark Gray
        "2222": b"\x02",  # Dark Gray
        "3333": b"\x03",  # Darker Medium Gray
        "4444": b"\x04",  # Medium Dark Gray
        "5555": b"\x05",  # Medium Gray
        "6666": b"\x06",  # Light Medium Gray
        "7777": b"\x07",  # Lighter Medium Gray
        "8888": b"\x08",  # Light Gray
        "9999": b"\x09",  # Lighter Gray
        "AAAA": b"\x0A",  # Very Light Gray
        "BBBB": b"\x0B",  # Almost White
        "CCCC": b"\x0C",  # Near White
        "DDDD": b"\x0D",  # Very Near White
        "EEEE": b"\x0E",  # Extremely Light Gray
        "FFFF": b"\x0F",  # White
    },
    # Monochrome 8-bit grayscale (0 to 255 intensity levels)
    "MONO8": {
        "000000": b"\x00",  # Black
        "010101": b"\x01",  # Very Dark Gray
        "020202": b"\x02",  # Dark Gray
        "030303": b"\x03",  # Darker Medium Gray
        "040404": b"\x04",  # Medium Dark Gray
        "050505": b"\x05",  # Medium Gray
        "060606": b"\x06",
        "070707": b"\x07",
        "080808": b"\x08",
        "090909": b"\x09",
        "0A0A0A": b"\x0A",
        "0B0B0B": b"\x0B",
        "0C0C0C": b"\x0C",
        "0D0D0D": b"\x0D",
        "0E0E0E": b"\x0E",
        "0F0F0F": b"\x0F",
        "101010": b"\x10",
        "111111": b"\x11",
        "121212": b"\x12",
        "131313": b"\x13",
        "141414": b"\x14",
        "151515": b"\x15",
        "161616": b"\x16",
        "171717": b"\x17",
        "181818": b"\x18",
        "191919": b"\x19",
        "1A1A1A": b"\x1A",
        "1B1B1B": b"\x1B",
        "1C1C1C": b"\x1C",
        "1D1D1D": b"\x1D",
        "1E1E1E": b"\x1E",
        "1F1F1F": b"\x1F",
        "202020": b"\x20",
        "212121": b"\x21",
        "222222": b"\x22",
        "232323": b"\x23",
        "242424": b"\x24",
        "252525": b"\x25",
        "262626": b"\x26",
        "272727": b"\x27",
        "282828": b"\x28",
        "292929": b"\x29",
        "2A2A2A": b"\x2A",
        "2B2B2B": b"\x2B",
        "2C2C2C": b"\x2C",
        "2D2D2D": b"\x2D",
        "2E2E2E": b"\x2E",
        "2F2F2F": b"\x2F",
        "303030": b"\x30",
        "313131": b"\x31",
        "323232": b"\x32",
        "333333": b"\x33",
        "343434": b"\x34",
        "353535": b"\x35",
        "363636": b"\x36",
        "373737": b"\x37",
        "383838": b"\x38",
        "393939": b"\x39",
        "3A3A3A": b"\x3A",
        "3B3B3B": b"\x3B",
        "3C3C3C": b"\x3C",
        "3D3D3D": b"\x3D",
        "3E3E3E": b"\x3E",
        "3F3F3F": b"\x3F",
        "404040": b"\x40",
        "414141": b"\x41",
        "424242": b"\x42",
        "434343": b"\x43",
        "444444": b"\x44",
        "454545": b"\x45",
        "464646": b"\x46",
        "474747": b"\x47",
        "484848": b"\x48",
        "494949": b"\x49",
        "4A4A4A": b"\x4A",
        "4B4B4B": b"\x4B",
        "4C4C4C": b"\x4C",
        "4D4D4D": b"\x4D",
        "4E4E4E": b"\x4E",
        "4F4F4F": b"\x4F",
        "505050": b"\x50",
        "515151": b"\x51",
        "525252": b"\x52",
        "535353": b"\x53",
        "545454": b"\x54",
        "555555": b"\x55",
        "565656": b"\x56",
        "575757": b"\x57",
        "585858": b"\x58",
        "595959": b"\x59",
        "5A5A5A": b"\x5A",
        "5B5B5B": b"\x5B",
        "5C5C5C": b"\x5C",
        "5D5D5D": b"\x5D",
        "5E5E5E": b"\x5E",
        "5F5F5F": b"\x5F",
        "606060": b"\x60",
        "616161": b"\x61",
        "626262": b"\x62",
        "636363": b"\x63",
        "646464": b"\x64",
        "656565": b"\x65",
        "666666": b"\x66",
        "676767": b"\x67",
        "686868": b"\x68",
        "696969": b"\x69",
        "6A6A6A": b"\x6A",
        "6B6B6B": b"\x6B",
        "6C6C6C": b"\x6C",
        "6D6D6D": b"\x6D",
        "6E6E6E": b"\x6E",
        "6F6F6F": b"\x6F",
        "707070": b"\x70",
        "717171": b"\x71",
        "727272": b"\x72",
        "737373": b"\x73",
        "747474": b"\x74",
        "757575": b"\x75",
        "767676": b"\x76",
        "777777": b"\x77",
        "787878": b"\x78",
        "797979": b"\x79",
        "7A7A7A": b"\x7A",
        "7B7B7B": b"\x7B",
        "7C7C7C": b"\x7C",
        "7D7D7D": b"\x7D",
        "7E7E7E": b"\x7E",
        "7F7F7F": b"\x7F",
        "808080": b"\x80",
        "818181": b"\x81",
        "828282": b"\x82",
        "838383": b"\x83",
        "848484": b"\x84",
        "858585": b"\x85",
        "868686": b"\x86",
        "878787": b"\x87",
        "888888": b"\x88",
        "898989": b"\x89",
        "8A8A8A": b"\x8A",
        "8B8B8B": b"\x8B",
        "8C8C8C": b"\x8C",
        "8D8D8D": b"\x8D",
        "8E8E8E": b"\x8E",
        "8F8F8F": b"\x8F",
        "909090": b"\x90",
        "919191": b"\x91",
        "929292": b"\x92",
        "939393": b"\x93",
        "949494": b"\x94",
        "959595": b"\x95",
        "969696": b"\x96",
        "979797": b"\x97",
        "989898": b"\x98",
        "999999": b"\x99",
        "9A9A9A": b"\x9A",
        "9B9B9B": b"\x9B",
        "9C9C9C": b"\x9C",
        "9D9D9D": b"\x9D",
        "9E9E9E": b"\x9E",
        "9F9F9F": b"\x9F",
        "A0A0A0": b"\xA0",
        "A1A1A1": b"\xA1",
        "A2A2A2": b"\xA2",
        "A3A3A3": b"\xA3",
        "A4A4A4": b"\xA4",
        "A5A5A5": b"\xA5",
        "A6A6A6": b"\xA6",
        "A7A7A7": b"\xA7",
        "A8A8A8": b"\xA8",
        "A9A9A9": b"\xA9",
        "AAAAAA": b"\xAA",
        "ABABAB": b"\xAB",
        "ACACAC": b"\xAC",
        "ADADAD": b"\xAD",
        "AEAEAE": b"\xAE",
        "AFAFAF": b"\xAF",
        "B0B0B0": b"\xB0",
        "B1B1B1": b"\xB1",
        "B2B2B2": b"\xB2",
        "B3B3B3": b"\xB3",
        "B4B4B4": b"\xB4",
        "B5B5B5": b"\xB5",
        "B6B6B6": b"\xB6",
        "B7B7B7": b"\xB7",
        "B8B8B8": b"\xB8",
        "B9B9B9": b"\xB9",
        "BABABA": b"\xBA",
        "BBBBBB": b"\xBB",
        "BCBCBC": b"\xBC",
        "BDBDBD": b"\xBD",
        "BEBEBE": b"\xBE",
        "BFBFBF": b"\xBF",
        "C0C0C0": b"\xC0",
        "C1C1C1": b"\xC1",
        "C2C2C2": b"\xC2",
        "C3C3C3": b"\xC3",
        "C4C4C4": b"\xC4",
        "C5C5C5": b"\xC5",
        "C6C6C6": b"\xC6",
        "C7C7C7": b"\xC7",
        "C8C8C8": b"\xC8",
        "C9C9C9": b"\xC9",
        "CACACA": b"\xCA",
        "CBCBCB": b"\xCB",
        "CCCCCC": b"\xCC",
        "CDCDCD": b"\xCD",
        "CECECE": b"\xCE",
        "CFCFCF": b"\xCF",
        "D0D0D0": b"\xD0",
        "D1D1D1": b"\xD1",
        "D2D2D2": b"\xD2",
        "D3D3D3": b"\xD3",
        "D4D4D4": b"\xD4",
        "D5D5D5": b"\xD5",
        "D6D6D6": b"\xD6",
        "D7D7D7": b"\xD7",
        "D8D8D8": b"\xD8",
        "D9D9D9": b"\xD9",
        "DADADA": b"\xDA",
        "DBDBDB": b"\xDB",
        "DCDCDC": b"\xDC",
        "DDDDDD": b"\xDD",
        "DEDEDE": b"\xDE",
        "DFDFDF": b"\xDF",
        "E0E0E0": b"\xE0",
        "E1E1E1": b"\xE1",
        "E2E2E2": b"\xE2",
        "E3E3E3": b"\xE3",
        "E4E4E4": b"\xE4",
        "E5E5E5": b"\xE5",
        "E6E6E6": b"\xE6",
        "E7E7E7": b"\xE7",
        "E8E8E8": b"\xE8",
        "E9E9E9": b"\xE9",
        "EAEAEA": b"\xEA",
        "EBEBEB": b"\xEB",
        "ECECEC": b"\xEC",
        "EDEDED": b"\xED",
        "EEEEEE": b"\xEE",
        "EFEFEF": b"\xEF",
        "F0F0F0": b"\xF0",
        "F1F1F1": b"\xF1",
        "F2F2F2": b"\xF2",
        "F3F3F3": b"\xF3",
        "F4F4F4": b"\xF4",
        "F5F5F5": b"\xF5",
        "F6F6F6": b"\xF6",
        "F7F7F7": b"\xF7",
        "F8F8F8": b"\xF8",
        "F9F9F9": b"\xF9",
        "FAFAFA": b"\xFA",
        "FBFBFB": b"\xFB",
        "FCFCFC": b"\xFC",
        "FDFDFD": b"\xFD",
        "FEFEFE": b"\xFE",
        "FFFFFF": b"\xFF",
    },
}


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def find_closest_color(rgb, color_mode):
    """Find the closest color in the selected color mode."""
    color_codes = COLOR_MODES[color_mode]
    return min(
        color_codes.keys(),
        key=lambda c: math.dist(rgb, tuple(int(c[i : i + 2], 16) for i in (0, 2, 4))),
    )


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


def encode_channel(
    channel,
    width,
    height,
    ch_name,
    mode="MONO16",
):
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
            pixels_per_second = (
                processed_pixels / elapsed_time if elapsed_time > 0 else 0
            )

            # Estimate time remaining
            remaining_pixels = total_pixels - processed_pixels
            estimated_time_left = (
                remaining_pixels / pixels_per_second if pixels_per_second > 0 else 0
            )

            # Format output
            progress = (processed_pixels / total_pixels) * 100
            print(
                f"Encoding {ch_name}[{color}] : {progress:.2f}% | {pixels_per_second:.0f} px/sec | Est. {format_time(estimated_time_left)} left",
                end="\r",
            )

    quantized_data.append((color_count, current_color))
    return quantized_data


# Helper functions for encoding
def pack_rgb_pixels(pixels):
    """Packs RGB pixels into a flat list, one byte for each channel"""
    packed = []
    for r, g, b in pixels:
        packed.append(r)  # Red channel
        packed.append(g)  # Green channel
        packed.append(b)  # Blue channel
    return packed


def pack_2bit_data(data):
    """Pack 2-bit data into bytes"""
    packed = []
    for i in range(0, len(data), 4):  # Pack 4 values into 1 byte
        byte = (data[i] << 6) | (data[i + 1] << 4) | (data[i + 2] << 2) | data[i + 3]
        packed.append(byte)
    return packed


def pack_4bit_data(data):
    """Pack 4-bit data into bytes"""
    packed = []
    for i in range(0, len(data), 2):  # Pack 2 values into 1 byte
        byte = (data[i] << 4) | data[i + 1]
        packed.append(byte)
    return packed


def run_length_encode(data):
    """Run-length encode a list of values"""
    encoded = []
    current_value = data[0]
    count = 1
    for value in data[1:]:
        if value == current_value:
            count += 1
        else:
            encoded.append((current_value, count))
            current_value = value
            count = 1
    encoded.append((current_value, count))  # Append the last group
    return encoded


# Decoding functions
def unpack_2bit_data(data, num_pixels):
    """Unpacks 2-bit data into pixels (grayscale values)."""
    pixels = []
    num_bytes = (
        num_pixels + 3
    ) // 4  # Number of bytes needed to store num_pixels (rounded up)

    if len(data) < num_bytes:
        raise ValueError(
            f"Insufficient data. Expected at least {num_bytes} bytes, but got {len(data)}."
        )

    for byte in data[:num_bytes]:
        pixels.append((byte >> 6) & 0x03)
        pixels.append((byte >> 4) & 0x03)
        pixels.append((byte >> 2) & 0x03)
        pixels.append(byte & 0x03)

    return pixels[:num_pixels]  # Trim excess pixels if any


def unpack_4bit_data(data, num_pixels):
    """Unpacks 4-bit data into pixels (grayscale values)."""
    pixels = []
    num_bytes = (
        num_pixels + 1
    ) // 2  # Number of bytes needed to store num_pixels (rounded up)

    if len(data) < num_bytes:
        raise ValueError(
            f"Insufficient data. Expected at least {num_bytes} bytes, but got {len(data)}."
        )

    for byte in data[:num_bytes]:
        pixels.append((byte >> 4) & 0x0F)  # Extract the first 4 bits
        pixels.append(byte & 0x0F)  # Extract the second 4 bits

    return pixels[:num_pixels]  # Trim excess pixels if any


def run_length_decode(encoded_data):
    """Run-length decode the data."""
    decoded = []
    idx = 0
    while idx < len(encoded_data):
        value = encoded_data[idx]  # First byte is the value
        count = int.from_bytes(
            encoded_data[idx + 1 : idx + 5], "big"
        )  # Next 4 bytes are the count
        decoded.extend([value] * count)  # Repeat the value `count` times
        idx += 5  # Move to the next RLE pair
    return decoded


def encode(image_path, mode="MONO8"):
    """
    General-purpose encoding function for multiple color modes.
    Now includes newline character after each row for improved error resilience.

    Args:
        image_path (str): Path to the input image.
        mode (str): Encoding mode ('MONO2', 'MONO4', 'MONO8', 'RGB8').

    Returns:
        str: Path to the encoded file.
    """
    start_time = time.time()
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    pixels = list(image.getdata())

    # Prepare output path
    file_name_in = os.path.splitext(os.path.basename(image_path))[0]
    output_filepath = os.path.join(
        os.path.dirname(image_path), f"{file_name_in}_encoded_{mode}.bin"
    )

    # Initialize encoded data as bytearray
    encoded_data = bytearray()

    # Add image metadata (width, height, mode)
    encoded_data.extend(width.to_bytes(4, "big"))
    encoded_data.extend(height.to_bytes(4, "big"))
    encoded_data.extend(mode.encode("utf-8"))
    encoded_data.extend(SEPARATOR)

    # Encode based on mode with row-wise processing
    def encode_row(row_pixels):
        if mode == "MONO2":
            quantized_pixels = [(p * 3) // 255 for p in row_pixels]
            packed_data = pack_2bit_data(quantized_pixels)
            return packed_data
        elif mode == "MONO4":
            quantized_pixels = [(p * 4) // 255 for p in row_pixels]
            packed_data = pack_4bit_data(quantized_pixels)
            return packed_data
        elif mode == "MONO8":
            run_length_data = run_length_encode(row_pixels)
            row_encoded = bytearray()
            for value, count in run_length_data:
                row_encoded.append(value)
                row_encoded.extend(count.to_bytes(4, "big"))
            return row_encoded
        elif mode == "RGB4":
            quantized_pixels = [
                ((pixel[0] * 15) // 255, (pixel[1] * 15) // 255, (pixel[2] * 15) // 255)
                for pixel in row_pixels
            ]
            packed_data = pack_4bit_data([val for p in quantized_pixels for val in p])
            return packed_data
        elif mode == "RGB8":
            return pack_rgb_pixels(row_pixels)

    # Process image row by row
    for y in range(height):
        row_start = y * width
        row_pixels = pixels[row_start : row_start + width]

        # Determine pixel processing based on mode
        if mode in ["MONO2", "MONO4"]:
            row_pixels = [round(sum(pixel) / 3) for pixel in row_pixels]

        row_encoded = encode_row(row_pixels)
        encoded_data.extend(row_encoded)
        encoded_data.append(ord("\n"))  # Add newline after each row

    # Save encoded file
    with open(output_filepath, "wb") as f:
        f.write(encoded_data)

    print(
        f"Encoding completed in {time.time() - start_time:.2f} seconds.\n{output_filepath=}"
    )
    return output_filepath


def decode(file_path):
    """
    Decodes the encoded file into an image.

    Args:
        file_path (str): Path to the encoded file.

    Returns:
        str: Path to the decoded image.
    """
    start_time = time.time()

    # Read the encoded file
    with open(file_path, "rb") as f:
        data = f.read()

    try:
        # Parse header
        width = int.from_bytes(data[:4], "big")
        height = int.from_bytes(data[4:8], "big")

        # Locate the separator
        try:
            mode_end = data.index(SEPARATOR)
        except ValueError:
            raise ValueError(
                f"Separator {SEPARATOR} not found in the file. Ensure the file format is correct."
            )

        mode = data[8:mode_end].decode("utf-8")

        # Extract pixel data
        body = data[mode_end + len(SEPARATOR) :]

        # Debug output
        print(f"Decoding mode: {mode}")
        print(f"Image dimensions: {width}x{height}")

        # Decode rows
        pixels = []
        row_data = bytearray()

        def decode_row(row_body):
            # Calculate expected bytes per row
            expected_bytes = width if mode.startswith("MONO") else width * 3
            if len(row_body) < expected_bytes:
                row_body += b"\x00" * (expected_bytes - len(row_body))  # Pad with black
            elif len(row_body) > expected_bytes:
                row_body = row_body[:expected_bytes]  # Truncate excess

            # Decode based on mode
            if mode == "MONO2":
                decoded_pixels = unpack_2bit_data(row_body, width)
                return [(p * 85, p * 85, p * 85) for p in decoded_pixels]
            elif mode == "MONO4":
                decoded_pixels = unpack_4bit_data(row_body, width)
                return [(p * 17, p * 17, p * 17) for p in decoded_pixels]
            elif mode == "MONO8":
                decoded_pixels = run_length_decode(row_body)
                return [(value, value, value) for value in decoded_pixels]
            elif mode == "RGB4":
                decoded_pixels = unpack_4bit_data(row_body, width * 3)
                return [
                    (
                        decoded_pixels[i] * 17,
                        decoded_pixels[i + 1] * 17,
                        decoded_pixels[i + 2] * 17,
                    )
                    for i in range(0, len(decoded_pixels), 3)
                ]
            elif mode == "RGB8":
                return [
                    (row_body[i], row_body[i + 1], row_body[i + 2])
                    for i in range(0, len(row_body), 3)
                ]

        # Process body row by row
        for byte in body:
            if byte == ord("\n"):
                row_pixels = decode_row(row_data)
                pixels.extend(row_pixels)
                row_data.clear()
            else:
                row_data.append(byte)

        # Process the last row
        if row_data:
            row_pixels = decode_row(row_data)
            pixels.extend(row_pixels)

        # Create the image
        image = Image.new("RGB", (width, height))
        image.putdata(pixels)

        # Save the decoded image
        output_filepath = os.path.splitext(file_path)[0] + "_decoded.png"
        image.save(output_filepath)
        print(f"Decoding completed in {time.time() - start_time:.2f} seconds.")
        return output_filepath

    except Exception as e:
        print(f"Error during decoding: {e}")
        return None


def main():
    while True:
        # Menu selection
        clear_terminal()
        choice = input(
            f"img2txt {__version__}\nChoose option (1-4):\n"
            "1) Encode Image\n"
            "2) Decode Encoded File\n"
            "3) Exit\n>>>"
        )

        if choice == "1":
            image_path = input("Provide the path to the image file: ")
            mode = input(
                "Choose color mode (default=COLOR):\
            \n1-MONO2\
            \n2-MONO4\
            \n3-MONO8\
            \n4-RGB4\
            \n5-RGB8\
            \n>>> "
            )

            encode(image_path, MODES.get(mode, "MONO8"))

        elif choice == "2":
            txt_path = input("Enter the path to the txt file: ")
            decode(txt_path)

        elif choice == "3":
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
