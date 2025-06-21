# Media-in-Speech

A Python GUI application that converts media files to text using speech recognition technology.

## Features

- **Easy-to-use GUI** - Simple tkinter-based interface
- **Multiple media formats** - Supports MP4, AVI, MOV, MKV, MP3, WAV, OGG.
- **Real-time progress tracking** - Visual progress bar with status updates
- **Automatic file management** - Saves text files in the same directory as source video
- **Cross-platform compatibility** - Works on Windows, macOS, and Linux

## Screenshots

![Application Interface](screenshot.png)

## Requirements

- Python 3.12+
- tkinter (usually included with Python)
- moviepy
- SpeechRecognition
- vosk (for offline speech recognition)

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/waldesem/Video-in-Speech.git
cd Video-in-Speech
```

2. **Install required dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install Vosk models (for offline recognition):**
```bash
# For Russian
wget https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip
unzip vosk-model-ru-0.42.zip
mv vosk-model-ru-0.42 model

## Usage

### GUI Application

1. **Run the application:**
```bash
python tis.py
```

2. **Convert video to text:**
   - Click "Browse" to select a video file
   - Click "Convert to Text"
   - Wait for the conversion to complete
   - Click "Open Folder" to view the generated text file

## How It Works

1. **Audio Extraction** - Uses MoviePy to extract audio from media files
2. **Audio Processing** - Converts audio to WAV format for speech recognition
3. **Speech Recognition** - Uses Vosk for offline speech-to-text conversion
4. **Text Output** - Saves the transcribed text to a .txt file
5. **Cleanup** - Removes temporary audio files

## Supported Formats

### Input Media Formats
- MP4
- AVI
- MOV
- MKV
- MP3
- WAV
- OGG

### Output
- Plain text (.txt) files with UTF-8 encoding

## Configuration

### File Locations
- Output text files are saved in the same directory as the input video
- Temporary WAV files are automatically cleaned up after processing

### Building Executable
You can create a standalone executable using PyInstaller that includes all dependencies and models.
```bash
pyinstaller --windowed --add-data="model:model" tis.py
```

## Troubleshooting

### Performance Tips

- **Large files**: For videos longer than 30 minutes, consider splitting them into smaller chunks
- **Audio quality**: Better audio quality results in more accurate transcription
- **Background noise**: Minimize background noise for better recognition accuracy

## License

This project is licensed under the MIT License.
