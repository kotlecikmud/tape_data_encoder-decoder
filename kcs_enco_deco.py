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

__version__ = "00.03.00.00"

print("loading...")

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

INPUT_SIGN = ">>>"
MAIN_MENU_OPTIONS = [
    ("Encode text", "Gets text UTF8 file and encodes into WAV file"),
    ("Decode text", "Gets WAV file and decodes to original file."),
    ("Adjust Frequencies", "Modify ZERO_FREQ and ONES_MULT values"),
    ("Exit program", "Exits Program."),
]


class LoadingAnimation:
    def __init__(self):
        self.animation_signs = ["|", "/", "-", "\\"]
        self.sign_index = 0
        self.finished = False

    def start(self):
        self.finished = False
        threading.Thread(target=self._animate).start()

    def stop(self):
        self.finished = True

    def _animate(self):
        while not self.finished:
            print(
                "- "
                + self.animation_signs[self.sign_index % len(self.animation_signs)]
                + " -",
                end="\r",
            )
            time.sleep(0.1)
            self.sign_index += 1


# Instantiate LoadingAnimation class
loading_animation = LoadingAnimation()


def cls_console():
    os.system("cls" if os.name == "nt" else "clear")


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
        "EXPLAIN_OPTIONS",
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


def adjust_frequencies(current_config, new_zero_freq=None, new_ones_mult=None):
    """
    Adjusts ZERO_FREQ and ONES_MULT in the configuration.
    If new_zero_freq or new_ones_mult are None, it prompts the user for input (for standalone mode).
    Otherwise, it uses the provided values.
    Returns the updated config dictionary or None if inputs are invalid.
    Saves the updated config to CFG_MAIN_FILE if changes are made.
    Note: This function will modify the 'current_config' dictionary directly if provided,
    or work on a copy of global 'config_main' if 'current_config' is global 'config_main'.
    The caller should handle pulse re-initialization based on the returned config.
    """
    config_to_update = (
        current_config  # Assume current_config is the one to modify or it's a copy.
    )

    try:
        if new_zero_freq is None:
            val_zero_freq_str = input(
                f"Enter ZERO_FREQ (current: {config_to_update['ZERO_FREQ']} Hz): "
            )
            if not val_zero_freq_str:  # User pressed enter without input
                _new_zero_freq = config_to_update["ZERO_FREQ"]  # Keep current
            else:
                _new_zero_freq = float(val_zero_freq_str)
        else:
            _new_zero_freq = float(new_zero_freq)

        if new_ones_mult is None:
            val_ones_mult_str = input(
                f"Enter ONES_MULT (current: {config_to_update['ONES_MULT']}): "
            )
            if not val_ones_mult_str:  # User pressed enter without input
                _new_ones_mult = config_to_update["ONES_MULT"]  # Keep current
            else:
                _new_ones_mult = float(val_ones_mult_str)
        else:
            _new_ones_mult = float(new_ones_mult)

        # Update the configuration
        config_to_update["ZERO_FREQ"] = _new_zero_freq
        config_to_update["ONES_MULT"] = _new_ones_mult

        log_event(
            f"Frequencies settings updated in config: ZERO_FREQ={_new_zero_freq}, ONES_MULT={_new_ones_mult}"
        )

        # Save updated configuration to file
        # This part assumes that if this function is called, the config should be saved.
        # For library use, saving might be optional or handled by the caller.
        with open(CFG_MAIN_FILE, "w") as f:
            json.dump(config_to_update, f)  # Save the modified config
            log_event(f"Updated configuration saved to {CFG_MAIN_FILE}.")

        # It's important that global config_main is also updated if it was the one passed in.
        # If current_config was a copy, the caller needs to handle updating the original if necessary.
        # If current_config is indeed the global config_main, this change is already reflected.
        if current_config is config_main:  # Check if it was the global one
            globals()["config_main"] = config_to_update

        print("Frequencies updated successfully in configuration!")
        time.sleep(1)
        return config_to_update

    except ValueError:
        print("Invalid input. Please enter valid numbers.")
        time.sleep(1)
        return None  # Indicate failure


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
        msbytes = bytearray(frames[samplewidth - 1 :: samplewidth * nchannels])

        # Emit a stream of sign-change bits
        for byte in msbytes:
            signbit = byte & 0x80
            yield 1 if (signbit ^ previous) else 0
            previous = signbit


def generate_bytes(bitstream, framerate, ones_freq):
    """
    Generates a sequence of data bytes by sampling the stream of sign change bits.
    Requires ones_freq to calculate frames_per_bit.
    """
    bitmasks = [0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80]

    # Compute the number of audio frames used to encode a single data bit
    frames_per_bit = int(round(float(framerate) * 8 / ones_freq))

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


def make_square_wave(freq, framerate, config):
    """
    Create a single square wave cycle of a given frequency using provided config
    """
    n = int(framerate / freq / 2)
    return (
        bytearray([config["CENTER"] - config["AMPLITUDE"] // 2]) * n
        + bytearray([config["CENTER"] + config["AMPLITUDE"] // 2]) * n
    )


def kcs_encode_byte(byteval, config, one_pulse, zero_pulse):
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


def kcs_encode_wav(in_filename, out_filename, config, leader_len=5, trailer_len=5):
    """
    Write a WAV file with encoded data including the original file's timestamp and filename information.
    Leader and trailer specify the number of seconds of carrier signal to encode.
    Returns True on success, False on failure.
    """
    try:
        original_filename_for_header = os.path.basename(in_filename)

        # Get the original file's modification timestamp
        try:
            file_timestamp = datetime.fromtimestamp(os.path.getmtime(in_filename))
            timestamp_str = file_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        except OSError as e:
            log_event(f"Error reading file timestamp for {in_filename}: {e}")
            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fallback

        header = f"###TIMESTAMP:{timestamp_str}###ORIGINAL_FILE:{original_filename_for_header}###\n"

        with open(in_filename, "rb") as file:
            rawdata = file.read()

        # Calculate ONES_FREQ and FRAMERATE from config
        local_ones_freq = config["ZERO_FREQ"] * config["ONES_MULT"]
        local_framerate = local_ones_freq * 2

        # Create local wave patterns based on config
        local_one_pulse = make_square_wave(local_ones_freq, local_framerate, config) * 8
        local_zero_pulse = (
            make_square_wave(config["ZERO_FREQ"], local_framerate, config) * 4
        )
        # Pause to insert after carriage returns (10 NULL bytes)
        local_null_pulse = ((local_zero_pulse * 9) + (local_one_pulse * 2)) * 10

        w = wave.open(out_filename, "wb")
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(local_framerate)

        encoded_data = bytearray()

        # Write the leader
        leader_frames = (
            local_one_pulse * (int(local_framerate / len(local_one_pulse)) * leader_len)
            if local_one_pulse
            else bytearray()
        )
        w.writeframes(leader_frames)

        # First encode the header with timestamp and filename
        for byteval in header.encode("utf-8"):  # Ensure consistent encoding
            encoded_data.extend(
                kcs_encode_byte(byteval, config, local_one_pulse, local_zero_pulse)
            )

        # Then encode the actual data
        for byteval in rawdata:
            encoded_data.extend(
                kcs_encode_byte(byteval, config, local_one_pulse, local_zero_pulse)
            )
            if byteval == 0x0D:  # Carriage Return
                encoded_data.extend(local_null_pulse)

        w.writeframes(encoded_data)

        # Write the trailer
        trailer_frames = (
            local_one_pulse
            * (int(local_framerate / len(local_one_pulse)) * trailer_len)
            if local_one_pulse
            else bytearray()
        )
        w.writeframes(trailer_frames)
        w.close()
        log_event(f"Text file was saved successfully: {out_filename}")
        return True
    except Exception as e:
        log_event(f"Error during encoding: {e}")
        # Ensure wave file is closed if open
        if "w" in locals() and w and not w.closed:
            w.close()
        return False


def kcs_decode_wav(file_to_decode, output_path_base, config):
    """
    Decode a WAV file and extract timestamp, original filename, and content data.
    Sets the decoded file's modification time based on the encoded timestamp.
    Returns the full path to the decoded file on success, None on failure.
    """
    timestamp = None
    original_filename_from_header = None
    output_filename = None  # Will be determined based on header or default
    wf = None  # Initialize wf to None for broader scope in case of early exit

    try:
        wf = wave.open(file_to_decode, "rb")

        local_ones_freq = config["ZERO_FREQ"] * config["ONES_MULT"]

        sign_changes = generate_wav_sign_change_bits(wf)
        byte_stream = generate_bytes(sign_changes, wf.getframerate(), local_ones_freq)

        buffer = bytearray()
        first_line_processed = (
            False  # To ensure header is checked only once at the beginning
        )
        decoded_content_started = False  # To differentiate header lines from data that might look like a header

        # Determine initial output_filename before loop
        # This will be used if header is not found or is malformed
        # It will be refined if a valid header is parsed
        current_output_filename_candidate = f"{output_path_base}_decoded.txt"
        # Ensure this candidate doesn't overwrite by finding a unique name upfront for the default case
        base_default, ext_default = os.path.splitext(current_output_filename_candidate)
        counter_default = 1
        while os.path.exists(current_output_filename_candidate):
            current_output_filename_candidate = (
                f"{base_default}_{counter_default}{ext_default}"
            )
            counter_default += 1
        output_filename = current_output_filename_candidate  # Default output filename

        out_file_handle = None

        while True:
            # Try to parse a line if we haven't definitively started binary content
            # and there's a newline in the buffer.
            if not decoded_content_started and b"\n" in buffer:
                linebreak = buffer.find(b"\n")
                line_bytes = buffer[: linebreak + 1]

                line_str = ""
                try:
                    line_str = line_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    # This line is not UTF-8, so it's part of the data.
                    # The buffer from this point onwards is considered data.
                    decoded_content_started = True
                    # The line_bytes that failed decoding are kept in buffer to be written as data

                if (
                    not decoded_content_started
                ):  # Still attempting to parse as text (header or text data)
                    buffer = buffer[linebreak + 1 :]  # Consume the line from buffer
                    if (
                        not first_line_processed
                        and "###TIMESTAMP:" in line_str
                        and "###ORIGINAL_FILE:" in line_str
                    ):
                        first_line_processed = True
                        try:
                            timestamp_str = (
                                line_str.split("###TIMESTAMP:")[1]
                                .split("###")[0]
                                .strip()
                            )
                            timestamp = datetime.strptime(
                                timestamp_str, "%Y-%m-%d %H:%M:%S"
                            )
                            original_filename_from_header = (
                                line_str.split("###ORIGINAL_FILE:")[1]
                                .split("###")[0]
                                .strip()
                            )

                            log_event(
                                f"Found original filename: {original_filename_from_header}"
                            )
                            log_event(f"Found timestamp: {timestamp}")

                            if original_filename_from_header:
                                if os.path.isdir(
                                    output_path_base
                                ):  # output_path_base is a directory
                                    current_output_filename_candidate = os.path.join(
                                        output_path_base, original_filename_from_header
                                    )
                                else:  # output_path_base is a file prefix
                                    current_output_filename_candidate = f"{output_path_base}_{original_filename_from_header}"
                            else:  # No original filename in header, use default base
                                current_output_filename_candidate = (
                                    f"{output_path_base}_decoded.txt"
                                )

                            # Ensure unique filename based on header info
                            base, ext = os.path.splitext(
                                current_output_filename_candidate
                            )
                            counter = 1
                            final_output_filename_candidate = (
                                current_output_filename_candidate
                            )
                            while os.path.exists(final_output_filename_candidate):
                                final_output_filename_candidate = (
                                    f"{base}_{counter}{ext}"
                                )
                                counter += 1
                            output_filename = final_output_filename_candidate
                            # Header processed, skip writing this line to file
                            continue
                        except Exception as e:
                            log_event(
                                f"Error parsing header: {e}. Content will be treated as data."
                            )
                            # Fallback to treating this line as data if header parsing fails
                            decoded_content_started = True
                            buffer = (
                                line_bytes + buffer
                            )  # Put line_bytes back for data writing
                    else:  # Not a header or header already processed. This is text data.
                        decoded_content_started = (
                            True  # From now on, everything is data.
                        )
                        # Write this text line to the (now determined) output file
                        if not out_file_handle:
                            out_file_handle = open(output_filename, "ab")
                        out_file_handle.write(line_bytes)
            else:  # No newline, or already in data mode. Treat buffer as binary data.
                decoded_content_started = True

            # Write any accumulated data in buffer if in data mode
            if decoded_content_started and buffer:
                if not out_file_handle:
                    out_file_handle = open(output_filename, "ab")
                out_file_handle.write(buffer)
                buffer.clear()

            # Fetch more bytes from the stream
            fragment = bytes(
                byte for byte in islice(byte_stream, 4096) if byte is not None
            )

            if not fragment:  # End of audio stream
                # Any remaining data in buffer must be written out.
                if (
                    buffer
                ):  # Should be empty if previous logic is correct, but as a safeguard
                    if not out_file_handle:
                        out_file_handle = open(output_filename, "ab")
                    out_file_handle.write(buffer)
                    buffer.clear()

                if out_file_handle:
                    out_file_handle.close()
                    out_file_handle = None

                if timestamp and output_filename and os.path.exists(output_filename):
                    try:
                        timestamp_epoch = timestamp.timestamp()
                        os.utime(output_filename, (timestamp_epoch, timestamp_epoch))
                    except Exception as e:
                        log_event(
                            f"Error setting file timestamp for {output_filename}: {e}"
                        )

                log_event(f"Decoded data were saved to file: {output_filename}")
                wf.close()
                return output_filename

            buffer.extend(fragment)
            # If after extending buffer we are still not in decoded_content_started mode,
            # it means we are still looking for the header. The loop will check again.

    except wave.Error as e:
        log_event(f"Error opening or reading WAV file {file_to_decode}: {e}")
        if wf:
            wf.close()
        if out_file_handle:
            out_file_handle.close()
        return None
    except Exception as e:
        log_event(f"An unexpected error occurred during decoding: {e}")
        if wf:
            wf.close()
        if out_file_handle:
            out_file_handle.close()
        return None


if __name__ == "__main__":
    print(f"Text2Audio Encoder/Decoder v{__version__}\n{license}")
    loading_animation.start()
    load_cfg()  # Loads global config_main

    # Initialize global pulses for potential standalone use (e.g. if menu was active)
    # These are based on the global config_main.
    # Refactored functions kcs_encode_wav and kcs_decode_wav create their own local pulses.
    ONES_FREQ = config_main["ZERO_FREQ"] * config_main["ONES_MULT"]
    FRAMERATE = ONES_FREQ * 2

    # make_square_wave now needs config_main explicitly for standalone init
    one_pulse = make_square_wave(ONES_FREQ, FRAMERATE, config_main) * 8
    zero_pulse = make_square_wave(config_main["ZERO_FREQ"], FRAMERATE, config_main) * 4
    null_pulse = ((zero_pulse * 9) + (one_pulse * 2)) * 10

    if config_main["EXPLAIN_OPTIONS"]:
        template = "({}) {} - {}"
    else:
        template = "({}) {}"

    loading_animation.stop()
    log_event("program started")

    while True:
        cls_console()

        print(f"Text2Audio Encoder/Decoder v{__version__}")

        # displaying the list in the main menu
        for i, (choice_main_menu, description) in enumerate(MAIN_MENU_OPTIONS, 1):
            print(template.format(i, choice_main_menu, description))

        usr_input = input(f"{INPUT_SIGN}").strip()

        if usr_input.isdigit():  # check if a digit is entered
            index = int(usr_input) - 1
            if (
                0 <= index < len(MAIN_MENU_OPTIONS)
            ):  # check if the digit is within the range
                usr_input = MAIN_MENU_OPTIONS[index][0]

        for choice_main_menu, description in MAIN_MENU_OPTIONS:
            if usr_input == choice_main_menu:
                if choice_main_menu == "Encode text":
                    # This would now need to gather inputs and pass to the refactored kcs_encode_wav
                    in_file = input("ENCODE\nInput file name: ")
                    out_file = get_filename_with_new_extension(in_file, "wav")
                    loading_animation.start()
                    if kcs_encode_wav(
                        in_file, out_file, config_main
                    ):  # Pass global config_main for standalone
                        loading_animation.stop()
                        log_event(f"Standalone encode successful: {out_file}")
                    else:
                        loading_animation.stop()
                        log_event(f"Standalone encode failed.")
                    time.sleep(1)

                elif choice_main_menu == "Decode text":
                    # This would now need to gather inputs and pass to the refactored kcs_decode_wav
                    in_file = input("DECODE\nInput file name: ")
                    # Base for output, e.g., derived from input or a fixed name
                    out_base = os.path.splitext(os.path.basename(in_file))[0]
                    loading_animation.start()
                    decoded_file = kcs_decode_wav(
                        in_file, out_base, config_main
                    )  # Pass global config_main
                    if decoded_file:
                        loading_animation.stop()
                        log_event(f"Standalone decode successful: {decoded_file}")
                    else:
                        loading_animation.stop()
                        log_event(f"Standalone decode failed.")
                    time.sleep(1)

                elif choice_main_menu == "Adjust Frequencies":
                    updated_cfg = adjust_frequencies(
                        config_main
                    )  # This already uses input() and saves config
                    if updated_cfg:
                        # config_main is already updated by adjust_frequencies
                        ONES_FREQ = config_main["ZERO_FREQ"] * config_main["ONES_MULT"]
                        FRAMERATE = ONES_FREQ * 2
                        one_pulse = (
                            make_square_wave(ONES_FREQ, FRAMERATE, config_main) * 8
                        )
                        zero_pulse = (
                            make_square_wave(
                                config_main["ZERO_FREQ"], FRAMERATE, config_main
                            )
                            * 4
                        )
                        null_pulse = ((zero_pulse * 9) + (one_pulse * 2)) * 10
                        log_event(
                            "Frequencies updated and pulses re-initialized for standalone mode."
                        )

                elif choice_main_menu == "Exit program":
                    log_event("exiting program")
                    exit(0)
