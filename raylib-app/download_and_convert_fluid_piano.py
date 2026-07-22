import os
import urllib.request
import subprocess
import sys
import wave
import array

# Ensure miniaudio is installed
try:
    import miniaudio  # type: ignore
except ImportError:
    print("Installing miniaudio...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "miniaudio"])
    import miniaudio  # type: ignore

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(SCRIPT_DIR, "..", "public", "audio", "piano")

# Ensure target directory exists
os.makedirs(AUDIO_DIR, exist_ok=True)

# 36 piano keys from C3 to B5
PIANO_KEYS = [
    "C3", "C#3", "D3", "D#3", "E3", "F3", "F#3", "G3", "G#3", "A3", "A#3", "B3",
    "C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
    "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5"
]

# Map sharp notes to flat names as stored in the repository
NOTE_FLAT_MAP = {
    "C": "C", "C#": "Db", "D": "D", "D#": "Eb", "E": "E",
    "F": "F", "F#": "Gb", "G": "G", "G#": "Ab", "A": "A",
    "A#": "Bb", "B": "B"
}

BASE_URL = "https://raw.githubusercontent.com/fuhton/piano-mp3/master/piano-mp3/"

def get_download_filename(note):
    # E.g. "C#3" -> "Db3"
    name = note[:-1]
    octave = note[-1]
    flat_name = NOTE_FLAT_MAP[name]
    return f"{flat_name}{octave}.mp3"

for note in PIANO_KEYS:
    remote_filename = get_download_filename(note)
    local_wav_name = note.replace("#", "s") + ".wav"
    local_wav_path = os.path.join(AUDIO_DIR, local_wav_name)
    
    # Download URL
    download_url = BASE_URL + remote_filename
    temp_mp3_path = os.path.join(AUDIO_DIR, remote_filename)
    
    print(f"Downloading {note} ({remote_filename}) from {download_url}...")
    try:
        urllib.request.urlretrieve(download_url, temp_mp3_path)
    except Exception as e:
        print(f"Failed to download {note}: {e}")
        continue
        
    print(f"Decoding {remote_filename}...")
    try:
        decoded = miniaudio.decode_file(temp_mp3_path)
        samples_array = array.array('h', decoded.samples)
        num_channels = decoded.nchannels
        
        # Apply 50ms fade-out at the end of each note
        fade_frames = int(0.05 * decoded.sample_rate)
        fade_samples = fade_frames * num_channels
        
        total_samples = len(samples_array)
        if total_samples > fade_samples:
            for i in range(fade_frames):
                factor = 1.0 - (i / fade_frames)
                sample_idx_left = total_samples - fade_samples + (i * num_channels)
                samples_array[sample_idx_left] = int(samples_array[sample_idx_left] * factor)
                if num_channels > 1:
                    sample_idx_right = sample_idx_left + 1
                    samples_array[sample_idx_right] = int(samples_array[sample_idx_right] * factor)
                    
        # Write to WAV
        print(f"Saving to {local_wav_name}...")
        with wave.open(local_wav_path, "wb") as wav_file:
            wav_file.setnchannels(decoded.nchannels)
            wav_file.setsampwidth(decoded.sample_width)
            wav_file.setframerate(decoded.sample_rate)
            wav_file.writeframes(samples_array.tobytes())
            
    except Exception as e:
        print(f"Failed to decode or convert {remote_filename}: {e}")
    finally:
        # Delete temp MP3
        if os.path.exists(temp_mp3_path):
            os.remove(temp_mp3_path)

print("All 36 piano samples downloaded and converted to high-quality WAV files!")
