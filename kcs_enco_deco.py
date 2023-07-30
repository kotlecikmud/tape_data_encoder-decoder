# kcs_enco-deco.py
# Filip Pawlowski 2023 (filippawlowski2012@gmail.com) 2023
# ---------------------------------------------------------
# based on: py-kcs by David Beazley (http://www.dabeaz.com)
# ---------------------------------------------------------


from collections import deque
from itertools import islice
import wave, os, datetime

# A few global parameters related to the encoding
ZERO_FREQ = 1000  # Hz (per KCS)
ONES_FREQ = ZERO_FREQ * 2  # Hz (per KCS)
FRAMERATE = ONES_FREQ * 2  # Hz

AMPLITUDE = 128  # Amplitude of generated square waves
CENTER = 128  # Center point of generated waves


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


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


# Create the wave patterns that encode 1s and 0s
one_pulse = make_square_wave(ONES_FREQ, FRAMERATE) * 8
zero_pulse = make_square_wave(ZERO_FREQ, FRAMERATE) * 4

# Pause to insert after carriage returns (10 NULL bytes)
null_pulse = ((zero_pulse * 9) + (one_pulse * 2)) * 10


# Take a single byte value and turn it into a bytearray representing
# the associated waveform along with the required start and stop bits.

def kcs_encode_byte(byteval):
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


# Include the run_length_encode function defined earlier for RLE compression
def run_length_encode(data):
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


# Write a WAV file with encoded data. leader and trailer specify the
# number of seconds of carrier signal to encode before and after the data

def kcs_write_wav(filename, rawdata, leader, trailer):
    w = wave.open(filename, "wb")
    w.setnchannels(1)
    w.setsampwidth(1)
    w.setframerate(FRAMERATE)

    # Encode the actual data
    encoded_data = bytearray()

    # Write the leader
    w.writeframes(one_pulse * (int(FRAMERATE / len(one_pulse)) * leader))

    for byteval in rawdata:
        encoded_data.extend(kcs_encode_byte(byteval))
        if byteval == 0x0d:
            # If CR, emit a short pause (10 NULL bytes)
            encoded_data.extend(null_pulse)

    # # Write the timestamp data at the beginning of the encoded data
    # timestamp_data = "###" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "###\n"
    # encoded_data = timestamp_data.encode() + encoded_data
    w.writeframes(encoded_data)

    # Write the trailer
    w.writeframes(one_pulse * (int(FRAMERATE / len(one_pulse)) * trailer))
    w.close()
    print(f"Text file was saved successfully: {filename}")


if __name__ == '__main__':
    input_sign = '>>> '
    template = "({}) {}"
    choices_main_menu = [
        ('Encode text', ''),
        ('Decode text', ''),
        ('Exit program', ''),
    ]

    for i, (choice_main_menu, description) in enumerate(choices_main_menu, 1):  # displaying the list in the main menu
        print(template.format(i, choice_main_menu, description))

    usr_input = input(f'{input_sign}').strip()

    if usr_input.isdigit():  # check if a digit is entered
        index = int(usr_input) - 1
        if 0 <= index < len(choices_main_menu):  # check if the digit is within the range
            usr_input = choices_main_menu[index][0]

    for choice_main_menu, description in choices_main_menu:  # display the list

        if usr_input == choice_main_menu:

            if choice_main_menu == 'Encode text':
                in_filename = input('ENCODE\
                        \nInput file name: ')
                out_filename = f'{in_filename}.wav'

                with open(in_filename, "rb") as file:
                    rawdata = file.read()

                kcs_write_wav(out_filename, rawdata, 5, 5)

            elif choice_main_menu == 'Decode text':
                file_to_decode = input('DECODE\
                            \nInput file name: ')

                wf = wave.open(file_to_decode, "rb")
                sign_changes = generate_wav_sign_change_bits(wf)
                byte_stream = generate_bytes(sign_changes, wf.getframerate())

                buffer = bytearray()
                while True:
                    linebreak = buffer.find(b'\n')
                    if linebreak >= 0:
                        line = buffer[:linebreak + 1].replace(b'\r\n', b'\n')
                        buffer = buffer[linebreak + 1:]
                        with open("decoded.txt", "ab") as outf:
                            outf.write(line)
                    else:
                        fragment = bytes(byte for byte in islice(byte_stream, 80) if byte)
                        if not fragment:
                            with open("decoded.txt", "ab") as outf:
                                outf.write(buffer)
                            print("Decoded data were saved to file: decoded.txt")
                            break
                        buffer.extend(fragment)

            elif choice_main_menu == 'Exit program':
                raise SystemExit
