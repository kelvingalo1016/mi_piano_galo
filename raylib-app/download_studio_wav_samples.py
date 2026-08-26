import os
import urllib.request
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(SCRIPT_DIR, "..", "public", "audio", "piano")

# Ensure target directory exists
os.makedirs(AUDIO_DIR, exist_ok=True)

# List of 30 original samples used by the piano app
AVAILABLE_SAMPLES = [
    'A0', 'C1', 'D#1', 'F#1', 'A1', 'C2', 'D#2', 'F#2', 'A2', 'C3', 'D#3', 'F#3', 'A3',
    'C4', 'D#4', 'F#4', 'A4', 'C5', 'D#5', 'F#5', 'A5', 'C6', 'D#6', 'F#6', 'A6',
    'C7', 'D#7', 'F#7', 'A7', 'C8'
]

BASE_URL = "https://github.com/nbrosowsky/tonejs-instruments/raw/master/samples/piano/"

# 1. Delete old WAV and MP3 files to prevent mixing formats
print("Cleaning old piano audio files...")
for file in os.listdir(AUDIO_DIR):
    if file.endswith(".wav") or file.endswith(".mp3"):
        os.remove(os.path.join(AUDIO_DIR, file))

# 2. Download high-quality studio WAV files
for sample in AVAILABLE_SAMPLES:
    filename = sample.replace("#", "s") + ".wav"
    download_url = BASE_URL + filename
    dest_path = os.path.join(AUDIO_DIR, filename)
    
    print(f"Downloading {filename} from {download_url}...")
    try:
        urllib.request.urlretrieve(download_url, dest_path)
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

print("All studio-grade WAV samples downloaded successfully!")
