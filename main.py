# Filip Pawlowski 2023 (filippawlowski2012@gmail.com) 2023
# ---------------------------------------------------------
# based on: py-kcs by David Beazley (http://www.dabeaz.com)
# ---------------------------------------------------------


from collections import deque
from itertools import islice
import wave
import os
import math
from PIL import Image

# A few global parameters related to the encoding
ZERO_FREQ = 1000  # Hz (per KCS)
ONES_FREQ = ZERO_FREQ * 2  # Hz (per KCS)
FRAMERATE = ONES_FREQ * 2  # Hz

AMPLITUDE = 128  # Amplitude of generated square waves
CENTER = 128  # Center point of generated waves

input_sign = '>>> '
template = "({}) {}"
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


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


# --- --- ---
# --- --- ---
# --- --- ---
def img2txt(image_path):
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
    img2txt_filepath = os.path.join(os.path.dirname(image_path), output_filename)
    with open(img2txt_filepath, "w") as f:
        f.write(f"#---\n{width}x{height}x{file_name_in}\n#---\n")
        for count, color in quantized_data:
            f.write(f"{count}{color}")
        f.write("\n#---\n")

    print(f"Text saved to {img2txt_filepath}")

    return img2txt_filepath


def txt2img(txt_path):
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

    print(f'Image saved to {output_filepath}')

    return output_filename


# --- --- ---
# --- --- ---
# --- --- ---

def img2wav(image_path):
    txt_file_path = img2txt(image_path)


def wav2img():
    pass


# --- --- ---
# --- --- ---
# --- --- ---
# Generate a sequence representing sign bits
def generate_wav_sign_change_bits(wavefile):
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


# Generate a sequence of data bytes by sampling the stream of sign change bits
def generate_bytes(bitstream, framerate):
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


# Create a single square wave cycle of a given frequency
def make_square_wave(freq, framerate):
    n = int(framerate / freq / 2)
    return bytearray([CENTER - AMPLITUDE // 2]) * n + \
        bytearray([CENTER + AMPLITUDE // 2]) * n


# MAIN MENU
def main():
    choices_tape_menu = [
        ('txt2wav', ''),
        ('wav2txt', ''),
        ('img2wav', ''),
        ('wav2img', ''),
        ('exit', ''),
    ]

    while True:

        clear_terminal()

        for i, (choice_main_menu, description) in enumerate(choices_tape_menu,
                                                            1):  # displaying the list in the main menu
            print(template.format(i, choice_main_menu, description))

        usr_input = input(f'{input_sign}').strip()

        if usr_input.isdigit():  # check if a digit is entered
            index = int(usr_input) - 1
            if 0 <= index < len(choices_tape_menu):  # check if the digit is within the range
                usr_input = choices_tape_menu[index][0]

        for choice_main_menu, description in choices_tape_menu:  # display the list

            if usr_input == choice_main_menu:

                if choice_main_menu == 'txt2wav':
                    in_filename = input('txt2wav\
                                            \nInput file name: ')
                    out_filename = f'{in_filename}.wav'

                    with open(in_filename, "rb") as file:
                        rawdata = file.read()

                    # Write a WAV file with encoded data. leader and trailer specify the
                    # number of seconds of carrier signal to encode before and after the data

                    w = wave.open(out_filename, "wb")
                    w.setnchannels(1)
                    w.setsampwidth(1)
                    w.setframerate(FRAMERATE)

                    # Encode the actual data
                    encoded_data = bytearray()

                    # Write the leader
                    w.writeframes(one_pulse * (int(FRAMERATE / len(one_pulse)) * 5))

                    for byteval in rawdata:
                        # Take a single byte value and turn it into a bytearray representing
                        # the associated waveform along with the required start and stop bits.

                        bitmasks = [0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80]
                        # The start bit (0)
                        encoded = bytearray(zero_pulse)
                        # 8 data bits
                        for mask in bitmasks:
                            encoded.extend(one_pulse if (byteval & mask) else zero_pulse)
                        # Two stop bits (1)
                        encoded.extend(one_pulse)
                        encoded.extend(one_pulse)

                        encoded_data.extend(encoded)
                        if byteval == 0x0d:
                            # If CR, emit a short pause (10 NULL bytes)
                            encoded_data.extend(null_pulse)

                    w.writeframes(encoded_data)

                    # Write the trailer
                    w.writeframes(one_pulse * (int(FRAMERATE / len(one_pulse)) * 5))
                    w.close()
                    print(f"Text file was saved successfully: {out_filename}")

                elif choice_main_menu == 'wav2txt':
                    file_to_decode = input('wav2txt\
                                                \nInput file name: ')

                    wf = wave.open(file_to_decode, "rb")
                    output_file_name = f"{file_to_decode}_decoded.txt"
                    sign_changes = generate_wav_sign_change_bits(wf)
                    byte_stream = generate_bytes(sign_changes, wf.getframerate())

                    buffer = bytearray()
                    while True:
                        linebreak = buffer.find(b'\n')
                        if linebreak >= 0:
                            line = buffer[:linebreak + 1].replace(b'\r\n', b'\n')
                            buffer = buffer[linebreak + 1:]
                            with open(output_file_name, "ab") as outf:
                                outf.write(line)
                        else:
                            fragment = bytes(byte for byte in islice(byte_stream, 80) if byte)
                            if not fragment:
                                with open(output_file_name, "ab") as outf:
                                    outf.write(buffer)
                                print(f"Saved to file: {output_file_name}")
                                break
                            buffer.extend(fragment)

                elif choice_main_menu == 'img2wav':
                    image_path = input("img2wav\
                        \nProvide the path to the image file: ")
                    img2txt(image_path)

                elif choice_main_menu == 'wav2img':
                    input("unavailable")
                    # image_path = input("wav2img\
                    #     \nProvide the path to the image file: ")
                    # wav2img(image_path)

                elif choice_main_menu == 'exit':
                    break


# --- --- ---
# --- --- ---
# --- --- ---

# Create the wave patterns that encode 1s and 0s
one_pulse = make_square_wave(ONES_FREQ, FRAMERATE) * 8
zero_pulse = make_square_wave(ZERO_FREQ, FRAMERATE) * 4

# Pause to insert after carriage returns (10 NULL bytes)
null_pulse = ((zero_pulse * 9) + (one_pulse * 2)) * 10

# --- --- ---
# --- --- ---
# --- --- ---

main()
