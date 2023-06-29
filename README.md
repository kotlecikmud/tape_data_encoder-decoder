# tape_enco/deco Repository

This repository contains three scripts developed by Filip Pawlowski in 2023. These scripts are used for encoding and decoding data using different techniques.

## base64encoder.py

This script provides functions for encoding and decoding binary data using Base64. It reads binary data from a file, encodes it to Base64, and saves the encoded data to a file. It also supports decoding Base64 data back to binary and reconstructing the original file.

The `base64encoder.py` script can be used in various scenarios where data needs to be encoded or decoded using Base64. It is especially useful when working with file formats that require Base64 encoding, such as JSON or XML.

To encode a file, you can run the following command:

```bash
python base64encoder.py encode input_file output_file
```

Where `input_file` is the path to the file you want to encode, and `output_file` is the desired path to save the encoded data.

To decode a file, you can use the following command:

```bash
python base64encoder.py decode input_file output_file
```

Where `input_file` is the path to the Base64-encoded file, and `output_file` is the desired path to save the decoded data.

## kcs_enco-deco.py

Based on "py-kcs" by David Beazley, this script encodes and decodes text using audio signals. It generates square wave patterns to represent 1s and 0s, and encodes the text by modulating the frequency of the waves. It can encode text into a WAV file and decode text from a WAV file.

The `kcs_enco-deco.py` script is particularly useful for scenarios where text data needs to be transmitted or stored using audio signals. It can be used for applications such as audio-based communication or data embedding.

To encode text into an audio file, you can run the following command:

```bash
python kcs_enco-deco.py encode input_text output_audio.wav
```

Where `input_text` is the text you want to encode, and `output_audio.wav` is the desired name of the output audio file.

To decode text from an audio file, you can use the following command:

Where `input_text` is the text you want to encode, and `output_audio.wav` is the desired name of the output audio file.

```bash
python kcs_enco-deco.py decode input_audio.wav output_text.txt
```

Where `input_audio.wav` is the path to the audio file containing the encoded text, and `output_text.txt` is the desired path to save the decoded text.

## img2txt.py

This script is used for encoding and decoding images into text format. It quantizes the colors in the image and represents them with corresponding characters. It can encode an image into a text file and decode the text file back into an image.

The `img2txt.py` script is helpful when there is a need to convert images into a textual representation or vice versa. It can be used for tasks such as embedding images in text-based documents or storing images as text data.

To encode an image into a text file, you can run the following command:

```bash
python img2txt.py encode input_image.png output_text.txt
```

Where `input_image.png` is the path to the image file you want to encode, and `output_text.txt` is the desired path to save the encoded text.

To decode the text file back into an image, you can use the following command:

```bash
python img2txt.py decode input_text.txt output_image.png
```

Where `input_text.txt` is the path to the text file containing the encoded image, and `output_image.png` is the desired path to save the decoded image.

Each script has its own functionality and can be used independently. They provide command-line interfaces for user interaction and offer various options for encoding and decoding data.

For any inquiries, you can contact the author, Filip Pawlowski, via email at filippawlowski2012@gmail.com.
