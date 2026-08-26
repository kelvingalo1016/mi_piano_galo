import os
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(SCRIPT_DIR, "..", "public", "audio", "piano")
DIST_DIR = os.path.join(SCRIPT_DIR, "..", "dist", "audio", "piano")

# 1. Delete all WAV files in public/audio/piano
for file in os.listdir(PUBLIC_DIR):
    if file.endswith(".wav"):
        os.remove(os.path.join(PUBLIC_DIR, file))
        print(f"Deleted {file}")

# 2. Copy all MP3 files from dist/audio/piano to public/audio/piano
for file in os.listdir(DIST_DIR):
    if file.endswith(".mp3"):
        shutil.copy(os.path.join(DIST_DIR, file), os.path.join(PUBLIC_DIR, file))
        print(f"Restored {file}")

print("Original MP3 files restored successfully!")
