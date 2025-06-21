"""Video to text converter with GUI."""

import os
import tkinter as tk
from pathlib import Path
from threading import Thread
from tkinter import filedialog, messagebox, ttk

from moviepy import AudioFileClip, VideoFileClip
from speech_recognition import AudioFile, Recognizer


class VideoToTextConverter:
    """GUI for video to text conversion."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialize the GUI."""
        self.root = root
        self.root.title("Video to Text Converter")
        self.root.geometry("540x300")
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
            main_frame, text="Video to Text Converter", font=("Arial", 16, "bold"),
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # File selection
        ttk.Label(main_frame, text="Select video file:").grid(
            row=1, column=0, sticky=tk.W, pady=5,
        )

        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.file_label = ttk.Label(
            file_frame, text="No file selected", foreground="gray", width=50,
        )
        self.file_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        self.upload_btn = ttk.Button(
            file_frame, text="Browse", command=self.browse_file,
        )
        self.upload_btn.grid(row=0, column=1)

        # Progress bar
        self.progress_label = ttk.Label(main_frame, text="")
        self.progress_label.grid(row=5, column=0, columnspan=2, pady=(20, 5))

        self.progress_bar = ttk.Progressbar(main_frame, mode="determinate")
        self.progress_bar.grid(
            row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5,
        )

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(20, 0))

        self.convert_btn = ttk.Button(
            button_frame,
            text="Convert to Text",
            command=self.start_conversion,
            state="disabled",
        )
        self.convert_btn.grid(row=0, column=0, padx=(0, 10))

        self.open_btn = ttk.Button(
            button_frame,
            text="Open Folder",
            command=self.open_text_file,
            state="disabled",
        )
        self.open_btn.grid(row=0, column=1)

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        file_frame.columnconfigure(0, weight=1)

    def browse_file(self) -> None:
        """Open file dialog to select video file."""
        file_types = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv"),
            # ("Audio files", "*.mp3 *.wav *.ogg"),
        ]

        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=file_types,
        )

        if filename:
            self.selected_file = Path(filename)
            self.file_label.config(text=self.selected_file.name, foreground="black")
            self.convert_btn.config(state="normal")
            self.open_btn.config(state="disabled")
            self.output_file = None

    def start_conversion(self) -> None:
        """Start the conversion process in a separate thread."""
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a video file first.")
            return

        # Disable buttons during conversion
        self.convert_btn.config(state="disabled")
        self.upload_btn.config(state="disabled")

        # Start progress bar
        self.progress_label.config(text="Converting video to text...")

        # Run conversion in separate thread to prevent GUI freezing
        thread = Thread(target=self.convert_video)
        thread.daemon = True
        thread.start()

    def convert_video(self) -> None:
        """Convert video to text."""
        try:
            # Update progress
            self.progress_bar.step(10)
            self.root.after(
                0, lambda: self.progress_label.config(text="Extracting audio..."),
            )

            # Load the video
            self.progress_bar.step(10)
            if self.selected_file.suffix.lower() in (".mp4", ".avi", ".mov", ".mkv"):
                video = VideoFileClip(str(self.selected_file))
                audio_file = video.audio
            elif self.selected_file.suffix.lower() in (".mp3", ".wav", ".ogg"):
                audio_file = AudioFileClip(str(self.selected_file))

            # Extract the audio from the video
            self.progress_bar.step(10)
            wav_filename = self.selected_file.parent / f"{self.selected_file.stem}.wav"
            audio_file.write_audiofile(str(wav_filename), logger=None)

            # Clean up video object
            self.progress_bar.step(10)
            if self.selected_file.suffix.lower() in (".mp4", ".avi", ".mov", ".mkv"):
                video.close()
            else:
                audio_file.close()

            # Update progress
            self.progress_bar.step(10)
            self.root.after(
                0,
                lambda: self.progress_label.config(text="Converting speech to text..."),
            )

            # Initialize recognizer
            self.progress_bar.step(10)
            r = Recognizer()

            # Load the audio file
            self.progress_bar.step(10)
            with AudioFile(str(wav_filename)) as source:
                data = r.record(source)

            # Convert speech to text
            self.progress_bar.step(10)
            text = r.recognize_vosk(data, language="ru")

            # Save text to file
            self.progress_bar.step(10)
            self.output_file = (
                self.selected_file.parent / f"{self.selected_file.stem}.txt"
            )
            with self.output_file.open("w", encoding="utf-8") as f:
                f.write(text)

            # Clean up temporary WAV file
            self.progress_bar.step(10)
            if wav_filename.exists():
                Path.unlink(wav_filename)

            # Update UI on completion
            self.root.after(0, self.conversion_completed)

        except Exception as e:  # noqa: BLE001
            # Handle errors - capture the error message first
            error_message = str(e)
            self.root.after(0, lambda msg=error_message: self.conversion_failed(msg))

    def conversion_completed(self) -> None:
        """Handle successful conversion completion."""
        self.progress_bar.stop()
        self.progress_label.config(text="Conversion completed successfully!")

        # Re-enable buttons
        self.convert_btn.config(state="normal")
        self.upload_btn.config(state="normal")
        self.open_btn.config(state="normal")

        messagebox.showinfo("Success", f"Text file saved as:\n{self.output_file.name}")

    def conversion_failed(self, error_message: str) -> None:
        """Handle conversion failure."""
        self.progress_bar.stop()
        self.progress_label.config(text="Conversion failed!")

        # Re-enable buttons
        self.convert_btn.config(state="normal")
        self.upload_btn.config(state="normal")

        messagebox.showerror("Error", f"Conversion failed:\n{error_message}")

    def open_text_file(self) -> None:
        """Open the folder containing the generated text file."""
        if self.output_file and self.output_file.exists():
            try:
                # Get the parent directory of the output file
                folder_path = self.output_file.parent

                # Try to open folder with default system application
                if os.name == "nt":  # Windows
                    os.startfile(folder_path)
                elif os.name == "posix":  # Linux
                    os.system(f'xdg-open "{folder_path}"')
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
