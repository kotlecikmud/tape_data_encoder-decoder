# main.py
# Unified Tape Data Encoder-Decoder & All-In-One Toolkit with Tkinter GUI
# Single Main Application File containing all tools (KCS audio tape, Image <-> Binary, QR Code, Polish Diacritics).

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# --- Import tool modules ---
try:
    import kcs_enco_deco
    KCS_AVAILABLE = True
except Exception as e:
    KCS_AVAILABLE = False
    print(f"Warning: kcs_enco_deco not available: {e}")

try:
    import img2txt
    IMG_AVAILABLE = True
except Exception as e:
    IMG_AVAILABLE = False
    print(f"Warning: img2txt not available: {e}")

try:
    import gen_qr
    QR_AVAILABLE = True
except Exception as e:
    QR_AVAILABLE = False
    print(f"Warning: gen_qr not available: {e}")

try:
    import replace_polish_signs
    POLISH_AVAILABLE = True
except Exception as e:
    POLISH_AVAILABLE = False
    print(f"Warning: replace_polish_signs not available: {e}")


class RedirectText:
    """Redirects print statements to a Tkinter ScrolledText widget."""
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, string)
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')
        if self.text_widget.winfo_exists():
            self.text_widget.after(0, append)

    def flush(self):
        pass


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tape Data Encoder & Decoder - Unified Suite")
        self.geometry("900x700")
        self.minsize(800, 600)

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Main container with Notebook (Tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create Tabs
        self.tab_kcs = ttk.Frame(self.notebook)
        self.tab_img = ttk.Frame(self.notebook)
        self.tab_qr = ttk.Frame(self.notebook)
        self.tab_polish = ttk.Frame(self.notebook)
        self.tab_logs = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_kcs, text="Audio / Tape (KCS)")
        self.notebook.add(self.tab_img, text="Image / Binary Converter")
        self.notebook.add(self.tab_qr, text="QR Code Generator")
        self.notebook.add(self.tab_polish, text="Polish Diacritics")
        self.notebook.add(self.tab_logs, text="Console Logs")

        self.build_kcs_tab()
        self.build_img_tab()
        self.build_qr_tab()
        self.build_polish_tab()
        self.build_logs_tab()

        # Redirect stdout/stderr to log console
        self.stdout_redirector = RedirectText(self.log_text)
        sys.stdout = self.stdout_redirector
        sys.stderr = self.stdout_redirector

        print("Unified Tape Data Encoder-Decoder Suite initialized successfully.")

    def run_in_thread(self, target, *args):
        """Run task in background thread to keep GUI responsive."""
        thread = threading.Thread(target=target, args=args, daemon=True)
        thread.start()

    # ==================== Tab 1: KCS Audio / Tape ====================
    def build_kcs_tab(self):
        frame = ttk.LabelFrame(self.tab_kcs, text="Kansas City Standard (KCS) Audio Tape Encoder / Decoder")
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Input file
        ttk.Label(frame, text="Input File / Text:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.kcs_input_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.kcs_input_var, width=50).grid(row=0, column=1, padx=5, pady=10)
        ttk.Button(frame, text="Browse...", command=lambda: self.browse_file(self.kcs_input_var)).grid(row=0, column=2, padx=5, pady=10)

        # Output file
        ttk.Label(frame, text="Output File (.wav or .txt):").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        self.kcs_output_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.kcs_output_var, width=50).grid(row=1, column=1, padx=5, pady=10)
        ttk.Button(frame, text="Browse...", command=lambda: self.browse_save_file(self.kcs_output_var)).grid(row=1, column=2, padx=5, pady=10)

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=20)

        ttk.Button(btn_frame, text="Encode to KCS WAV", command=self.kcs_encode_action, width=20).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Decode KCS WAV", command=self.kcs_decode_action, width=20).pack(side=tk.LEFT, padx=10)

    def kcs_encode_action(self):
        if not KCS_AVAILABLE:
            messagebox.showerror("Error", "kcs_enco_deco module is not available.")
            return
        inp = self.kcs_input_var.get().strip()
        out = self.kcs_output_var.get().strip()
        if not inp:
            messagebox.showerror("Error", "Please specify an input file or text.")
            return
        if not out:
            base, _ = os.path.splitext(inp)
            out = base + "_encoded.wav"
            self.kcs_output_var.set(out)

        def task():
            try:
                print(f"Starting KCS Encoding: {inp} -> {out}")
                cfg = kcs_enco_deco.load_cfg()
                kcs_enco_deco.kcs_encode_wav(inp, out, cfg)
                messagebox.showinfo("Success", f"KCS encoding completed:\n{out}")
            except Exception as e:
                print(f"Error in KCS Encoding: {e}")
                messagebox.showerror("Error", str(e))

        self.run_in_thread(task)

    def kcs_decode_action(self):
        if not KCS_AVAILABLE:
            messagebox.showerror("Error", "kcs_enco_deco module is not available.")
            return
        inp = self.kcs_input_var.get().strip()
        out = self.kcs_output_var.get().strip()
        if not inp:
            messagebox.showerror("Error", "Please specify an input WAV file.")
            return
        if not out:
            base, _ = os.path.splitext(inp)
            out = base + "_decoded.txt"
            self.kcs_output_var.set(out)

        def task():
            try:
                print(f"Starting KCS Decoding: {inp} -> {out}")
                cfg = kcs_enco_deco.load_cfg()
                kcs_enco_deco.kcs_decode_wav(inp, out, cfg)
                messagebox.showinfo("Success", f"KCS decoding completed:\n{out}")
            except Exception as e:
                print(f"Error in KCS Decoding: {e}")
                messagebox.showerror("Error", str(e))

        self.run_in_thread(task)

    # ==================== Tab 2: Image / Binary Converter ====================
    def build_img_tab(self):
        frame = ttk.LabelFrame(self.tab_img, text="Image <-> Binary Converter (Fixed Binary Image Formats)")
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Input File
        ttk.Label(frame, text="Input File (Image / .bin):").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.img_input_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.img_input_var, width=50).grid(row=0, column=1, padx=5, pady=10)
        ttk.Button(frame, text="Browse...", command=lambda: self.browse_file(self.img_input_var)).grid(row=0, column=2, padx=5, pady=10)

        # Mode for Encoding
        ttk.Label(frame, text="Binary Encoding Mode:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        self.img_mode_var = tk.StringVar(value="MONO8")
        modes = ["MONO2", "MONO4", "MONO8", "RGB4", "RGB8"]
        ttk.Combobox(frame, textvariable=self.img_mode_var, values=modes, state="readonly", width=15).grid(row=1, column=1, sticky=tk.W, padx=5, pady=10)

        # Output format for Decoding
        ttk.Label(frame, text="Decoded Image Format:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        self.img_format_var = tk.StringVar(value="png")
        formats = ["png", "bmp", "jpg", "jpeg", "webp"]
        ttk.Combobox(frame, textvariable=self.img_format_var, values=formats, state="readonly", width=15).grid(row=2, column=1, sticky=tk.W, padx=5, pady=10)

        # Output File
        ttk.Label(frame, text="Output File Path:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
        self.img_output_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.img_output_var, width=50).grid(row=3, column=1, padx=5, pady=10)
        ttk.Button(frame, text="Browse...", command=lambda: self.browse_save_file(self.img_output_var)).grid(row=3, column=2, padx=5, pady=10)

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=20)

        ttk.Button(btn_frame, text="Encode Image to Binary", command=self.img_encode_action, width=22).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Decode Binary to Image", command=self.img_decode_action, width=22).pack(side=tk.LEFT, padx=10)

    def img_encode_action(self):
        if not IMG_AVAILABLE:
            messagebox.showerror("Error", "img2txt module is not available.")
            return
        inp = self.img_input_var.get().strip()
        mode = self.img_mode_var.get().strip()
        if not inp:
            messagebox.showerror("Error", "Please select an input image file.")
            return

        def task():
            try:
                print(f"Encoding image '{inp}' with mode {mode}...")
                out_path = img2txt.encode(inp, mode=mode)
                self.img_output_var.set(out_path)
                messagebox.showinfo("Success", f"Image successfully encoded to:\n{out_path}")
            except Exception as e:
                print(f"Error encoding image: {e}")
                messagebox.showerror("Error", str(e))

        self.run_in_thread(task)

    def img_decode_action(self):
        if not IMG_AVAILABLE:
            messagebox.showerror("Error", "img2txt module is not available.")
            return
        inp = self.img_input_var.get().strip()
        out_format = self.img_format_var.get().strip().lower()
        if not inp:
            messagebox.showerror("Error", "Please select an encoded binary file.")
            return

        def task():
            try:
                print(f"Decoding binary file '{inp}' to image format {out_format.upper()}...")
                decoded_path = img2txt.decode(inp)
                if decoded_path and os.path.exists(decoded_path):
                    if out_format not in ["png", ""]:
                        from PIL import Image
                        img = Image.open(decoded_path)
                        new_out_path = os.path.splitext(inp)[0] + f"_decoded.{out_format}"
                        img.save(new_out_path, format=out_format.upper() if out_format != 'jpg' else 'JPEG')
                        decoded_path = new_out_path
                    self.img_output_var.set(decoded_path)
                    messagebox.showinfo("Success", f"Binary successfully decoded to image:\n{decoded_path}")
                else:
                    messagebox.showerror("Error", "Decoding failed to produce output image.")
            except Exception as e:
                print(f"Error decoding binary file: {e}")
                messagebox.showerror("Error", str(e))

        self.run_in_thread(task)

    # ==================== Tab 3: QR Code Generator ====================
    def build_qr_tab(self):
        frame = ttk.LabelFrame(self.tab_qr, text="QR Code Generator")
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        ttk.Label(frame, text="Data / Text to Encode:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.qr_input_text = tk.Text(frame, height=5, width=50)
        self.qr_input_text.grid(row=0, column=1, padx=5, pady=10)

        ttk.Label(frame, text="Output QR Image Path:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        self.qr_output_var = tk.StringVar(value="qrcode.png")
        ttk.Entry(frame, textvariable=self.qr_output_var, width=50).grid(row=1, column=1, padx=5, pady=10)
        ttk.Button(frame, text="Browse...", command=lambda: self.browse_save_file(self.qr_output_var)).grid(row=1, column=2, padx=5, pady=10)

        ttk.Button(frame, text="Generate QR Code", command=self.qr_generate_action, width=25).grid(row=2, column=1, pady=20)

    def qr_generate_action(self):
        if not QR_AVAILABLE:
            messagebox.showerror("Error", "gen_qr module is not available.")
            return
        data = self.qr_input_text.get("1.0", tk.END).strip()
        out_path = self.qr_output_var.get().strip()
        if not data:
            messagebox.showerror("Error", "Please enter data or text for the QR code.")
            return
        if not out_path:
            out_path = "qrcode.png"
            self.qr_output_var.set(out_path)

        def task():
            try:
                print(f"Generating QR code -> {out_path}")
                gen_qr.generate_qr_code(data, out_path)
                messagebox.showinfo("Success", f"QR Code generated successfully:\n{out_path}")
            except Exception as e:
                print(f"Error generating QR code: {e}")
                messagebox.showerror("Error", str(e))

        self.run_in_thread(task)

    # ==================== Tab 4: Polish Diacritics ====================
    def build_polish_tab(self):
        frame = ttk.LabelFrame(self.tab_polish, text="Polish Diacritics / Signs Processor")
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        ttk.Label(frame, text="Input Text / File:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.polish_input_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.polish_input_var, width=50).grid(row=0, column=1, padx=5, pady=10)
        ttk.Button(frame, text="Browse...", command=lambda: self.browse_file(self.polish_input_var)).grid(row=0, column=2, padx=5, pady=10)

        ttk.Label(frame, text="Or Direct Text Input:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        self.polish_text_box = tk.Text(frame, height=6, width=50)
        self.polish_text_box.grid(row=1, column=1, padx=5, pady=10)

        ttk.Button(frame, text="Process / Replace Polish Signs", command=self.polish_process_action, width=30).grid(row=2, column=1, pady=20)

    def polish_process_action(self):
        if not POLISH_AVAILABLE:
            messagebox.showerror("Error", "replace_polish_signs module is not available.")
            return
        inp = self.polish_input_var.get().strip()
        direct_text = self.polish_text_box.get("1.0", tk.END).strip()

        def task():
            try:
                if inp:
                    print(f"Processing Polish signs in file: {inp}")
                    replace_polish_signs.process_file(inp)
                    messagebox.showinfo("Success", f"Processed file successfully: {inp}")
                elif direct_text:
                    print("Processing direct text input for Polish signs...")
                    res = direct_text
                    for k, v in replace_polish_signs.REPLACEMENTS_DICTIONARY.items():
                        res = res.replace(k, v.strip("'"))
                    self.polish_text_box.delete("1.0", tk.END)
                    self.polish_text_box.insert("1.0", res)
                    print(f"Result:\n{res}")
                    messagebox.showinfo("Success", "Polish signs processed successfully.")
                else:
                    messagebox.showerror("Error", "Please provide either an input file or direct text.")
            except Exception as e:
                print(f"Error processing Polish signs: {e}")
                messagebox.showerror("Error", str(e))

        self.run_in_thread(task)

    # ==================== Tab 5: Console Logs ====================
    def build_logs_tab(self):
        frame = ttk.LabelFrame(self.tab_logs, text="Application Activity Log & Console")
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.log_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, state='disabled', bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Button(frame, text="Clear Logs", command=lambda: self.clear_logs()).pack(pady=5)

    def clear_logs(self):
        self.log_text.configure(state='normal')
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state='disabled')

    # ==================== Helpers ====================
    def browse_file(self, string_var):
        filename = filedialog.askopenfilename()
        if filename:
            string_var.set(filename)

    def browse_save_file(self, string_var):
        filename = filedialog.asksaveasfilename()
        if filename:
            string_var.set(filename)


if __name__ == "__main__":
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        os.chdir(sys._MEIPASS)
    app = MainApp()
    app.mainloop()
