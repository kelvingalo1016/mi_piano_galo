import os
import subprocess
import sys

# Ensure miniaudio is installed
try:
    import miniaudio
except ImportError:
    print("Installing miniaudio...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "miniaudio"])
    import miniaudio

import wave
import array

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SONIDOS_DIR = os.path.join(SCRIPT_DIR, "sonidos")

files = [
    "click_select_option_sound.mp3",
    "seleccion_opcion_sonido.mp3"
]

for filename in files:
    mp3_path = os.path.join(SONIDOS_DIR, filename)
    wav_name = filename.replace(".mp3", ".wav")
    wav_path = os.path.join(SONIDOS_DIR, wav_name)
    
    if not os.path.exists(mp3_path):
        print(f"Skipping {filename}, not found.")
        continue
        
    print(f"Decoding {filename}...")
    # Decode to default format: signed 16-bit, 2 channels, 44100 Hz
    decoded = miniaudio.decode_file(mp3_path)
    
    # Cast samples to a modifiable array of signed 16-bit integers (short)
    samples_array = array.array('h', decoded.samples)
    
    # Apply fade out to the last 20ms of audio
    # 20ms at 44100 Hz = 882 frames.
    # Since it is stereo (2 channels), there are 882 * 2 = 1764 samples.
    num_channels = decoded.nchannels
    fade_frames = int(0.02 * decoded.sample_rate) # 20ms
    fade_samples = fade_frames * num_channels
    
    total_samples = len(samples_array)
    if total_samples > fade_samples:
        for i in range(fade_frames):
            # i goes from 0 to fade_frames - 1
            # factor goes from 1.0 down to 0.0
            factor = 1.0 - (i / fade_frames)
            
            # Index of samples from the end
            sample_idx_left = total_samples - fade_samples + (i * num_channels)
            sample_idx_right = sample_idx_left + 1
            
            samples_array[sample_idx_left] = int(samples_array[sample_idx_left] * factor)
            if num_channels > 1:
                samples_array[sample_idx_right] = int(samples_array[sample_idx_right] * factor)
                
    # Write to WAV
    print(f"Saving to {wav_name}...")
    with wave.open(wav_path, "wb") as wav_file:
        wav_file.setnchannels(decoded.nchannels)
        wav_file.setsampwidth(decoded.sample_width)
        wav_file.setframerate(decoded.sample_rate)
        wav_file.writeframes(samples_array.tobytes())
        
    print("Done!")
