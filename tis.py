from pathlib import Path

from moviepy import VideoFileClip
from speech_recognition import AudioFile, Recognizer

filename = Path("DWAwxJAbzUyQIDR9PkSKJll3Y6TREVYC.mp4")

# Load the video
video = VideoFileClip(filename)

# Extract the audio from the video
audio_file = video.audio
audio_file.write_audiofile(filename.stem + ".wav")

# Initialize recognizer
r = Recognizer()

# Load the audio file
with AudioFile(filename.stem + ".wav") as source:
    data = r.record(source)

# Convert speech to text
text = r.recognize_vosk(data, language="ru")

# Print the text
with Path.open(filename.stem + ".txt", "w+", encoding="utf-8") as f:
    f.writelines(text)
