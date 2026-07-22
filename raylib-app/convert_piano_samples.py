import os
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

# Get all MP3 files in the piano audio directory
files = [f for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3")]

for filename in files:
    mp3_path = os.path.join(AUDIO_DIR, filename)
    wav_name = filename.replace(".mp3", ".wav")
    wav_path = os.path.join(AUDIO_DIR, wav_name)
    
    print(f"Decoding {filename}...")
    decoded = miniaudio.decode_file(mp3_path)
    
    samples_array = array.array('h', decoded.samples)
    num_channels = decoded.nchannels
    
    # Apply fade out to the last 50ms of audio (piano notes are long, 50ms is very smooth)
    fade_frames = int(0.05 * decoded.sample_rate) # 50ms
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
                
    print(f"Saving to {wav_name}...")
    with wave.open(wav_path, "wb") as wav_file:
        wav_file.setnchannels(decoded.nchannels)
        wav_file.setsampwidth(decoded.sample_width)
        wav_file.setframerate(decoded.sample_rate)
        wav_file.writeframes(samples_array.tobytes())
        
print("All piano samples converted successfully!")
