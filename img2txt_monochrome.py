# image2hex_monochrome.py
# Filip Pawlowski 2023
# filippawlowski2012gmail.com

import os
from PIL import Image


def image_to_binary(image_path):
    # Open the image using the PIL library
    image = Image.open(image_path)

    # Convert the image to 2-bit bitmap
    image = image.convert("1", dither=Image.Dither.NONE)

    # Get the dimensions of the image
    width, height = image.size
    dimensions = f"{width}x{height}"

    # Create a string of binary values
    binary_values = []
    for y in range(height):
        row_values = []
        count = 0
        previous_value = None
        for x in range(width):
            pixel = image.getpixel((x, y))
            binary_value = "W" if pixel == 255 else "B"

            if binary_value == previous_value:
                count += 1
            else:
                if previous_value is not None:
                    if previous_value == "B":
                        row_values.append(f"B{count}")
                    else:
                        row_values.append(f"W{count}")
                count = 1

            previous_value = binary_value

        if previous_value is not None:
            if previous_value == "B":
                row_values.append(f"B{count}")
            else:
                row_values.append(f"W{count}")

        binary_values.append("".join(row_values))

    # Generate the output file path
    output_path = os.path.splitext(image_path)[0] + ".txt"

    # Save the results to a file
    with open(output_path, "w") as file:
        file.write("#---\n")
        file.write(f"{dimensions}\n")
        file.write("#---\n")
        file.write("\n".join(binary_values))
        file.write("\n#---")

    print(f"Text file was saved successfully: {output_path}")

    return output_path


def binary_to_image(txt_path):
    with open(txt_path, "r") as file:
        lines = file.readlines()

        # Read and validate the dimensions and binary data
        dimensions = lines[1].strip()
        binary_data = []

        for line in lines[3:-1]:
            binary_value = line.strip()
            if binary_value[0] == "B" or binary_value[0] == "W":
                count = 0
                color = 0 if binary_value[0] == "B" else 255
                for char in binary_value:
                    if char == "B" or char == "W":
                        if count > 0:
                            binary_data.extend([color] * count)
                            count = 0
                        color = 0 if char == "B" else 255
                    else:
                        count = count * 10 + int(char)

                if count > 0:
                    binary_data.extend([color] * count)

        # Calculate the expected number of pixels based on dimensions
        width, height = map(int, dimensions.split("x"))
        expected_num_pixels = width * height

        # Create a new image based on the read data
        image = Image.new("L", (width, height))
        image.putdata(binary_data)

        # Generate the output file path
        output_filename = os.path.splitext(txt_path)[0] + ".png"
        output_path = os.path.join(os.path.dirname(txt_path), output_filename)

        # Save the image to file
        image.save(output_path)
        print(f"Image was saved successfully as: {output_path}")


if __name__ == '__main__':
    input_sign = '>>> '
    template = "({}) {}"
    choices_main_menu = [
        ('Encode image file', ''),
        ('Decode image file', ''),
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

            if choice_main_menu == 'Encode image file':  # image to text
                in_filename = input('ENCODE IMAGE\nInput file name: ')
                image_to_binary(in_filename)

            elif choice_main_menu == 'Decode image file':  # text to image
                file_to_decode = input('DECODE IMAGE\nInput file name: ')
                binary_to_image(file_to_decode)

            elif choice_main_menu == 'Exit program':
                raise SystemExit
