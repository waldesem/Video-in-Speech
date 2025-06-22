"""Video to text converter with GUI."""

import os
import tkinter as tk
from pathlib import Path
from threading import Thread
from tkinter import filedialog, messagebox, ttk

from moviepy import AudioFileClip
from speech_recognition import AudioFile, Recognizer


class VideoToTextConverter:
    """GUI for media to text conversion."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialize the GUI."""
        self.root = root
        self.root.title("Media to Text Converter")
        self.root.geometry("540x260")
        self.root.resizable(width=False, height=False)

        # Variables
        self.selected_file = None
        self.output_file = None

        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the UI components."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Media to Text Converter",
            font=("Arial", 16, "bold"),
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # File selection
        ttk.Label(main_frame, text="Select media file:").grid(
            row=1,
            column=0,
            sticky=tk.W,
            pady=5,
        )

        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.file_label = ttk.Label(
            file_frame,
            text="No file selected",
            foreground="gray",
            width=50,
        )
        self.file_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        self.upload_btn = ttk.Button(
            file_frame,
            text="Browse",
            command=self.browse_file,
        )
        self.upload_btn.grid(row=0, column=1)

        # Progress bar
        self.progress_label = ttk.Label(main_frame, text="")
        self.progress_label.grid(row=5, column=0, columnspan=2, pady=(20, 5))

        self.progress_bar = ttk.Progressbar(main_frame, mode="determinate")
        self.progress_bar.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky=(tk.W, tk.E),
            pady=5,
        )

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(20, 0))

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        file_frame.columnconfigure(0, weight=1)

    def browse_file(self) -> None:
        """Open file dialog to select media file."""
        file_types = [
            ("Media files", "*.mp4 *.avi *.mov *.mkv *.mp3 *.wav *.ogg"),
            ("All files", "*.*"),
        ]

        filename = filedialog.askopenfilename(
            title="Select media File",
            filetypes=file_types,
        )

        if filename:
            self.selected_file = Path(filename)
            self.file_label.config(text=self.selected_file.name, foreground="black")
            self.output_file = None
            self.start_conversion()

    def start_conversion(self) -> None:
        """Start the conversion process in a separate thread."""
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a media file first.")
            return

        # Disable buttons during conversion
        self.upload_btn.config(state="disabled")

        # Start progress bar
        self.progress_label.config(text="Converting media to text...")

        # Run conversion in separate thread to prevent GUI freezing
        thread = Thread(target=self.convert_media)
        thread.daemon = True
        thread.start()

    def convert_media(self) -> None:
        """Convert media to text."""
        try:
            # Load the media file. Extract/convert the audio
            self.progress_bar.step(30)
            self.root.after(
                0,
                lambda: self.progress_label.config(text="Extracting audio..."),
            )
            file = AudioFileClip(str(self.selected_file))
            wav_filename = self.selected_file.parent / f"{self.selected_file.stem}.wav"
            file.write_audiofile(str(wav_filename))
            file.close()

            # Initialize recognizer
            self.progress_bar.step(30)
            self.root.after(
                0,
                lambda: self.progress_label.config(text="Converting speech to text..."),
            )
            r = Recognizer()
            with AudioFile(str(wav_filename)) as source:
                data = r.record(source)
                text = r.recognize_vosk(data)

            # Save text to file
            self.progress_bar.step(30)
            self.output_file = (
                self.selected_file.parent / f"{self.selected_file.stem}.txt"
            )
            with self.output_file.open("w", encoding="utf-8") as f:
                f.write(text)

            # Update UI on completion
            if wav_filename.exists():
                wav_filename.unlink()
            self.root.after(0, self.conversion_completed)

        except Exception as e:  # noqa: BLE001
            # Handle errors - capture the error message first
            error_message = str(e)
            self.root.after(0, lambda msg=error_message: self.conversion_failed(msg))

    def conversion_completed(self) -> None:
        """Handle successful conversion completion."""
        self.progress_bar.stop()
        self.progress_label.config(text="Conversion completed successfully!")

        # Re-enable button
        self.upload_btn.config(state="normal")

        messagebox.showinfo("Success", f"Text file saved as:\n{self.output_file.name}")
        self.open_folder()
        self.root.after(
            3000,
            lambda: self.progress_label.config(text=""),
        )
        self.file_label.config(text="No file selected", foreground="gray")


    def conversion_failed(self, error_message: str) -> None:
        """Handle conversion failure."""
        self.progress_bar.stop()
        self.progress_label.config(text="Conversion failed!")

        # Re-enable button
        self.upload_btn.config(state="normal")
        self.file_label.config(text="No file selected", foreground="gray")

        messagebox.showerror("Error", f"Conversion failed:\n{error_message}")
        self.root.after(
            3000,
            lambda: self.progress_label.config(text=""),
        )
        self.file_label.config(text="No file selected", foreground="gray")

    def open_folder(self) -> None:
        """Open the folder containing the generated text file."""
        if self.output_file and self.output_file.exists():
            try:
                # Get the parent directory of the output file
                folder_path = self.output_file.parent

                # Try to open folder with default system application
                if os.name == "nt":  # Windows
                    os.startfile(folder_path)  # noqa: S606
                elif os.name == "darwin":  # macOS
                    os.system(f'open "{folder_path}"')  # noqa: S605
                elif os.name == "posix":  # Linux
                    os.system(f'xdg-open "{folder_path}"')  # noqa: S605
            except OSError as e:
                messagebox.showerror("Error", f"Could not open folder:\n{e}")
        else:
            messagebox.showwarning("Warning", "No text file available to open.")


def main() -> None:
    """Run the application."""
    root = tk.Tk()
    VideoToTextConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
