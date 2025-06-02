import os
import sys  # For resource_path if needed

# --- Imports from our modules ---
try:
    # KCS functions and configuration
    from kcs_enco_deco import (
        kcs_encode_wav,
        kcs_decode_wav,
        load_cfg as kcs_load_cfg,
        config_main as kcs_config_global,  # This is the global config from kcs_enco_deco
        resource_path as kcs_resource_path,  # For loading config
        get_filename_with_new_extension as kcs_get_filename_ext,
        adjust_frequencies as kcs_adjust_frequencies,  # If we add this option later
    )

    # Initialize KCS config immediately
    kcs_initial_config = kcs_load_cfg()
    # The kcs_config_global in kcs_enco_deco module is now populated.
    # We will pass kcs_config_global to kcs_encode_wav and kcs_decode_wav.
    is_kcs_imported = True

except ImportError as e:
    print(f"Error importing from kcs_enco_deco: {e}")
    print("Please ensure kcs_enco_deco.py is in the same directory or Python path.")
    kcs_encode_wav = (
        kcs_decode_wav
    ) = (
        kcs_load_cfg
    ) = kcs_config_global = kcs_get_filename_ext = kcs_adjust_frequencies = None
    kcs_initial_config = {}
    is_kcs_imported = False


try:
    # Image processing functions
    from img2txt import encode as img_encode, decode as img_decode, MODES as IMG_MODES

    is_img2text_imported = True
except ImportError as e:
    print(f"Error importing from img2txt: {e}")
    print("Please ensure img2txt.py is in the same directory or Python path.")
    img_encode = img_decode = IMG_MODES = None
    is_img2text_imported = False

try:
    # Polish signs processing function
    from replace_polish_signs import process_file as process_polish_file
except ImportError as e:
    print(f"Error importing from replace_polish_signs: {e}")
    print(
        "Please ensure replace_polish_signs.py is in the same directory or Python path."
    )
    process_polish_file = None


# --- Helper Functions ---
def cls_console():
    """Clears the console."""
    os.system("cls" if os.name == "nt" else "clear")


def get_valid_filepath(prompt_message, must_exist=True):
    """Gets a valid file path from user, optionally checks for existence."""
    while True:
        filepath = input(prompt_message).strip()
        if not filepath:
            print("File path cannot be empty.")
            continue
        if must_exist and not os.path.exists(filepath):
            print(f"Error: File not found at '{filepath}'. Please try again.")
            continue
        if not must_exist and os.path.isdir(filepath):
            print(
                f"Error: Expected a file path, but got a directory: '{filepath}'. Please try again."
            )
            continue
        return filepath


def get_output_filepath(input_path, default_suffix, default_ext):
    """Generates a default output filepath and asks user to confirm or change."""
    base, _ = os.path.splitext(input_path)
    suggested_path = f"{base}{default_suffix}{default_ext}"

    while True:
        user_path = input(
            f"Enter output file path (default: {suggested_path}): "
        ).strip()
        if not user_path:
            return suggested_path

        # Basic validation: ensure it's not a directory if it exists
        if os.path.isdir(user_path):
            print(
                f"Error: Output path '{user_path}' is a directory. Please enter a valid file path."
            )
            continue

        # Ensure parent directory exists
        parent_dir = os.path.dirname(user_path)
        if (
            parent_dir
        ):  # Only try to create if parent_dir is not empty (i.e., not saving in CWD)
            if not os.path.exists(parent_dir):
                try:
                    os.makedirs(parent_dir)
                    print(f"Info: Created directory: '{parent_dir}'")
                except OSError as e:
                    print(f"Error: Could not create directory '{parent_dir}'. {e}")
                    continue  # Ask for path again
            elif not os.path.isdir(parent_dir):
                print(f"Error: Output path's parent '{parent_dir}' is not a directory.")
                continue

        return user_path


# --- Main Application Logic ---
def main():
    if not kcs_initial_config and (
        kcs_encode_wav or kcs_decode_wav
    ):  # Check if KCS part might be used
        print(
            "Warning: KCS configuration could not be loaded. KCS features might not work."
        )

    while True:
        cls_console()
        print("\n--- All-In-One Application Menu ---")
        print("1. Encode Text to KCS WAV")
        print("2. Decode KCS WAV to Text")
        print("3. Encode Image to Binary File")
        print("4. Decode Binary File to Image")
        print("5. Remove Polish Signs from Text File")
        print("6. Restore Polish Signs in Text File")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ").strip()

        # Main try-except block for unexpected errors during an operation
        try:
            if choice == "1":  # KCS Encode
                if not is_kcs_imported:
                    print(
                        "Error: KCS encode function is not available (import failed)."
                    )
                else:
                    print("\n--- Encode Text to KCS WAV ---")
                    input_file = get_valid_filepath(
                        "Enter path to the input text file: ", must_exist=True
                    )
                    if input_file:  # Proceed only if a valid input file was provided
                        output_file = get_output_filepath(
                            input_file, "_encoded", ".wav"
                        )
                        if (
                            output_file
                        ):  # Proceed only if a valid output file was provided/confirmed
                            print(
                                f"Using KCS Config: ZERO_FREQ={kcs_config_global.get('ZERO_FREQ')}, ONES_MULT={kcs_config_global.get('ONES_MULT')}"
                            )
                            try:
                                success = kcs_encode_wav(
                                    input_file, output_file, kcs_config_global
                                )
                                if success:
                                    print(
                                        f"Successfully encoded '{input_file}' to '{output_file}'"
                                    )
                                else:
                                    # The module itself should log specifics if possible
                                    print(
                                        f"Error: Failed to encode '{input_file}'. Module indicated failure."
                                    )
                            except Exception as e:
                                print(
                                    f"Error: An exception occurred during KCS encoding operation."
                                )
                                print(f"Debug details: {type(e).__name__} - {e}")

            elif choice == "2":  # KCS Decode
                if not is_kcs_imported:
                    print(
                        "Error: KCS decode function is not available (import failed)."
                    )
                else:
                    print("\n--- Decode KCS WAV to Text ---")
                    input_file = get_valid_filepath(
                        "Enter path to the KCS WAV file: ", must_exist=True
                    )
                    if input_file:
                        base_input_name = os.path.splitext(
                            os.path.basename(input_file)
                        )[0]
                        output_base_name_prompt = f"Enter base for output file name (e.g., {base_input_name}_decoded, default uses this pattern): "
                        output_base_name_user = input(output_base_name_prompt).strip()
                        if not output_base_name_user:  # Default if user enters nothing
                            output_base_name_user = base_input_name + "_decoded"

                        output_dir = os.path.dirname(input_file)
                        output_path_base_for_decode = os.path.join(
                            output_dir, output_base_name_user
                        )

                        print(
                            f"Using KCS Config: ZERO_FREQ={kcs_config_global.get('ZERO_FREQ')}, ONES_MULT={kcs_config_global.get('ONES_MULT')}"
                        )
                        try:
                            output_filename = kcs_decode_wav(
                                input_file,
                                output_path_base_for_decode,
                                kcs_config_global,
                            )
                            if output_filename:
                                print(
                                    f"Successfully decoded '{input_file}' to '{output_filename}'"
                                )
                            else:
                                print(
                                    f"Error: Failed to decode '{input_file}'. Module indicated failure."
                                )
                        except Exception as e:
                            print(
                                f"Error: An exception occurred during KCS decoding operation."
                            )
                            print(f"Debug details: {type(e).__name__} - {e}")

            elif choice == "3":  # Image Encode
                if not is_img2text_imported or not IMG_MODES:
                    print(
                        "Error: Image encode function or modes are not available (import failed)."
                    )
                else:
                    print("\n--- Encode Image to Binary File ---")
                    input_file = get_valid_filepath(
                        "Enter path to the input image file: ", must_exist=True
                    )
                    if input_file:
                        print("Available encoding modes:")
                        for key, value in IMG_MODES.items():
                            print(f"  {key}: {value}")  # Display as "1: MONO2"

                        mode_prompt = f"Select mode number (1-{len(IMG_MODES)}) or name (e.g., MONO8, default: MONO8): "
                        mode_choice_input = input(mode_prompt).strip()

                        selected_mode_name = IMG_MODES.get(
                            mode_choice_input
                        )  # Check if input is a key like "1"
                        if (
                            not selected_mode_name
                        ):  # If not a key, check if it's a value like "MONO8"
                            # Check if input matches a value in IMG_MODES (case-insensitive for value matching)
                            is_value_match = False
                            for k, v in IMG_MODES.items():
                                if mode_choice_input.upper() == v:
                                    selected_mode_name = v
                                    is_value_match = True
                                    break
                            if not is_value_match:  # Default if invalid or empty
                                selected_mode_name = "MONO8"  # Default to MONO8
                                if (
                                    mode_choice_input
                                ):  # User entered something, but it was invalid
                                    print(
                                        f"Info: Invalid mode selection '{mode_choice_input}'. Defaulting to {selected_mode_name}."
                                    )
                                else:  # User entered nothing
                                    print(
                                        f"Info: No mode selected. Defaulting to {selected_mode_name}."
                                    )
                        print(f"Selected mode: {selected_mode_name}")
                        try:
                            output_file = img_encode(input_file, selected_mode_name)
                            if output_file:
                                print(
                                    f"Successfully encoded '{input_file}' to '{output_file}' using mode {selected_mode_name}"
                                )
                            else:
                                print(
                                    f"Error: Failed to encode '{input_file}'. Module indicated failure."
                                )
                        except Exception as e:
                            print(
                                f"Error: An exception occurred during image encoding operation."
                            )
                            print(f"Debug details: {type(e).__name__} - {e}")

            elif choice == "4":  # Image Decode
                if not is_img2text_imported:
                    print(
                        "Error: Image decode function is not available (import failed)."
                    )
                else:
                    print("\n--- Decode Binary File to Image ---")
                    input_file = get_valid_filepath(
                        "Enter path to the encoded binary file: ", must_exist=True
                    )
                    if input_file:
                        try:
                            output_file = img_decode(input_file)
                            if output_file:
                                print(
                                    f"Successfully decoded '{input_file}' to '{output_file}'"
                                )
                            else:
                                print(
                                    f"Error: Failed to decode '{input_file}'. Module indicated failure."
                                )
                        except Exception as e:
                            print(
                                f"Error: An exception occurred during image decoding operation."
                            )
                            print(f"Debug details: {type(e).__name__} - {e}")

            elif choice == "5":  # Replace Polish Signs
                if not process_polish_file:
                    print(
                        "Error: Polish signs processing function is not available (import failed)."
                    )
                else:
                    print("\n--- Remove Polish Signs from Text File ---")
                    input_file = get_valid_filepath(
                        "Enter path to the input text file: ", must_exist=True
                    )
                    if input_file:
                        output_file = get_output_filepath(
                            input_file, "_removed_PL", ".txt"
                        )
                        if output_file:
                            try:
                                success = process_polish_file(
                                    input_file, output_file, "PL2"
                                )
                                if success:
                                    print(
                                        f"Successfully processed '{input_file}', Polish signs removed. Output: '{output_file}'"
                                    )
                                else:
                                    print(
                                        f"Error: Failed to process '{input_file}'. Module indicated failure."
                                    )
                            except Exception as e:
                                print(
                                    f"Error: An exception occurred during Polish sign removal."
                                )
                                print(f"Debug details: {type(e).__name__} - {e}")

            elif choice == "6":  # Restore Polish Signs
                if not process_polish_file:
                    print(
                        "Error: Polish signs processing function is not available (import failed)."
                    )
                else:
                    print("\n--- Restore Polish Signs in Text File ---")
                    input_file = get_valid_filepath(
                        "Enter path to the text file with removed Polish signs: ",
                        must_exist=True,
                    )
                    if input_file:
                        output_file = get_output_filepath(
                            input_file, "_restored_PL", ".txt"
                        )
                        if output_file:
                            try:
                                success = process_polish_file(
                                    input_file, output_file, "2PL"
                                )
                                if success:
                                    print(
                                        f"Successfully processed '{input_file}', Polish signs restored. Output: '{output_file}'"
                                    )
                                else:
                                    print(
                                        f"Error: Failed to process '{input_file}'. Module indicated failure."
                                    )
                            except Exception as e:
                                print(
                                    f"Error: An exception occurred during Polish sign restoration."
                                )
                                print(f"Debug details: {type(e).__name__} - {e}")

            elif choice == "7":
                print("Exiting application...")
                break

            else:  # Handles invalid menu choices (non-numeric or out of range)
                print("Error: Invalid choice. Please enter a number between 1 and 7.")

        except (
            Exception
        ) as e:  # Catch-all for truly unexpected errors in the main loop or input functions
            print(
                f"Critical Error: An unexpected issue occurred in the application: {e}"
            )
            print(f"Debug details: {type(e).__name__} - {e}")
            # For more detailed debugging if needed:
            # import traceback
            # traceback.print_exc()

        if choice not in ("7"):  # Don't pause if exiting
            input("\nPress Enter to return to the menu...")


if __name__ == "__main__":
    # This check is important if resource_path relies on sys._MEIPASS for PyInstaller
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        os.chdir(
            sys._MEIPASS
        )  # Change CWD to where bundled files are if running as PyInstaller bundle
    main()
