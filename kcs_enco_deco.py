# Filip Pawlowski 2023 (filippawlowski2012@gmail.com) 2023
# ---------------------------------------------------------
# based on: py-kcs by David Beazley (http://www.dabeaz.com)
# ---------------------------------------------------------

"""
---ABOUT---

Custom tool for encoding text data as audio, based on KCS format and "py-kcs by David Beazley (http://www.dabeaz.com)".

Script Name: kcs_enco-deco.py
Author: Filip Pawłowski
Contact: filippawlowski2012@gmail.com
"""

license = """MIT License

Copyright (c) 2025 Filip Pawłowski(kotlecikmud)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__version__ = "00.02.01.00"

print(f"Text2Audio Encoder/Decoder v{__version__}\n{license}\nloading...")

import os
import wave
import json
import time
import threading
from collections import deque
from itertools import islice
from datetime import datetime


# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


LOG_F_NAME = resource_path(".log")
CFG_MAIN_FILE = resource_path("config.json")
BACKUP_CFG = """{
  "ZERO_FREQ": 1400,
  "ONES_MULT": 2,
  "AMPLITUDE": 128,
  "CENTER": 128,
  "EXPLAIN_OPTIONS": false
}"""

INPUT_SIGN = '>>>'
MAIN_MENU_OPTIONS = [
    ('Encode text', 'Gets text UTF8 file and encodes into WAV file'),
    ('Decode text', 'Gets WAV file and decodes to original file.'),
    ('Adjust Frequencies', 'Modify ZERO_FREQ and ONES_MULT values'),
    ('Exit program', 'Exits Program.'),
]


class LoadingAnimation:
    def __init__(self):
        self.animation_signs = ['|', '/', '-', '\\']
        self.sign_index = 0
        self.finished = False

    def start(self):
        self.finished = False
        threading.Thread(target=self._animate).start()

    def stop(self):
        self.finished = True

    def _animate(self):
        while not self.finished:
            print('- ' + self.animation_signs[self.sign_index % len(self.animation_signs)] + ' -', end='\r')
            time.sleep(0.1)
            self.sign_index += 1


# Instantiate LoadingAnimation class
loading_animation = LoadingAnimation()
loading_animation.start()


def cls_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def log_event(entry: str = ""):
    print(entry)

    current_time = datetime.now()
    log_entry = f"[{current_time}]|{entry}\n"

    with open(LOG_F_NAME, "a") as log_f:
        log_f.write(log_entry)


def load_cfg():
    global config_main

    main_keys_list = [
        "ZERO_FREQ",
        "ONES_MULT",
        "AMPLITUDE",
        "CENTER",
        "EXPLAIN_OPTIONS"
    ]

    config_main = {param_main: None for param_main in main_keys_list}

    try:
        with open(CFG_MAIN_FILE, "r") as f:
            _config_main = json.load(f)

        for param_m in config_main:
            config_main[param_m] = _config_main.get(param_m, None)

        # Ensure fallback defaults
        config_main["ZERO_FREQ"] = config_main["ZERO_FREQ"] or 1400
        config_main["ONES_MULT"] = config_main["ONES_MULT"] or 2
        config_main["AMPLITUDE"] = config_main["AMPLITUDE"] or 128
        config_main["CENTER"] = config_main["CENTER"] or 128
        config_main["EXPLAIN_OPTIONS"] = config_main["EXPLAIN_OPTIONS"] or False

        globals().update(config_main)

        log_event("config successfully loaded from file")

    except FileNotFoundError:
        log_event("config file was not found")
        restore_backup_config()
        time.sleep(0.1)
        load_cfg()

    except Exception as e:
        log_event(str(e))
        exit(1)


def write_backup_config():
    with open(CFG_MAIN_FILE, "w") as backup_cfg:
        backup_cfg.write(BACKUP_CFG)
        backup_cfg.flush()
        log_event(f"backup config written to {CFG_MAIN_FILE}")


def restore_backup_config():
    if not os.path.isfile(CFG_MAIN_FILE):
        write_backup_config()


def adjust_frequencies():
    global config_main, ONES_FREQ, FRAMERATE, one_pulse, zero_pulse

    try:
        zero_freq = float(input(f"Enter ZERO_FREQ (current: {config_main['ZERO_FREQ']} Hz): "))
        ones_mult = float(input(f"Enter ONES_MULT (current: {config_main['ONES_MULT']}): "))

        # Update the configuration and recompute dependent values
        config_main["ZERO_FREQ"] = zero_freq
        config_main["ONES_MULT"] = ones_mult

        ONES_FREQ = zero_freq * ones_mult
        FRAMERATE = ONES_FREQ * 2

        # Recreate the wave patterns
        one_pulse = make_square_wave(ONES_FREQ, FRAMERATE) * 8
        zero_pulse = make_square_wave(config_main["ZERO_FREQ"], FRAMERATE) * 4

        print("Frequencies updated successfully!")
        time.sleep(1)

        # Save updated configuration to file
        with open(CFG_MAIN_FILE, "w") as f:
            json.dump(config_main, f)
            log_event("Updated configuration saved to file.")

    except ValueError:
        print("Invalid input. Please enter valid numbers.")
        time.sleep(1)


# ===============

def generate_wav_sign_change_bits(wavefile):
    """
    Generate a sequence representing sign bits
    """
    samplewidth = wavefile.getsampwidth()
    nchannels = wavefile.getnchannels()
    previous = 0
    while True:
        frames = wavefile.readframes(8192)
        if not frames:
            break

        # Extract most significant bytes from left-most audio channel
        msbytes = bytearray(frames[samplewidth - 1::samplewidth * nchannels])

        # Emit a stream of sign-change bits
        for byte in msbytes:
            signbit = byte & 0x80
            yield 1 if (signbit ^ previous) else 0
            previous = signbit


def generate_bytes(bitstream, framerate):
    """
    Generates a sequence of data bytes by sampling the stream of sign change bits
    """
    bitmasks = [0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80]

    # Compute the number of audio frames used to encode a single data bit
    frames_per_bit = int(round(float(framerate) * 8 / ONES_FREQ))

    # Queue of sampled sign bits
    sample = deque(maxlen=frames_per_bit)

    # Fill the sample buffer with an initial set of data
    sample.extend(islice(bitstream, frames_per_bit - 1))
    sign_changes = sum(sample)

    # Look for the start bit
    for val in bitstream:
        if val:
            sign_changes += 1
        if sample.popleft():
            sign_changes -= 1
        sample.append(val)

        # If a start bit is detected, sample the next 8 data bits
        if sign_changes <= 9:
            byteval = 0
            for mask in bitmasks:
                if sum(islice(bitstream, frames_per_bit)) >= 12:
                    byteval |= mask
            yield byteval
            # Skip the final two stop bits and refill the sample buffer
            sample.extend(islice(bitstream, 2 * frames_per_bit, 3 * frames_per_bit - 1))
            sign_changes = sum(sample)


def make_square_wave(freq, framerate):
    """
    Create a single square wave cycle of a given frequency
    """
    n = int(framerate / freq / 2)
    return bytearray([config_main["CENTER"] - config_main["AMPLITUDE"] // 2]) * n + \
        bytearray([config_main["CENTER"] + config_main["AMPLITUDE"] // 2]) * n


def kcs_encode_byte(byteval):
    """
    Take a single byte value and turn it into a bytearray representing
    the associated waveform along with the required start and stop bits.
    """
    bitmasks = [0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80]
    # The start bit (0)
    encoded = bytearray(zero_pulse)
    # 8 data bits
    for mask in bitmasks:
        encoded.extend(one_pulse if (byteval & mask) else zero_pulse)
    # Two stop bits (1)
    encoded.extend(one_pulse)
    encoded.extend(one_pulse)
    return encoded


def run_length_encode(data):
    """
    Include the run_length_encode function defined earlier for RLE compression
    """
    encoded_data = []
    count = 1
    for i in range(1, len(data)):
        if data[i] == data[i - 1]:
            count += 1
        else:
            encoded_data.append((count, data[i - 1]))
            count = 1
    encoded_data.append((count, data[-1]))
    return encoded_data


def get_filename_with_new_extension(filename: str, new_extension: str) -> str:
    """
    Replace the extension of a filename with a new one.

    Args:
        filename (str): Original filename
        new_extension (str): New extension (without the dot)

    Returns:
        str: Filename with new extension
    """
    # Split the filename into base and extension
    base = os.path.splitext(filename)[0]
    # Return base name with new extension
    return f"{base}.{new_extension.lstrip('.')}"


def kcs_encode_wav():
    """
    Write a WAV file with encoded data including the original file's timestamp and filename information.
    Leader and trailer specify the number of seconds of carrier signal to encode.
    """
    leader_len = 5
    trailer_len = 5

    in_filename = input("ENCODE\nInput file name: ")
    # Get just the filename without path for storing in header
    original_filename = os.path.basename(in_filename)
    out_filename = get_filename_with_new_extension(in_filename, 'wav')

    loading_animation.start()

    # Get the original file's modification timestamp
    try:
        file_timestamp = datetime.fromtimestamp(os.path.getmtime(in_filename))
        timestamp = file_timestamp.strftime("%Y-%m-%d %H:%M:%S")
    except OSError as e:
        log_event(f"Error reading file timestamp: {e}")
        # Fallback to current time if there's an error
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create header with both timestamp and original filename
    header = f"###TIMESTAMP:{timestamp}###ORIGINAL_FILE:{original_filename}###\n"

    with open(in_filename, "rb") as file:
        rawdata = file.read()

    w = wave.open(out_filename, "wb")
    w.setnchannels(1)
    w.setsampwidth(1)
    w.setframerate(FRAMERATE)

    # Encode the actual data
    encoded_data = bytearray()

    # Write the leader
    w.writeframes(one_pulse * (int(FRAMERATE / len(one_pulse)) * leader_len))

    # First encode the header with timestamp and filename
    for byteval in header.encode():
        encoded_data.extend(kcs_encode_byte(byteval))

    # Then encode the actual data
    for byteval in rawdata:
        encoded_data.extend(kcs_encode_byte(byteval))
        if byteval == 0x0d:
            # If CR, emit a short pause (10 NULL bytes)
            encoded_data.extend(null_pulse)

    w.writeframes(encoded_data)

    # Write the trailer
    w.writeframes(one_pulse * (int(FRAMERATE / len(one_pulse)) * trailer_len))
    w.close()

    loading_animation.stop()
    log_event(f"Text file was saved successfully: {out_filename}")


def kcs_decode_wav():
    """
    Decode a WAV file and extract timestamp, original filename, and content data.
    Sets the decoded file's modification time based on the encoded timestamp.
    """
    file_to_decode = input('DECODE\nInput file name: ')
    timestamp = None
    original_filename = None

    wf = wave.open(file_to_decode, "rb")
    sign_changes = generate_wav_sign_change_bits(wf)
    byte_stream = generate_bytes(sign_changes, wf.getframerate())

    buffer = bytearray()
    while True:
        linebreak = buffer.find(b'\n')
        if linebreak >= 0:
            line = buffer[:linebreak + 1].replace(b'\r\n', b'\n')
            buffer = buffer[linebreak + 1:]

            # Check if this line contains the header information
            line_str = line.decode('utf-8', errors='ignore')
            if '###TIMESTAMP:' in line_str and timestamp is None:
                try:
                    # Extract timestamp
                    timestamp_str = line_str.split('###TIMESTAMP:')[1].split('###')[0]
                    timestamp = datetime.strptime(timestamp_str.strip(), "%Y-%m-%d %H:%M:%S")

                    # Extract original filename
                    original_filename = line_str.split('###ORIGINAL_FILE:')[1].split('###')[0]
                    log_event(f"Found original filename: {original_filename}")
                    log_event(f"Found timestamp: {timestamp}")

                    # Use original filename for output if possible
                    if original_filename:
                        output_filename = original_filename
                    else:
                        output_filename = "decoded.txt"

                    # If file already exists, add a number to prevent overwriting
                    base, ext = os.path.splitext(output_filename)
                    counter = 1
                    while os.path.exists(output_filename):
                        output_filename = f"{base}_{counter}{ext}"
                        counter += 1

                    continue  # Skip writing the header line to the output file
                except Exception as e:
                    log_event(f"Error parsing header: {e}")
                    output_filename = "decoded.txt"  # Fallback filename

            with open(output_filename, "ab") as outf:
                outf.write(line)
        else:
            fragment = bytes(byte for byte in islice(byte_stream, 80) if byte)
            if not fragment:
                with open(output_filename, "ab") as outf:
                    outf.write(buffer)

                # Set file modification time if timestamp was found
                if timestamp:
                    timestamp_epoch = timestamp.timestamp()
                    os.utime(output_filename, (timestamp_epoch, timestamp_epoch))

                log_event(f"Decoded data were saved to file: {output_filename}")
                break
            buffer.extend(fragment)


if __name__ == '__main__':
    load_cfg()

    ONES_FREQ = config_main["ZERO_FREQ"] * config_main["ONES_MULT"]  # Hz
    FRAMERATE = ONES_FREQ * 2  # Hz

    # Create the wave patterns that encode 1s and 0s
    one_pulse = make_square_wave(ONES_FREQ, FRAMERATE) * 8
    zero_pulse = make_square_wave(config_main["ZERO_FREQ"], FRAMERATE) * 4

    # Pause to insert after carriage returns (10 NULL bytes)
    null_pulse = ((zero_pulse * 9) + (one_pulse * 2)) * 10

    if config_main["EXPLAIN_OPTIONS"]:
        template = "({}) {} - {}"
    else:
        template = "({}) {}"

    loading_animation.stop()
    log_event("program started")
    # === UI ===

    while True:
        cls_console()

        print(f"Text2Audio Encoder/Decoder v{__version__}")

        # displaying the list in the main menu
        for i, (choice_main_menu, description) in enumerate(MAIN_MENU_OPTIONS, 1):
            print(template.format(i, choice_main_menu, description))

        usr_input = input(f'{INPUT_SIGN}').strip()

        if usr_input.isdigit():  # check if a digit is entered
            index = int(usr_input) - 1
            if 0 <= index < len(MAIN_MENU_OPTIONS):  # check if the digit is within the range
                usr_input = MAIN_MENU_OPTIONS[index][0]

        for choice_main_menu, description in MAIN_MENU_OPTIONS:
            if usr_input == choice_main_menu:

                if choice_main_menu == 'Encode text':
                    kcs_encode_wav()

                elif choice_main_menu == 'Decode text':
                    kcs_decode_wav()

                elif choice_main_menu == 'Adjust Frequencies':
                    adjust_frequencies()

                elif choice_main_menu == 'Exit program':
                    log_event("exiting program")
                    exit(0)
