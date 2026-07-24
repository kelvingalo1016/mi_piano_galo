import os
import sys
import subprocess
import zipfile
import math
import urllib.request

def setup_fluidsynth():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bin_dir = os.path.join(script_dir, "bin")
    fluid_dir = os.path.join(bin_dir, "fluidsynth")
    sf2_path = os.path.join(script_dir, "TimGM6mb.sf2")
    
    os.makedirs(bin_dir, exist_ok=True)
    
    # 1. Download SoundFont if not present
    if not os.path.exists(sf2_path):
        print("Downloading TimGM6mb.sf2 SoundFont...")
        sf2_url = "https://github.com/craffel/pretty-midi/raw/main/pretty_midi/TimGM6mb.sf2"
        try:
            urllib.request.urlretrieve(sf2_url, sf2_path)
            print("SoundFont downloaded successfully.")
        except Exception as e:
            print(f"Failed to download SoundFont: {e}")
            
    # 2. Download FluidSynth binaries if on Windows and not present
    if sys.platform == 'win32' and not os.path.exists(fluid_dir):
        print("Downloading FluidSynth Windows x64 binaries...")
        fluid_url = "https://github.com/FluidSynth/fluidsynth/releases/download/v2.5.6/fluidsynth-v2.5.6-win10-x64-glib.zip"
        zip_path = os.path.join(bin_dir, "fluidsynth.zip")
        try:
            urllib.request.urlretrieve(fluid_url, zip_path)
            print("FluidSynth zip downloaded. Extracting...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(fluid_dir)
            print("Extraction completed.")
            os.remove(zip_path)
        except Exception as e:
            print(f"Failed to download or extract FluidSynth: {e}")
            
    # 3. Add DLL directory to search path on Windows
    if sys.platform == 'win32':
        dll_path = None
        for root, dirs, files in os.walk(fluid_dir):
            if "libfluidsynth-3.dll" in files:
                dll_path = root
                break
        if dll_path:
            os.environ["PATH"] = dll_path + os.pathsep + os.environ["PATH"]
            if hasattr(os, "add_dll_directory"):
                os.add_dll_directory(dll_path)
                
    # 4. Ensure pyfluidsynth is installed
    try:
        import fluidsynth
    except ImportError:
        print("Installing pyfluidsynth...")
        installed = False
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyfluidsynth"])
            installed = True
        except Exception as e:
            print(f"Failed to install pyfluidsynth via pip: {e}")
            if sys.platform.startswith('linux'):
                print("Trying to install using --break-system-packages on Linux...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyfluidsynth", "--break-system-packages"])
                    installed = True
                except Exception as e2:
                    print(f"Failed to install pyfluidsynth with --break-system-packages: {e2}")
        if installed:
            try:
                import site
                from importlib import reload
                reload(site)
                print("Refreshed Python site paths successfully.")
            except Exception as reload_err:
                print(f"Failed to refresh site paths: {reload_err}")
                
    # 5. Ensure raylib is installed (provides pyray)
    try:
        import pyray
    except ImportError:
        print("Installing raylib...")
        installed = False
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "raylib"])
            installed = True
        except Exception as e:
            print(f"Failed to install raylib via pip: {e}")
            if sys.platform.startswith('linux'):
                print("Trying to install raylib using --break-system-packages on Linux...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "raylib", "--break-system-packages"])
                    installed = True
                except Exception as e2:
                    print(f"Failed to install raylib with --break-system-packages: {e2}")
        if installed:
            try:
                import site
                from importlib import reload
                reload(site)
                print("Refreshed Python site paths successfully for raylib.")
            except Exception as reload_err:
                print(f"Failed to refresh site paths: {reload_err}")

# Run setup
setup_fluidsynth()
import fluidsynth
import pyray as pr


# Initialize Raylib Window
pr.set_config_flags(pr.FLAG_WINDOW_RESIZABLE | pr.FLAG_VSYNC_HINT)
pr.init_window(1024, 600, "GPiano")
pr.toggle_fullscreen()
pr.hide_cursor()
pr.set_target_fps(60)

# Initialize Audio
pr.init_audio_device()

# Resolve paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(SCRIPT_DIR, "..", "public", "audio", "piano")
FONT_PATH = os.path.join(SCRIPT_DIR, "Inter-Bold", "Inter (TTF)", "Inter-Bold.ttf")
CLICK_SOUND_PATH = os.path.join(SCRIPT_DIR, "sonidos", "click_select_option_sound.wav")
SELECT_SOUND_PATH = os.path.join(SCRIPT_DIR, "sonidos", "seleccion_opcion_sonido.wav")

# Load Menu Audio Effects
click_sound = None
select_sound = None

if os.path.exists(CLICK_SOUND_PATH):
    try:
        click_sound = pr.load_sound(CLICK_SOUND_PATH)
        print("Loaded click navigation sound successfully.")
    except Exception as e:
        print("Failed to load click navigation sound:", e)

if os.path.exists(SELECT_SOUND_PATH):
    try:
        select_sound = pr.load_sound(SELECT_SOUND_PATH)
        print("Loaded selection sound successfully.")
    except Exception as e:
        print("Failed to load selection sound:", e)


# Modern Font Downloader and Loader
custom_font = None

def init_font():
    global custom_font
    if os.path.exists(FONT_PATH):
        try:
            # Load font with custom Spanish accent codepoints using CFFI pointer
            codepoints_list = list(range(32, 128)) + [225, 233, 237, 243, 250, 241, 193, 201, 205, 211, 218, 209, 191, 161]
            raw_arr = pr.ffi.new('int[]', codepoints_list)
            custom_font = pr.load_font_ex(FONT_PATH, 64, pr.ffi.cast('int *', raw_arr), len(codepoints_list))
            pr.set_texture_filter(custom_font.texture, pr.TEXTURE_FILTER_BILINEAR)
            print("Loaded TTF font with accents successfully.")
        except Exception as e:
            print("Failed to load TTF font:", e)
    else:
        print(f"Font file not found at {FONT_PATH}")

# Trigger font initialization
init_font()

# Load Logo Texture
logo_path = os.path.join(SCRIPT_DIR, "logo.png")
logo_texture = None
if os.path.exists(logo_path):
    try:
        logo_texture = pr.load_texture(logo_path)
        print("Loaded logo texture successfully.")
    except Exception as e:
        print("Failed to load logo texture:", e)

# Load Menu Textures (PNG icons)
nota_path = os.path.join(SCRIPT_DIR, "iconos", "nota.png")
flecha_izq_path = os.path.join(SCRIPT_DIR, "iconos", "flecha_izquierda.png")
flecha_der_path = os.path.join(SCRIPT_DIR, "iconos", "flecha_derecha.png")

nota_texture = None
flecha_izq_texture = None
flecha_der_texture = None

if os.path.exists(nota_path):
    try:
        nota_texture = pr.load_texture(nota_path)
        print("Loaded nota texture successfully.")
    except Exception as e:
        print("Failed to load nota texture:", e)

if os.path.exists(flecha_izq_path):
    try:
        flecha_izq_texture = pr.load_texture(flecha_izq_path)
        print("Loaded flecha_izquierda texture successfully.")
    except Exception as e:
        print("Failed to load flecha_izquierda texture:", e)

if os.path.exists(flecha_der_path):
    try:
        flecha_der_texture = pr.load_texture(flecha_der_path)
        print("Loaded flecha_derecha texture successfully.")
    except Exception as e:
        print("Failed to load flecha_derecha texture:", e)

# Load Countdown Number Textures
num1_path = os.path.join(SCRIPT_DIR, "iconos", "1.png")
num2_path = os.path.join(SCRIPT_DIR, "iconos", "2.png")
num3_path = os.path.join(SCRIPT_DIR, "iconos", "3.png")

num1_texture = None
num2_texture = None
num3_texture = None

if os.path.exists(num1_path):
    try:
        num1_texture = pr.load_texture(num1_path)
        print("Loaded texture 1 successfully.")
    except Exception as e:
        print("Failed to load texture 1:", e)

if os.path.exists(num2_path):
    try:
        num2_texture = pr.load_texture(num2_path)
        print("Loaded texture 2 successfully.")
    except Exception as e:
        print("Failed to load texture 2:", e)

if os.path.exists(num3_path):
    try:
        num3_texture = pr.load_texture(num3_path)
        print("Loaded texture 3 successfully.")
    except Exception as e:
        print("Failed to load texture 3:", e)

# Modern Text Wrappers for Premium Typography
def draw_text_modern(text, x, y, size, color):
    if custom_font:
        pr.draw_text_ex(custom_font, text, pr.Vector2(x, y), size, 0.0, color)
    else:
        pr.draw_text(text, int(x), int(y), int(size), color)

def measure_text_modern_width(text, size):
    if custom_font:
        size_vec = pr.measure_text_ex(custom_font, text, size, 0.0)
        return int(size_vec.x)
    else:
        return pr.measure_text(text, int(size))

# Available samples and their notes
AVAILABLE_SAMPLES = [
    'A0', 'C1', 'D#1', 'F#1', 'A1', 'C2', 'D#2', 'F#2', 'A2', 'C3', 'D#3', 'F#3', 'A3',
    'C4', 'D#4', 'F#4', 'A4', 'C5', 'D#5', 'F#5', 'A5', 'C6', 'D#6', 'F#6', 'A6',
    'C7', 'D#7', 'F#7', 'A7', 'C8'
]

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def note_to_midi(note_str):
    note_str = note_str.replace("Db", "C#").replace("Eb", "D#").replace("Gb", "F#").replace("Ab", "G#").replace("Bb", "A#")
    name = note_str[:-1]
    octave = int(note_str[-1])
    return 12 * (octave + 1) + NOTE_NAMES.index(name)

sample_midis = {note: note_to_midi(note) for note in AVAILABLE_SAMPLES}

def get_closest_sample(target_note):
    target_midi = note_to_midi(target_note)
    closest_note = None
    min_diff = 999
    
    for sample, midi in sample_midis.items():
        diff = abs(target_midi - midi)
        if diff < min_diff:
            min_diff = diff
            closest_note = sample
            
    return closest_note, target_midi - sample_midis[closest_note]

# Piano Keys Definition (C3 to B5)
PIANO_KEYS = [
    # Octave 3
    {"note": "C3", "key": "a", "is_black": False},
    {"note": "C#3", "key": "b", "is_black": True},
    {"note": "D3", "key": "c", "is_black": False},
    {"note": "D#3", "key": "d", "is_black": True},
    {"note": "E3", "key": "e", "is_black": False},
    {"note": "F3", "key": "f", "is_black": False},
    {"note": "F#3", "key": "g", "is_black": True},
    {"note": "G3", "key": "h", "is_black": False},
    {"note": "G#3", "key": "i", "is_black": True},
    {"note": "A3", "key": "j", "is_black": False},
    {"note": "A#3", "key": "k", "is_black": True},
    {"note": "B3", "key": "l", "is_black": False},

    # Octave 4
    {"note": "C4", "key": "m", "is_black": False},
    {"note": "C#4", "key": "n", "is_black": True},
    {"note": "D4", "key": "o", "is_black": False},
    {"note": "D#4", "key": "p", "is_black": True},
    {"note": "E4", "key": "q", "is_black": False},
    {"note": "F4", "key": "r", "is_black": False},
    {"note": "F#4", "key": "s", "is_black": True},
    {"note": "G4", "key": "t", "is_black": False},
    {"note": "G#4", "key": "u", "is_black": True},
    {"note": "A4", "key": "v", "is_black": False},
    {"note": "A#4", "key": "w", "is_black": True},
    {"note": "B4", "key": "x", "is_black": False},

    # Octave 5
    {"note": "C5", "key": "y", "is_black": False},
    {"note": "C#5", "key": "z", "is_black": True},
    {"note": "D5", "key": "1", "is_black": False},
    {"note": "D#5", "key": "2", "is_black": True},
    {"note": "E5", "key": "3", "is_black": False},
    {"note": "F5", "key": "4", "is_black": False},
    {"note": "F#5", "key": "5", "is_black": True},
    {"note": "G5", "key": "6", "is_black": False},
    {"note": "G#5", "key": "7", "is_black": True},
    {"note": "A5", "key": "8", "is_black": False},
    {"note": "A#5", "key": "9", "is_black": True},
    {"note": "B5", "key": "0", "is_black": False},
]

# Separate white and black keys list
white_keys = []
black_keys = []

for key in PIANO_KEYS:
    if not key["is_black"]:
        white_keys.append(key)
    else:
        preceding_white_index = len(white_keys) - 1
        if preceding_white_index >= 0:
            black_keys.append({**key, "white_index": preceding_white_index})

# Key to note QWERTY maps
KEY_MAP_RAYLIB = {
    "a": pr.KEY_A, "b": pr.KEY_B, "c": pr.KEY_C, "d": pr.KEY_D, "e": pr.KEY_E,
    "f": pr.KEY_F, "g": pr.KEY_G, "h": pr.KEY_H, "i": pr.KEY_I, "j": pr.KEY_J,
    "k": pr.KEY_K, "l": pr.KEY_L, "m": pr.KEY_M, "n": pr.KEY_N, "o": pr.KEY_O,
    "p": pr.KEY_P, "q": pr.KEY_Q, "r": pr.KEY_R, "s": pr.KEY_S, "t": pr.KEY_T,
    "u": pr.KEY_U, "v": pr.KEY_V, "w": pr.KEY_W, "x": pr.KEY_X, "y": pr.KEY_Y,
    "z": pr.KEY_Z, "1": pr.KEY_ONE, "2": pr.KEY_TWO, "3": pr.KEY_THREE,
    "4": pr.KEY_FOUR, "5": pr.KEY_FIVE, "6": pr.KEY_SIX, "7": pr.KEY_SEVEN,
    "8": pr.KEY_EIGHT, "9": pr.KEY_NINE, "0": pr.KEY_ZERO
}

# FluidSynth global instance
fs_synth = None
sf_id = -1
loading_progress = 0

def load_samples_tick():
    global loading_progress, fs_synth, sf_id
    if loading_progress >= 1:
        return True
        
    print("Initializing FluidSynth...")
    try:
        fs_synth = fluidsynth.Synth()
        if sys.platform.startswith('linux'):
            drivers = ['pulseaudio', 'alsa', 'pipewire', 'jack']
            success = False
            for driver in drivers:
                try:
                    print(f"Trying FluidSynth driver: {driver}...")
                    fs_synth.start(driver=driver)
                    success = True
                    print(f"FluidSynth started successfully with driver: {driver}")
                    break
                except Exception as driver_err:
                    print(f"Failed to start with driver {driver}: {driver_err}")
            if not success:
                print("Failed to start FluidSynth with specific drivers, trying default start...")
                fs_synth.start()
        else:
            fs_synth.start()
        
        sf2_path = os.path.join(SCRIPT_DIR, "TimGM6mb.sf2")
        print(f"Loading SoundFont: {sf2_path}")
        sf_id = fs_synth.sfload(sf2_path)
        if sf_id != -1:
            fs_synth.program_select(0, sf_id, 0, 0)
            print("FluidSynth initialized and SoundFont loaded successfully.")
        else:
            print("Failed to load SoundFont.")
    except Exception as e:
        print(f"Failed to initialize FluidSynth: {e}")
        
    loading_progress = len(PIANO_KEYS)
    return True

# Song definitions
SONGS = [
    {
        "id": "twinkle",
        "title": "Estrellita Dónde Estás",
        "composer": "Tradicional",
        "notes": [
            {"note": "C4", "time": 0.0, "duration": 0.4},
            {"note": "C4", "time": 0.5, "duration": 0.4},
            {"note": "G4", "time": 1.0, "duration": 0.4},
            {"note": "G4", "time": 1.5, "duration": 0.4},
            {"note": "A4", "time": 2.0, "duration": 0.4},
            {"note": "A4", "time": 2.5, "duration": 0.4},
            {"note": "G4", "time": 3.0, "duration": 0.8},
            {"note": "F4", "time": 4.0, "duration": 0.4},
            {"note": "F4", "time": 4.5, "duration": 0.4},
            {"note": "E4", "time": 5.0, "duration": 0.4},
            {"note": "E4", "time": 5.5, "duration": 0.4},
            {"note": "D4", "time": 6.0, "duration": 0.4},
            {"note": "D4", "time": 6.5, "duration": 0.4},
            {"note": "C4", "time": 7.0, "duration": 0.8},
            {"note": "G4", "time": 8.0, "duration": 0.4},
            {"note": "G4", "time": 8.5, "duration": 0.4},
            {"note": "F4", "time": 9.0, "duration": 0.4},
            {"note": "F4", "time": 9.5, "duration": 0.4},
            {"note": "E4", "time": 10.0, "duration": 0.4},
            {"note": "E4", "time": 10.5, "duration": 0.4},
            {"note": "D4", "time": 11.0, "duration": 0.8},
            {"note": "G4", "time": 12.0, "duration": 0.4},
            {"note": "G4", "time": 12.5, "duration": 0.4},
            {"note": "F4", "time": 13.0, "duration": 0.4},
            {"note": "F4", "time": 13.5, "duration": 0.4},
            {"note": "E4", "time": 14.0, "duration": 0.4},
            {"note": "E4", "time": 14.5, "duration": 0.4},
            {"note": "D4", "time": 15.0, "duration": 0.8},
            {"note": "C4", "time": 16.0, "duration": 0.4},
            {"note": "C4", "time": 16.5, "duration": 0.4},
            {"note": "G4", "time": 17.0, "duration": 0.4},
            {"note": "G4", "time": 17.5, "duration": 0.4},
            {"note": "A4", "time": 18.0, "duration": 0.4},
            {"note": "A4", "time": 18.5, "duration": 0.4},
            {"note": "G4", "time": 19.0, "duration": 0.8},
            {"note": "F4", "time": 20.0, "duration": 0.4},
            {"note": "F4", "time": 20.5, "duration": 0.4},
            {"note": "E4", "time": 21.0, "duration": 0.4},
            {"note": "E4", "time": 21.5, "duration": 0.4},
            {"note": "D4", "time": 22.0, "duration": 0.4},
            {"note": "D4", "time": 22.5, "duration": 0.4},
            {"note": "C4", "time": 23.0, "duration": 0.8}
        ]
    },
    {
        "id": "joy",
        "title": "Himno a la Alegría",
        "composer": "L.v. Beethoven",
        "notes": [
            {"note": "E4", "time": 0.0, "duration": 0.4},
            {"note": "E4", "time": 0.5, "duration": 0.4},
            {"note": "F4", "time": 1.0, "duration": 0.4},
            {"note": "G4", "time": 1.5, "duration": 0.4},
            {"note": "G4", "time": 2.0, "duration": 0.4},
            {"note": "F4", "time": 2.5, "duration": 0.4},
            {"note": "E4", "time": 3.0, "duration": 0.4},
            {"note": "D4", "time": 3.5, "duration": 0.4},
            {"note": "C4", "time": 4.0, "duration": 0.4},
            {"note": "C4", "time": 4.5, "duration": 0.4},
            {"note": "D4", "time": 5.0, "duration": 0.4},
            {"note": "E4", "time": 5.5, "duration": 0.4},
            {"note": "E4", "time": 6.0, "duration": 0.6},
            {"note": "D4", "time": 6.5, "duration": 0.2},
            {"note": "D4", "time": 6.8, "duration": 0.8},
            {"note": "E4", "time": 8.0, "duration": 0.4},
            {"note": "E4", "time": 8.5, "duration": 0.4},
            {"note": "F4", "time": 9.0, "duration": 0.4},
            {"note": "G4", "time": 9.5, "duration": 0.4},
            {"note": "G4", "time": 10.0, "duration": 0.4},
            {"note": "F4", "time": 10.5, "duration": 0.4},
            {"note": "E4", "time": 11.0, "duration": 0.4},
            {"note": "D4", "time": 11.5, "duration": 0.4},
            {"note": "C4", "time": 12.0, "duration": 0.4},
            {"note": "C4", "time": 12.5, "duration": 0.4},
            {"note": "D4", "time": 13.0, "duration": 0.4},
            {"note": "E4", "time": 13.5, "duration": 0.4},
            {"note": "D4", "time": 14.0, "duration": 0.6},
            {"note": "C4", "time": 14.5, "duration": 0.2},
            {"note": "C4", "time": 14.8, "duration": 0.8}
        ]
    },
    {
        "id": "birthday",
        "title": "Cumpleaños Feliz",
        "composer": "Mildred J. Hill & Patty Hill",
        "notes": [
            {"note": "G4", "time": 0.0, "duration": 0.3},
            {"note": "G4", "time": 0.35, "duration": 0.15},
            {"note": "A4", "time": 0.5, "duration": 0.4},
            {"note": "G4", "time": 1.0, "duration": 0.4},
            {"note": "C5", "time": 1.5, "duration": 0.4},
            {"note": "B4", "time": 2.0, "duration": 0.8},
            {"note": "G4", "time": 3.0, "duration": 0.3},
            {"note": "G4", "time": 3.35, "duration": 0.15},
            {"note": "A4", "time": 3.5, "duration": 0.4},
            {"note": "G4", "time": 4.0, "duration": 0.4},
            {"note": "D5", "time": 4.5, "duration": 0.4},
            {"note": "C5", "time": 5.0, "duration": 0.8},
            {"note": "G4", "time": 6.0, "duration": 0.3},
            {"note": "G4", "time": 6.35, "duration": 0.15},
            {"note": "G5", "time": 6.5, "duration": 0.4},
            {"note": "E5", "time": 7.0, "duration": 0.4},
            {"note": "C5", "time": 7.5, "duration": 0.4},
            {"note": "B4", "time": 8.0, "duration": 0.4},
            {"note": "A4", "time": 8.5, "duration": 0.4},
            {"note": "F5", "time": 9.2, "duration": 0.3},
            {"note": "F5", "time": 9.55, "duration": 0.15},
            {"note": "E5", "time": 9.7, "duration": 0.4},
            {"note": "C5", "time": 10.2, "duration": 0.4},
            {"note": "D5", "time": 10.7, "duration": 0.4},
            {"note": "C5", "time": 11.2, "duration": 0.8}
        ]
    }
]

# App Global States
selected_song_id = "none"
is_playing = False
playback_time = 0.0

# State Machine Constants and Variables
STATE_MENU = 0
STATE_FREE_PLAY = 1
STATE_TUTORIAL = 2

app_state = STATE_MENU
free_play_exit_timer = 0.0  # Tracks how long 'a' and '9' are held down to exit free play
carousel_index = 0
current_scroll = 0.0
target_scroll = 0.0
in_countdown = False
countdown_timer = 3.0
selection_timer = 0.0




CAROUSEL_OPTIONS = [
    {"id": "free", "title": "Modo libre"},
    {"id": "twinkle", "title": "Tutorial\ncanción\nEstrellita"},
    {"id": "joy", "title": "Tutorial\ncanción\nHimno a la Alegría"},
    {"id": "birthday", "title": "Tutorial\ncanción\nCumpleaños"}
]

# Gameplay Stats
score = 0
combo = 0
max_combo = 0
mistake_count = 0

active_notes = set()
guide_notes = set()
user_pressed_notes = set()
rainbow_notes_map = {}
mistakes_notes_map = {}

show_celebration = False
show_modal = False
modal_animation_timer = 0.0

# Confetti / Visual Particles
particles = []

class VisualParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = (pr.get_random_value(-100, 100) / 100.0) * 1.5
        self.vy = -(pr.get_random_value(100, 300) / 100.0)
        self.color = color
        self.alpha = 1.0
        self.size = pr.get_random_value(2, 5)

def get_white_key_rect(index, screen_w, kb_y, kb_h):
    x_start = int(index * screen_w / 21)
    x_end = int((index + 1) * screen_w / 21)
    return pr.Rectangle(x_start, kb_y, x_end - x_start - 2, kb_h)

def get_black_key_rect(preceding_index, screen_w, kb_y, kb_h):
    w_width_base = screen_w / 21
    b_width = int(w_width_base * 0.6)
    b_height = int(kb_h * 0.6)
    x_divider = int((preceding_index + 1) * screen_w / 21)
    left = x_divider - b_width // 2
    return pr.Rectangle(left, kb_y, b_width, b_height)

# Note key coordinates finder
def get_key_x(note_name, canvas_width):
    white_keys_list = [k for k in PIANO_KEYS if not k["is_black"]]
    
    # Find the target key
    key_info = None
    for k in PIANO_KEYS:
        if k["note"] == note_name:
            key_info = k
            break
            
    if not key_info:
        return 0, False, 10
        
    w_width_base = canvas_width / 21
    b_width = int(w_width_base * 0.6)

    if not key_info["is_black"]:
        idx = white_keys_list.index(key_info)
        x_start = int(idx * canvas_width / 21)
        x_end = int((idx + 1) * canvas_width / 21)
        center_x = (x_start + x_end) // 2
        return center_x, False, x_end - x_start
    else:
        # Preceding white key placement
        target_idx = PIANO_KEYS.index(key_info)
        preceding_white_note = PIANO_KEYS[target_idx - 1]["note"]
        idx = white_keys_list.index(next(k for k in white_keys_list if k["note"] == preceding_white_note))
        x_divider = int((idx + 1) * canvas_width / 21)
        return x_divider, True, b_width

# Handle user key hits
def handle_play_note(note, volume=1.0):
    active_notes.add(note)
    
    # Sound trigger via FluidSynth
    if fs_synth and sf_id != -1:
        midi_note = note_to_midi(note)
        velocity = int(max(0.0, min(1.0, volume)) * 127)
        fs_synth.noteon(0, midi_note, velocity)
        
    global score, combo, max_combo, mistake_count
    
    if is_playing and selected_song_id != "none":
        current_song = next((s for s in SONGS if s["id"] == selected_song_id), None)
        if current_song:
            next_note = next((n for n in current_song["notes"] if f"{n['time']}-{n['note']}" not in user_pressed_notes), None)
            
            if next_note:
                if note == next_note["note"]:
                    # Correct note hit!
                    user_pressed_notes.add(f"{next_note['time']}-{next_note['note']}")
                    hit_score = max(10, 100 - int(abs(playback_time - next_note["time"]) * 100))
                    score += hit_score
                    combo += 1
                    if combo > max_combo:
                        max_combo = combo
                    update_guide_notes(current_song)
                else:
                    # Wrong note hit!
                    if next_note["time"] <= playback_time + 1.0:
                        mistake_count += 1
                        combo = 0
                        trigger_mistake(note)

def handle_stop_note(note):
    active_notes.discard(note)
    if fs_synth and sf_id != -1:
        midi_note = note_to_midi(note)
        fs_synth.noteoff(0, midi_note)

def clear_all_active_notes():
    global prev_pressed_notes
    active_notes.clear()
    prev_pressed_notes.clear()
    if fs_synth:
        fs_synth.cc(0, 123, 0) # All Notes Off

def trigger_mistake(note):
    mistakes_notes_map[note] = 0.3 # shake duration
    
    # Spawn floating Oops label
    global oops_label_timer, oops_label_note
    oops_label_timer = 0.75
    oops_label_note = note

oops_label_timer = 0.0
oops_label_note = ""

def update_guide_notes(song):
    guide_notes.clear()
    next_note = next((n for n in song["notes"] if f"{n['time']}-{n['note']}" not in user_pressed_notes), None)
    if next_note:
        notes_at_time = [n for n in song["notes"] if n["time"] == next_note["time"]]
        for n in notes_at_time:
            guide_notes.add(n["note"])

# Victory arpeggio scheduled items
scheduled_fanfare = []
scheduled_releases = []

def play_celebration_fanfare():
    now = pr.get_time()
    scheduled_fanfare.append((now + 0.0, "C4", 0.4))
    scheduled_fanfare.append((now + 0.15, "E4", 0.4))
    scheduled_fanfare.append((now + 0.3, "G4", 0.4))
    scheduled_fanfare.append((now + 0.45, "C5", 0.4))
    
    # Final chord
    for n in ["C4", "E4", "G4", "C5", "E5"]:
        scheduled_fanfare.append((now + 0.65, n, 2.5))

def trigger_rainbow_cascade():
    colors = [
        pr.Color(30, 58, 138, 255),    # Deep Navy Blue (900)
        pr.Color(29, 78, 216, 255),    # Royal Blue (700)
        pr.Color(37, 99, 235, 255),    # Vibrant Blue (600)
        pr.Color(59, 130, 246, 255),   # Electric Blue (500)
        pr.Color(96, 165, 250, 255),   # Sky Blue (400)
        pr.Color(56, 189, 248, 255),   # Light Sky Blue (Sky 400)
        pr.Color(147, 197, 253, 255)   # Ice Blue (300)
    ]
    
    now = pr.get_time()
    for index, key in enumerate(PIANO_KEYS):
        trigger_time = now + index * 0.04
        color = colors[index % len(colors)]
        scheduled_rainbow.append((trigger_time, key["note"], color))

scheduled_rainbow = []
active_rainbow_keys = {}

def close_celebration_modal():
    global show_celebration, show_modal, selected_song_id, is_playing, app_state
    show_celebration = False
    show_modal = False
    active_rainbow_keys.clear()
    selected_song_id = "none"
    is_playing = False
    handle_song_change("none")
    clear_all_active_notes()
    app_state = STATE_MENU

def stop_song_playback():
    global is_playing
    is_playing = False
    guide_notes.clear()
    clear_all_active_notes()

def reset_stats():
    global score, combo, max_combo, mistake_count
    score = 0
    combo = 0
    max_combo = 0
    mistake_count = 0
    user_pressed_notes.clear()

def handle_song_change(song_id):
    global selected_song_id, is_playing, playback_time
    selected_song_id = song_id
    reset_stats()
    guide_notes.clear()
    
    if song_id == "none":
        is_playing = False
    else:
        is_playing = True
        playback_time = 0.0
        
        song = next((s for s in SONGS if s["id"] == song_id), None)
        if song:
            update_guide_notes(song)

# Premium Vector Drawing Helpers
def draw_star(cx, cy, r_out, r_in, color):
    points = []
    for i in range(10):
        angle = i * math.pi / 5 - math.pi / 2
        r = r_out if i % 2 == 0 else r_in
        x = cx + math.cos(angle) * r
        y = cy + math.sin(angle) * r
        points.append(pr.Vector2(x, y))
        
    for i in range(10):
        p1 = points[i]
        p2 = points[(i + 1) % 10]
        pr.draw_triangle(pr.Vector2(cx, cy), p1, p2, color)

def draw_vector_trophy(cx, cy, scale):
    # Base Pedestal shadow and body
    pr.draw_rectangle_rounded(pr.Rectangle(cx - int(35 * scale), cy + int(38 * scale), int(70 * scale), int(10 * scale)), 0.3, 4, pr.Color(23, 23, 23, 255))
    pr.draw_rectangle_rounded(pr.Rectangle(cx - int(25 * scale), cy + int(28 * scale), int(50 * scale), int(10 * scale)), 0.3, 4, pr.Color(40, 40, 40, 255))
    
    # Stem
    pr.draw_rectangle_gradient_v(cx - int(8 * scale), cy + int(10 * scale), int(16 * scale), int(18 * scale), pr.Color(217, 119, 6, 255), pr.Color(180, 83, 9, 255))
    
    # Left and Right Handles
    pr.draw_ring(pr.Vector2(cx - int(24 * scale), cy - int(10 * scale)), int(11 * scale), int(16 * scale), 90, 270, 16, pr.Color(245, 158, 11, 255))
    pr.draw_ring(pr.Vector2(cx + int(24 * scale), cy - int(10 * scale)), int(11 * scale), int(16 * scale), -90, 90, 16, pr.Color(245, 158, 11, 255))
    
    # Cup Main Body
    pr.draw_rectangle_rounded(pr.Rectangle(cx - int(25 * scale), cy - int(30 * scale), int(50 * scale), int(42 * scale)), 0.35, 4, pr.Color(245, 158, 11, 255))
    # Cup top shading ellipse
    pr.draw_ellipse(cx, cy - int(30 * scale), int(25 * scale), int(7 * scale), pr.Color(252, 211, 77, 255))
    # Cup highlights
    pr.draw_rectangle(cx - int(20 * scale), cy - int(23 * scale), int(8 * scale), int(30 * scale), pr.Color(252, 211, 77, 120))

# Premium Vector Drawing Helpers for Menu
def draw_vector_note(cx, cy, scale, color):
    r = 14 * scale
    # Note heads (angled ellipses)
    pr.draw_ellipse(int(cx - 30 * scale), int(cy + 20 * scale), int(16 * scale), int(12 * scale), color)
    pr.draw_ellipse(int(cx + 20 * scale), int(cy + 5 * scale), int(16 * scale), int(12 * scale), color)
    
    # Stems
    stem_w = max(2, int(6 * scale))
    stem_h = int(60 * scale)
    pr.draw_rectangle(int(cx - 30 * scale + 12 * scale), int(cy + 20 * scale - stem_h), stem_w, stem_h, color)
    pr.draw_rectangle(int(cx + 20 * scale + 12 * scale), int(cy + 5 * scale - stem_h), stem_w, stem_h, color)
    
    # Beam
    p1 = pr.Vector2(cx - 30 * scale + 12 * scale, cy + 20 * scale - stem_h)
    p2 = pr.Vector2(cx + 20 * scale + 12 * scale, cy + 5 * scale - stem_h)
    beam_h = int(14 * scale)
    pr.draw_line_ex(pr.Vector2(p1.x + stem_w/2, p1.y + beam_h/2), pr.Vector2(p2.x + stem_w/2, p2.y + beam_h/2), beam_h, color)

def draw_vector_arrow(cx, cy, scale, is_right, color):
    w = 20 * scale
    h = 30 * scale
    thickness = max(3, int(6 * scale))
    
    if is_right:
        p_tip = pr.Vector2(cx + w // 2, cy)
        p_top = pr.Vector2(cx - w // 2, cy - h // 2)
        p_bottom = pr.Vector2(cx - w // 2, cy + h // 2)
    else:
        p_tip = pr.Vector2(cx - w // 2, cy)
        p_top = pr.Vector2(cx + w // 2, cy - h // 2)
        p_bottom = pr.Vector2(cx + w // 2, cy + h // 2)
    pr.draw_line_ex(p_top, p_tip, thickness, color)
    pr.draw_line_ex(p_bottom, p_tip, thickness, color)

def draw_texture_centered(tex, cx, cy, w, h, color):
    if tex:
        source_rec = pr.Rectangle(0, 0, tex.width, tex.height)
        dest_rec = pr.Rectangle(int(cx - w // 2), int(cy - h // 2), int(w), int(h))
        origin = pr.Vector2(0, 0)
        pr.draw_texture_pro(tex, source_rec, dest_rec, origin, 0.0, color)

def draw_menu_note(cx, cy, scale, color):
    if nota_texture:
        h = int(80 * scale)
        aspect = nota_texture.width / nota_texture.height
        w = int(h * aspect)
        draw_texture_centered(nota_texture, cx, cy, w, h, color)
    else:
        draw_vector_note(cx, cy, scale, color)

def draw_menu_arrow(cx, cy, scale, is_right, color):
    tex = flecha_der_texture if is_right else flecha_izq_texture
    if tex:
        h = int(40 * scale)
        aspect = tex.width / tex.height
        w = int(h * aspect)
        draw_texture_centered(tex, cx, cy, w, h, color)
    else:
        draw_vector_arrow(cx, cy, scale, is_right, color)

# GUI States
song_select_open = False
song_select_rect = pr.Rectangle(0, 0, 0, 0)

# Touch/Mouse held tracking
prev_pressed_notes = set()

# Main Application Loop
while not pr.window_should_close():
    delta_time = pr.get_frame_time()
    m_pos = pr.get_mouse_position()
    
    # ------------------ LOADING PHASE ------------------
    if loading_progress < len(PIANO_KEYS):
        load_samples_tick()
        
        pr.begin_drawing()
        pr.clear_background(pr.Color(10, 10, 10, 255))
        
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()
        
        # Load modern font at start if ready, else use default text
        draw_text_modern("GPIANO", sw // 2 - measure_text_modern_width("GPIANO", 40) // 2, sh // 2 - 80, 40, pr.WHITE)
        
        # Draw loading bar
        bar_w = 340
        bar_h = 8
        bar_x = sw // 2 - bar_w // 2
        bar_y = sh // 2 - 4
        
        pr.draw_rectangle_rounded(pr.Rectangle(bar_x, bar_y, bar_w, bar_h), 1.0, 4, pr.Color(38, 38, 38, 255))
        progress_w = int(bar_w * (loading_progress / len(PIANO_KEYS)))
        pr.draw_rectangle_rounded(pr.Rectangle(bar_x, bar_y, progress_w, bar_h), 1.0, 4, pr.Color(14, 165, 233, 255))
        
        load_lbl = "Cargando muestras de sonido..."
        draw_text_modern(load_lbl, sw // 2 - measure_text_modern_width(load_lbl, 16) // 2, sh // 2 + 30, 16, pr.Color(163, 163, 163, 255))
        pr.end_drawing()
        continue
        
    # ------------------ GAMEPLAY PHASE ------------------
    
    # 1. Update Fanfare and Rainbow Cascades (Celebration)
    now_time = pr.get_time()
    
    # Ascending arpeggio scheduled notes playback
    for item in list(scheduled_fanfare):
        trigger_time, note, duration = item
        if now_time >= trigger_time:
            if fs_synth and sf_id != -1:
                midi_note = note_to_midi(note)
                fs_synth.noteon(0, midi_note, 127)
            scheduled_releases.append((now_time + duration, note))
            scheduled_fanfare.remove(item)
            
    # Scheduled arpeggio releases
    for item in list(scheduled_releases):
        release_time, note = item
        if now_time >= release_time:
            if fs_synth and sf_id != -1:
                midi_note = note_to_midi(note)
                fs_synth.noteoff(0, midi_note)
            scheduled_releases.remove(item)
            
    # Rainbow keys cascade animation
    for item in list(scheduled_rainbow):
        trigger_time, note, color = item
        if now_time >= trigger_time:
            active_rainbow_keys[note] = (now_time + 1.5, color)
            scheduled_rainbow.remove(item)
            
    # Clear expired rainbow keys
    for note, val in list(active_rainbow_keys.items()):
        expire_time, color = val
        if now_time >= expire_time:
            del active_rainbow_keys[note]
            
    # Key shake mistake timers
    for note, duration in list(mistakes_notes_map.items()):
        next_dur = duration - delta_time
        if next_dur <= 0:
            del mistakes_notes_map[note]
        else:
            mistakes_notes_map[note] = next_dur
            
    # Oops label floating text timer
    if oops_label_timer > 0:
        oops_label_timer -= delta_time

    # Countdown timer update
    if in_countdown:
        countdown_timer -= delta_time
        if countdown_timer <= 0.0:
            in_countdown = False

    # Update active sound fade outs is handled natively by FluidSynth ADSR release envelope

    # 2. Practice/Solo Game Mode Loop
    if is_playing and selected_song_id != "none" and not in_countdown:
        current_song = next((s for s in SONGS if s["id"] == selected_song_id), None)
        if current_song:
            next_note = next((n for n in current_song["notes"] if f"{n['time']}-{n['note']}" not in user_pressed_notes), None)
            next_time = playback_time + delta_time
            
            if not next_note:
                song_length = max(n["time"] + n["duration"] for n in current_song["notes"]) + 1.0
                if playback_time >= song_length:
                    stop_song_playback()
                    show_celebration = True
                    play_celebration_fanfare()
                    trigger_rainbow_cascade()
                    modal_animation_timer = 0.0
                    show_modal = False
            else:
                # Solo practice mode timing lock
                if playback_time >= next_note["time"]:
                    next_time = next_note["time"]
                elif next_time >= next_note["time"]:
                    next_time = next_note["time"]
                    
            playback_time = next_time
    elif app_state == STATE_FREE_PLAY and not in_countdown:
        if pr.is_key_down(pr.KEY_A) and pr.is_key_down(pr.KEY_NINE):
            free_play_exit_timer += delta_time
            if free_play_exit_timer >= 5.0:
                clear_all_active_notes()
                app_state = STATE_MENU
                handle_song_change("none")
        else:
            free_play_exit_timer = 0.0

    # Update modal timer
    if show_celebration and not show_modal:
        modal_animation_timer += delta_time
        if modal_animation_timer >= 1.5:
            show_modal = True

    # Exit celebration if modal is open and key is pressed
    just_closed_modal = False
    if show_celebration and show_modal:
        if pr.get_key_pressed() != 0:
            close_celebration_modal()
            just_closed_modal = True

    # 3. Process pointer and QWERTY keyboard inputs
    sw = pr.get_screen_width()
    sh = pr.get_screen_height()
    
    # Calculate responsiveness scale factor
    # Calculate responsiveness scale factor
    ui_scale = min(sw / 1024.0, sh / 600.0)
    
    # Menu Navigation logic
    if app_state == STATE_MENU and not just_closed_modal:
        # Update selection/blink timer
        if selection_timer > 0.0:
            selection_timer -= delta_time
            if selection_timer <= 0.0:
                selection_timer = 0.0
                clear_all_active_notes()
                # Perform the transition now that the blink is done
                option = CAROUSEL_OPTIONS[carousel_index]
                if option["id"] == "free":
                    app_state = STATE_FREE_PLAY
                    free_play_exit_timer = 0.0
                    handle_song_change("none")
                    in_countdown = True
                    countdown_timer = 3.0
                else:
                    app_state = STATE_TUTORIAL
                    handle_song_change(option["id"])
                    in_countdown = True
                    countdown_timer = 3.0

        # Smooth scroll interpolation
        if current_scroll != target_scroll:
            current_scroll += (target_scroll - current_scroll) * 12.0 * delta_time
            if abs(target_scroll - current_scroll) < 0.005:
                current_scroll = target_scroll
                
        # Check QWERTY keyboard first (piano keys mapping)
        if current_scroll == target_scroll and selection_timer == 0.0:
            if pr.is_key_pressed(pr.KEY_A):  # Left
                target_scroll = current_scroll - 1.0
                carousel_index = int(round(target_scroll)) % len(CAROUSEL_OPTIONS)
                if click_sound:
                    pr.play_sound(click_sound)
            elif pr.is_key_pressed(pr.KEY_E):  # Right
                target_scroll = current_scroll + 1.0
                carousel_index = int(round(target_scroll)) % len(CAROUSEL_OPTIONS)
                if click_sound:
                    pr.play_sound(click_sound)
                
        # Enter action is only processed if scroll has completed
        if pr.is_key_pressed(pr.KEY_C) and current_scroll == target_scroll and selection_timer == 0.0:  # Enter
            if select_sound:
                pr.play_sound(select_sound)
            selection_timer = 0.6  # 600ms blink duration
                
        # Check mouse/touch clicks on carousel elements
        if pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT) and selection_timer == 0.0:
            m_pos = pr.get_mouse_position()
            
            center_card_w = int(260 * ui_scale)
            center_card_h = int(360 * ui_scale)
            side_card_w = int(200 * ui_scale)
            side_card_h = int(280 * ui_scale)
            card_cy = sh // 2 + int(20 * ui_scale)
            
            left_card_x = sw // 2 - int(250 * ui_scale) - side_card_w // 2
            center_card_x = sw // 2 - center_card_w // 2
            right_card_x = sw // 2 + int(250 * ui_scale) - side_card_w // 2
            
            arrow_size = int(40 * ui_scale)
            left_arrow_x = sw // 2 - int(420 * ui_scale)
            right_arrow_x = sw // 2 + int(420 * ui_scale)
            
            left_card_rect = pr.Rectangle(left_card_x, card_cy - side_card_h // 2, side_card_w, side_card_h)
            center_card_rect = pr.Rectangle(center_card_x, card_cy - center_card_h // 2, center_card_w, center_card_h)
            right_card_rect = pr.Rectangle(right_card_x, card_cy - side_card_h // 2, side_card_w, side_card_h)
            left_arrow_rect = pr.Rectangle(left_arrow_x - arrow_size // 2 - 20, card_cy - arrow_size // 2 - 20, arrow_size + 40, arrow_size + 40)
            right_arrow_rect = pr.Rectangle(right_arrow_x - arrow_size // 2 - 20, card_cy - arrow_size // 2 - 20, arrow_size + 40, arrow_size + 40)
            
            if current_scroll == target_scroll:
                if pr.check_collision_point_rec(m_pos, left_arrow_rect) or pr.check_collision_point_rec(m_pos, left_card_rect):
                    target_scroll = current_scroll - 1.0
                    carousel_index = int(round(target_scroll)) % len(CAROUSEL_OPTIONS)
                    if click_sound:
                        pr.play_sound(click_sound)
                elif pr.check_collision_point_rec(m_pos, right_arrow_rect) or pr.check_collision_point_rec(m_pos, right_card_rect):
                    target_scroll = current_scroll + 1.0
                    carousel_index = int(round(target_scroll)) % len(CAROUSEL_OPTIONS)
                    if click_sound:
                        pr.play_sound(click_sound)
                elif pr.check_collision_point_rec(m_pos, center_card_rect):
                    if select_sound:
                        pr.play_sound(select_sound)
                    selection_timer = 0.6  # 600ms blink duration


    # Layout Coordinates
    top_height = int(80 * ui_scale)
    keyboard_h = int(sh * 0.35)
    keyboard_y = sh - keyboard_h - 10
    visualizer_y = top_height
    visualizer_h = keyboard_y - visualizer_y
    
    # Gather Touch + Mouse positions
    active_points = []
    if pr.is_mouse_button_down(pr.MOUSE_BUTTON_LEFT):
        m_pos = pr.get_mouse_position()
        if not (song_select_open and pr.check_collision_point_rec(m_pos, pr.Rectangle(song_select_rect.x, song_select_rect.y, song_select_rect.width, song_select_rect.height + len(SONGS) * int(40 * ui_scale)))):
            if not pr.check_collision_point_rec(m_pos, song_select_rect) and not (show_celebration and show_modal):
                active_points.append(m_pos)
                
    for t in range(pr.get_touch_point_count()):
        active_points.append(pr.get_touch_position(t))
        
    # Check notes pressed by mouse/touch
    pressed_by_touch = {}
    if not (show_celebration and show_modal) and app_state != STATE_MENU and not in_countdown:
        for pt in active_points:
            # Check black keys first (overlay z-order)
            hit_black = False
            for bk in black_keys:
                rect = get_black_key_rect(bk["white_index"], sw, keyboard_y, keyboard_h)
                if pr.check_collision_point_rec(pt, rect):
                    # Calculate volume based on Y coordinate (top to bottom of black key)
                    rel_y = (pt.y - rect.y) / rect.height
                    volume = 0.35 + 0.65 * max(0.0, min(1.0, rel_y))
                    pressed_by_touch[bk["note"]] = volume
                    hit_black = True
                    break
            if not hit_black:
                # Check white keys
                for index, wk in enumerate(white_keys):
                    rect = get_white_key_rect(index, sw, keyboard_y, keyboard_h)
                    if pr.check_collision_point_rec(pt, rect):
                        # Calculate volume based on Y coordinate (top to bottom of white key)
                        rel_y = (pt.y - rect.y) / rect.height
                        volume = 0.35 + 0.65 * max(0.0, min(1.0, rel_y))
                        pressed_by_touch[wk["note"]] = volume
                        break
                        
    # Compare with previous frame to trigger attacks/releases
    for note, vol in pressed_by_touch.items():
        if note not in prev_pressed_notes:
            handle_play_note(note, vol)
            
    for note in prev_pressed_notes:
        if note not in pressed_by_touch:
            handle_stop_note(note)
            
    prev_pressed_notes = set(pressed_by_touch.keys())

    # Read QWERTY keyboard mappings
    if not (show_celebration and show_modal) and app_state != STATE_MENU and not in_countdown:
        for key_data in PIANO_KEYS:
            char = key_data["key"]
            r_key = KEY_MAP_RAYLIB.get(char)
            if r_key:
                if pr.is_key_pressed(r_key):
                    handle_play_note(key_data["note"])
                elif pr.is_key_released(r_key):
                    handle_stop_note(key_data["note"])

    # 4. Drawing Canvas Elements (Hardware Accelerated GPU)
    pr.begin_drawing()
    
    if app_state == STATE_MENU:
        # Clear background to a very clean light gray
        pr.clear_background(pr.Color(245, 245, 245, 255))
        
        # --- Draw Top Panel Header (Premium sharp card with 90° corners, full-width) ---
        top_height = int(80 * ui_scale)
        pr.draw_rectangle(0, 0, sw, top_height, pr.WHITE)
        pr.draw_line(0, top_height, sw, top_height, pr.Color(200, 200, 200, 255))
        
        # Left Logo & Info Scale calculations
        title_sz = int(24 * ui_scale)
        desc_sz = int(11 * ui_scale)
        
        # Responsive Visibility Rules
        show_subtitle = True
        show_title = True
        
        if sw < 1100:
            show_subtitle = False
        if sw < 800:
            show_title = False
            
        # Draw Left block (Title/Subtitle)
        if show_title:
            draw_text_modern("GPiano", 25, int(top_height/2 - title_sz), title_sz, pr.Color(20, 20, 20, 255))
            if show_subtitle:
                draw_text_modern("Aprende tocando tus canciones favoritas", 25, int(top_height/2 + 2), desc_sz, pr.Color(100, 100, 100, 255))
            else:
                draw_text_modern("GPiano", 25, int(top_height/2 - title_sz/2), title_sz, pr.Color(20, 20, 20, 255))
        
        # Draw Logo centered both horizontally and vertically in the header (Absolute Center)
        if logo_texture:
            logo_aspect = logo_texture.width / logo_texture.height
            target_h = int(top_height * 0.75)
            target_w = int(target_h * logo_aspect)
            
            logo_x = sw // 2 - target_w // 2
            logo_y = top_height // 2 - target_h // 2
            
            source_rect = pr.Rectangle(0, 0, logo_texture.width, logo_texture.height)
            dest_rect = pr.Rectangle(logo_x, logo_y, target_w, target_h)
            origin = pr.Vector2(0, 0)
            pr.draw_texture_pro(logo_texture, source_rect, dest_rect, origin, 0.0, pr.WHITE)
            
        # 1. Draw Title "Elige una opción:"
        title_text = "Elige una opción:"
        title_font_sz = int(32 * ui_scale)
        title_w = measure_text_modern_width(title_text, title_font_sz)
        draw_text_modern(title_text, sw // 2 - title_w // 2, top_height + int(25 * ui_scale), title_font_sz, pr.BLACK)
        
        # 2. Dynamic card drawing loop
        card_cy = sh // 2 + int(20 * ui_scale)
        center_i = int(round(current_scroll))
        
        # Sort indices to draw furthest cards first (back-to-front z-ordering)
        draw_indices = list(range(center_i - 2, center_i + 3))
        draw_indices.sort(key=lambda idx: -abs(idx - current_scroll))
        
        for i in draw_indices:
            opt_idx = i % len(CAROUSEL_OPTIONS)
            opt = CAROUSEL_OPTIONS[opt_idx]
            
            diff = i - current_scroll
            
            # Skip if card is too far to be visible
            if abs(diff) > 2.0:
                continue
                
            # Size scale factor based on distance from center
            if abs(diff) <= 1.0:
                scale_factor = 1.0 - abs(diff) * 0.23
            else:
                scale_factor = 0.77 - (abs(diff) - 1.0) * 0.17
            scale_factor = max(0.5, scale_factor)
            
            # Calculate coordinates as floats first, then convert using int(round()) to prevent sub-pixel jitter
            card_cx_float = sw / 2.0 + diff * 250.0 * ui_scale
            card_cy_float = sh / 2.0 + 20.0 * ui_scale
            w_float = 260.0 * ui_scale * scale_factor
            h_float = 360.0 * ui_scale * scale_factor
            
            card_x = int(round(card_cx_float - w_float / 2.0))
            card_y = int(round(card_cy_float - h_float / 2.0))
            card_w = int(round(w_float))
            card_h = int(round(h_float))
            
            card_rect = pr.Rectangle(card_x, card_y, card_w, card_h)
            
            # Opacity/Alpha (smoothly fades out at edges)
            if abs(diff) <= 1.0:
                alpha = 255
            else:
                alpha = int(max(0, 1.0 - (abs(diff) - 1.0)) * 255)
                
            # Color blending: Active (diff=0) is black; Inactive (diff=1) is gray.
            t = min(1.0, abs(diff))
            
            # Lerp border color
            border_r = int(0 + t * 180)
            border_g = int(0 + t * 180)
            border_b = int(0 + t * 180)
            border_color = pr.Color(border_r, border_g, border_b, alpha)
            
            # Border thickness (2 for center card, 1 for side cards)
            border_thick = int(max(1, round(2 - t * 1)))
            
            # Lerp text/note color
            text_r = int(0 + t * 160)
            text_g = int(0 + t * 160)
            text_b = int(0 + t * 160)
            text_color = pr.Color(text_r, text_g, text_b, alpha)
            
            # Draw card background (White with alpha, or blinking if selected)
            is_selected_blink = (opt_idx == carousel_index and selection_timer > 0.0)
            if is_selected_blink:
                # Blink effect: alternate between white and a premium light-blue highlight (Sky 100/500)
                if int(selection_timer * 10) % 2 == 0:
                    bg_color = pr.Color(224, 242, 254, alpha)  # Light Sky Blue
                    border_color = pr.Color(2, 132, 199, alpha)  # Electric Blue border
                    border_thick = int(3 * ui_scale)
                    text_color = pr.Color(3, 105, 161, alpha)  # Deep blue text
                else:
                    bg_color = pr.Color(255, 255, 255, alpha)
                    border_color = pr.Color(14, 165, 233, alpha)
                    border_thick = int(3 * ui_scale)
                    text_color = pr.Color(14, 165, 233, alpha)
            else:
                bg_color = pr.Color(255, 255, 255, alpha)
                
            pr.draw_rectangle_rec(card_rect, bg_color)
            pr.draw_rectangle_lines_ex(card_rect, border_thick, border_color)
            
            # Draw card icon (centered in top half)
            note_cx = int(round(card_cx_float))
            note_cy = int(round(card_cy_float - 45.0 * ui_scale * scale_factor))
            draw_menu_note(note_cx, note_cy, scale_factor * ui_scale, text_color)
            
            # Draw Text
            opt_text = opt["title"]
            opt_sz = int(15 * ui_scale) # Fixed font size prevents Raylib font glyph scale jittering
            lines = opt_text.split("\n")
            
            # Text starts in bottom half of the card
            text_start_y = int(round(card_cy_float + 25.0 * ui_scale * scale_factor))
            line_height = int(round(24.0 * ui_scale * scale_factor))
            
            for line_idx, line in enumerate(lines):
                lw = measure_text_modern_width(line, opt_sz)
                draw_text_modern(line, note_cx - lw // 2, text_start_y + line_idx * line_height, opt_sz, text_color)
                
            # Draw D3 Accept hint on the active center card
            if opt_idx == carousel_index and abs(diff) < 0.1:
                accept_text = 'Presiona "D3" para aceptar'
                accept_sz = int(13 * ui_scale)
                accept_w = measure_text_modern_width(accept_text, accept_sz)
                accept_y = int(card_y + card_h - 25 * ui_scale)
                draw_text_modern(accept_text, note_cx - accept_w // 2, accept_y, accept_sz, text_color)
                
        # 3. Draw Left and Right Arrows
        left_arrow_x = sw // 2 - int(420 * ui_scale)
        right_arrow_x = sw // 2 + int(420 * ui_scale)
        
        draw_menu_arrow(left_arrow_x, card_cy, 1.2 * ui_scale, False, pr.BLACK)
        draw_menu_arrow(right_arrow_x, card_cy, 1.2 * ui_scale, True, pr.BLACK)
        
        # Draw piano key hints above arrows (symmetrical)
        arrow_lbl_sz = int(22 * ui_scale)
        c3_w = measure_text_modern_width("C3", arrow_lbl_sz)
        e3_w = measure_text_modern_width("E3", arrow_lbl_sz)
        draw_text_modern("C3", left_arrow_x - c3_w // 2, card_cy - int(52 * ui_scale), arrow_lbl_sz, pr.Color(100, 116, 139, 255))
        draw_text_modern("E3", right_arrow_x - e3_w // 2, card_cy - int(52 * ui_scale), arrow_lbl_sz, pr.Color(100, 116, 139, 255))
        
        pr.end_drawing()
        continue

    pr.clear_background(pr.Color(10, 10, 10, 255)) # Premium pitch dark

    # --- Draw Falling Notes Visualizer Area ---
    pr.draw_rectangle(0, visualizer_y, sw, visualizer_h, pr.WHITE)
    
    # White key vertical guide lines (translucent for modern look)
    w_width = sw / 21
    for i in range(1, 21):
        pr.draw_line(int(i * w_width), visualizer_y, int(i * w_width), visualizer_y + visualizer_h, pr.Color(38, 38, 38, 120))
        
    # Draw guides and falling blocks if a song is playing
    if is_playing and selected_song_id != "none":
        current_song = next((s for s in SONGS if s["id"] == selected_song_id), None)
        if current_song:
            time_window = 3.0
            
            # Active note columns backglow (gorgeous transparent columns)
            for note in current_song["notes"]:
                is_active = playback_time >= note["time"] and playback_time <= note["time"] + note["duration"]
                if is_active:
                    x_coord, is_b, kw = get_key_x(note["note"], sw)
                    col = pr.Color(217, 119, 6, 45) if is_b else pr.Color(2, 132, 199, 45)
                    pr.draw_rectangle(x_coord - kw // 2, visualizer_y, kw, visualizer_h, col)
                    
            # Draw actual falling note blocks
            for note in current_song["notes"]:
                note_end = note["time"] + note["duration"]
                is_visible = note_end >= playback_time and note["time"] <= playback_time + time_window
                
                if is_visible:
                    x_coord, is_b, kw = get_key_x(note["note"], sw)
                    bottom_y = visualizer_y + visualizer_h - int(((note["time"] - playback_time) / time_window) * visualizer_h)
                    top_y = visualizer_y + visualizer_h - int(((note_end - playback_time) / time_window) * visualizer_h)
                    
                    is_active = playback_time >= note["time"] and playback_time <= note_end
                    if is_active:
                        bottom_y = visualizer_y + visualizer_h
                        # Spawn impact particles
                        if pr.get_random_value(0, 10) < 4:
                            p_color = "#f59e0b" if is_b else "#0ea5e9"
                            particles.append(VisualParticle(x_coord, visualizer_y + visualizer_h - 2, p_color))
                            
                    block_h = max(8, bottom_y - top_y)
                    block_y = top_y
                    
                    # Rounded rectangle drawing with border outline
                    rect = pr.Rectangle(x_coord - kw // 2, block_y, kw, block_h)
                    color = pr.Color(245, 158, 11, 255) if is_b else pr.Color(14, 165, 233, 255) # Orange or Blue
                    if not is_active:
                        color.a = 180
                    
                    pr.draw_rectangle_rounded(rect, 0.25, 4, color)
                    
                    # Faint outer border for contrast
                    pr.draw_rectangle_rounded_lines(rect, 0.25, 4, pr.Color(0, 0, 0, 40))
                    
                    # Highlight outline border for active note hitting
                    if is_active:
                        pr.draw_rectangle_rounded_lines(rect, 0.25, 4, pr.WHITE)
                        
                    # Display note name inside block (Premium Typography)
                    if block_h > 15:
                        label = note["note"].replace("#", "s")
                        text_col = pr.Color(28, 25, 23, 255) if is_b else pr.WHITE
                        font_sz = max(9, int(11 * ui_scale))
                        text_w = measure_text_modern_width(label, font_sz)
                        draw_text_modern(label, x_coord - text_w // 2, block_y + block_h // 2 - font_sz // 2, font_sz, text_col)

    # Draw target line at bottom of visualizer
    pr.draw_line_ex(pr.Vector2(0, visualizer_y + visualizer_h), pr.Vector2(sw, visualizer_y + visualizer_h), 2, pr.Color(64, 64, 64, 255))

    # --- Draw Keyboard Area ---
    # Layer 1: White Keys (with vertical color gradients)
    for index, wk in enumerate(white_keys):
        is_active = wk["note"] in active_notes or wk["note"] in guide_notes
        is_rainbow = active_rainbow_keys.get(wk["note"])
        is_shaking = wk["note"] in mistakes_notes_map
        
        rect = get_white_key_rect(index, sw, keyboard_y, keyboard_h)
        
        # Shake effect offset
        if is_shaking:
            rect.x += math.sin(pr.get_time() * 50) * 4
            
        color_top = pr.Color(255, 255, 255, 255) # Top white
        color_bottom = pr.Color(230, 230, 230, 255) # Bottom gray
        border_col = pr.Color(186, 186, 186, 255)
        b_offset = 6
        
        if is_shaking:
            color_top = pr.Color(248, 113, 113, 255) # Red mistake top
            color_bottom = pr.Color(220, 38, 38, 255) # Red mistake bottom
            border_col = pr.Color(153, 27, 27, 255)
            b_offset = 2
        elif is_active:
            color_top = pr.Color(56, 189, 248, 255) # Sky active top
            color_bottom = pr.Color(2, 132, 199, 255) # Sky active bottom
            border_col = pr.Color(3, 105, 161, 255)
            b_offset = 2
        elif is_rainbow:
            color_top = is_rainbow[1]
            color_bottom = pr.Color(int(color_top.r*0.7), int(color_top.g*0.7), int(color_top.b*0.7), 255)
            border_col = pr.Color(int(color_top.r*0.5), int(color_top.g*0.5), int(color_top.b*0.5), 255)
            b_offset = 2
            
        # Sinking Y-offset
        y_offset = int(4 * ui_scale) if (is_active or is_shaking or is_rainbow) else 0

        # Draw Key body using vertical gradient
        pr.draw_rectangle_gradient_v(int(rect.x), int(rect.y + y_offset), int(rect.width), int(rect.height - b_offset - y_offset), color_top, color_bottom)
        # Draw Key bottom border (simulate 3D depth)
        pr.draw_rectangle_gradient_v(int(rect.x), int(rect.y + rect.height - b_offset), int(rect.width), b_offset, border_col, pr.Color(int(border_col.r*0.8), int(border_col.g*0.8), int(border_col.b*0.8), 255))
        

        
        # Draw musical note label (High contrast!)
        font_sz = max(9, int(13 * ui_scale))
        lbl = wk["note"]
        lbl_w = measure_text_modern_width(lbl, font_sz)
        
        if is_shaking:
            lbl_color = pr.WHITE
        elif is_active:
            lbl_color = pr.Color(15, 23, 42, 255) # Dark slate/navy
        else:
            lbl_color = pr.Color(70, 70, 70, 255) # Dark charcoal
            
        draw_text_modern(lbl, int(rect.x + rect.width / 2 - lbl_w // 2), int(rect.y + rect.height - 25 * ui_scale + y_offset), font_sz, lbl_color)
        

        
        # Mistake floating oops label
        if oops_label_timer > 0 and oops_label_note == wk["note"]:
            lbl_oops = "Oops!"
            oops_sz = max(10, int(13 * ui_scale))
            oops_w = measure_text_modern_width(lbl_oops, oops_sz)
            float_dist = (0.75 - oops_label_timer) * 80 * ui_scale
            oops_y = int(rect.y + y_offset - float_dist)
            cap_w = oops_w + int(16 * ui_scale)
            cap_h = oops_sz + int(8 * ui_scale)
            cap_x = int(rect.x + rect.width / 2 - cap_w / 2)
            cap_y = oops_y - cap_h // 2
            alpha = int((oops_label_timer / 0.75) * 255)
            pr.draw_rectangle_rounded(pr.Rectangle(cap_x, cap_y, cap_w, cap_h), 0.5, 4, pr.Color(220, 38, 38, alpha))
            pr.draw_rectangle_rounded_lines(pr.Rectangle(cap_x, cap_y, cap_w, cap_h), 0.5, 4, pr.Color(153, 27, 27, int(alpha * 0.8)))
            draw_text_modern(lbl_oops, cap_x + cap_w // 2 - oops_w // 2, cap_y + cap_h // 2 - oops_sz // 2, oops_sz, pr.Color(255, 255, 255, alpha))

    # Layer 2: Black Keys (with bevels and vertical gradients)
    for bk in black_keys:
        is_active = bk["note"] in active_notes or bk["note"] in guide_notes
        is_rainbow = active_rainbow_keys.get(bk["note"])
        is_shaking = bk["note"] in mistakes_notes_map
        
        rect = get_black_key_rect(bk["white_index"], sw, keyboard_y, keyboard_h)
        
        # Shake effect offset
        if is_shaking:
            rect.x += math.sin(pr.get_time() * 50) * 4
            
        color_top = pr.Color(44, 44, 44, 255) # Sleek charcoal top
        color_bottom = pr.Color(18, 18, 18, 255) # Dark black bottom
        border_col = pr.Color(0, 0, 0, 255)
        b_offset = 6
        
        if is_shaking:
            color_top = pr.Color(248, 113, 113, 255) # Red mistake top
            color_bottom = pr.Color(220, 38, 38, 255) # Red mistake bottom
            border_col = pr.Color(153, 27, 27, 255)
            b_offset = 2
        elif is_active:
            color_top = pr.Color(251, 191, 36, 255) # Amber active top
            color_bottom = pr.Color(217, 119, 6, 255) # Amber active bottom
            border_col = pr.Color(180, 83, 9, 255)
            b_offset = 2
        elif is_rainbow:
            color_top = is_rainbow[1]
            color_bottom = pr.Color(int(color_top.r*0.7), int(color_top.g*0.7), int(color_top.b*0.7), 255)
            border_col = pr.Color(int(color_top.r*0.5), int(color_top.g*0.5), int(color_top.b*0.5), 255)
            b_offset = 2
            
        # Draw black border background (very fast and batched)
        pr.draw_rectangle(int(rect.x), int(rect.y), int(rect.width), int(rect.height), pr.Color(10, 10, 10, 255))
        
        # Sinking Y-offset
        y_offset = int(4 * ui_scale) if (is_active or is_shaking or is_rainbow) else 0

        border_thickness = 2
        # Draw Key body
        pr.draw_rectangle_gradient_v(int(rect.x + border_thickness), int(rect.y + y_offset), int(rect.width - 2 * border_thickness), int(rect.height - b_offset - border_thickness - y_offset), color_top, color_bottom)
        # Draw Key bottom border
        pr.draw_rectangle_gradient_v(int(rect.x + border_thickness), int(rect.y + rect.height - b_offset - border_thickness), int(rect.width - 2 * border_thickness), b_offset, border_col, pr.Color(20, 20, 20, 255))
        
        # Premium 3D bevel top line highlight (shifted down by y_offset)
        pr.draw_line(int(rect.x + border_thickness), int(rect.y + y_offset), int(rect.x + rect.width - border_thickness), int(rect.y + y_offset), pr.Color(255, 255, 255, 30))
        
        # Draw key label (Premium Typography)
        font_sz = max(7, int(9 * ui_scale))
        lbl = bk["note"]
        lbl_w = measure_text_modern_width(lbl, font_sz)
        
        if is_shaking:
            lbl_color = pr.WHITE
        elif is_active:
            lbl_color = pr.Color(15, 23, 42, 255)
        else:
            lbl_color = pr.Color(200, 200, 200, 255)
            
        draw_text_modern(lbl, int(rect.x + rect.width // 2 - lbl_w // 2), int(rect.y + rect.height - 20 * ui_scale + y_offset), font_sz, lbl_color)
        

        
        # Mistake floating oops label
        if oops_label_timer > 0 and oops_label_note == bk["note"]:
            lbl_oops = "Oops!"
            oops_sz = max(10, int(13 * ui_scale))
            oops_w = measure_text_modern_width(lbl_oops, oops_sz)
            float_dist = (0.75 - oops_label_timer) * 80 * ui_scale
            oops_y = int(rect.y + y_offset - float_dist)
            cap_w = oops_w + int(16 * ui_scale)
            cap_h = oops_sz + int(8 * ui_scale)
            cap_x = int(rect.x + rect.width / 2 - cap_w / 2)
            cap_y = oops_y - cap_h // 2
            alpha = int((oops_label_timer / 0.75) * 255)
            pr.draw_rectangle_rounded(pr.Rectangle(cap_x, cap_y, cap_w, cap_h), 0.5, 4, pr.Color(220, 38, 38, alpha))
            pr.draw_rectangle_rounded_lines(pr.Rectangle(cap_x, cap_y, cap_w, cap_h), 0.5, 4, pr.Color(153, 27, 27, int(alpha * 0.8)))
            draw_text_modern(lbl_oops, cap_x + cap_w // 2 - oops_w // 2, cap_y + cap_h // 2 - oops_sz // 2, oops_sz, pr.Color(255, 255, 255, alpha))

    # --- Draw Floating Particles ---
    for p in list(particles):
        p.x += p.vx
        p.y += p.vy
        p.alpha -= 0.025
        if p.alpha <= 0:
            particles.remove(p)
        else:
            col_hex = p.color
            p_color = pr.Color(14, 165, 233, int(p.alpha * 255)) if col_hex == "#0ea5e9" else pr.Color(245, 158, 11, int(p.alpha * 255))
            pr.draw_circle(int(p.x), int(p.y), p.size, p_color)

    # --- Draw Top Panel Header (Premium sharp card with 90° corners, full-width) ---
    pr.draw_rectangle(0, 0, sw, top_height, pr.WHITE)
    pr.draw_line(0, top_height, sw, top_height, pr.Color(200, 200, 200, 255))
    
    # Left Logo & Info Scale calculations
    title_sz = int(24 * ui_scale)
    desc_sz = int(11 * ui_scale)
    title_w = measure_text_modern_width("GPiano", title_sz)
    
    # Check if stats text is needed
    has_stats = (selected_song_id != "none")
    if has_stats:
        stats_text = f"Puntos: {score}  |  Fallos: {mistake_count}"
        stats_sz = int(18 * ui_scale)
        stats_w = measure_text_modern_width(stats_text, stats_sz)
        stats_x = sw - stats_w - 25
        stats_y = int(top_height / 2 - stats_sz / 2)

    # Responsive Visibility Rules
    show_subtitle = True
    show_title = True
    
    # Hide subtitle if space is tight
    if sw < 1100 or (has_stats and sw < 1200):
        show_subtitle = False
    
    # Hide title as well if space is extremely narrow
    if sw < 800 or (has_stats and sw < 900):
        show_title = False

    # Draw Left block (Title/Subtitle)
    if show_title:
        draw_text_modern("GPiano", 25, int(top_height/2 - title_sz), title_sz, pr.Color(20, 20, 20, 255))
        if show_subtitle:
            draw_text_modern("Aprende tocando tus canciones favoritas", 25, int(top_height/2 + 2), desc_sz, pr.Color(100, 100, 100, 255))
        else:
            # Center title vertically if there is no subtitle
            draw_text_modern("GPiano", 25, int(top_height/2 - title_sz/2), title_sz, pr.Color(20, 20, 20, 255))

    # Draw Logo centered both horizontally and vertically in the header (Absolute Center)
    if logo_texture:
        logo_aspect = logo_texture.width / logo_texture.height
        target_h = int(top_height * 0.75)
        target_w = int(target_h * logo_aspect)
        
        # Absolute center horizontally and vertically
        logo_x = sw // 2 - target_w // 2
        logo_y = top_height // 2 - target_h // 2
        
        source_rect = pr.Rectangle(0, 0, logo_texture.width, logo_texture.height)
        dest_rect = pr.Rectangle(logo_x, logo_y, target_w, target_h)
        origin = pr.Vector2(0, 0)
        pr.draw_texture_pro(logo_texture, source_rect, dest_rect, origin, 0.0, pr.WHITE)
        
    # Draw Stats Text (No container, larger size)
    if has_stats:
        draw_text_modern(stats_text, stats_x, stats_y, stats_sz, pr.Color(30, 30, 30, 255))
        
    # Draw Exit Countdown in Free Play Mode if keys are held, otherwise draw the instructions hint
    if app_state == STATE_FREE_PLAY:
        if free_play_exit_timer > 0.0:
            timer_text = f"Regresando al menú en: {max(1, 5 - int(free_play_exit_timer))}s..."
            timer_sz = int(22 * ui_scale)
            timer_w = measure_text_modern_width(timer_text, timer_sz)
            
            # Calculate pill dimensions with scaling padding
            pill_w = timer_w + int(24 * ui_scale)
            pill_h = timer_sz + int(12 * ui_scale)
            
            # Position the pill with a margin of 25 pixels from the screen edge (matches GPiano's left margin)
            pill_x = sw - pill_w - 25
            pill_y = int(top_height / 2 - pill_h / 2)
            
            # Center the text inside the pill
            timer_x = pill_x + int(12 * ui_scale)
            timer_y = int(top_height / 2 - timer_sz / 2)
            
            pr.draw_rectangle_rounded(pr.Rectangle(pill_x, pill_y, pill_w, pill_h), 0.4, 4, pr.Color(254, 226, 226, 255))
            pr.draw_rectangle_rounded_lines(pr.Rectangle(pill_x, pill_y, pill_w, pill_h), 0.4, 4, pr.Color(248, 113, 113, 255))
            draw_text_modern(timer_text, timer_x, timer_y, timer_sz, pr.Color(220, 38, 38, 255))
        else:
            hint_text = "Presiona C3 + A#5 para regresar"
            hint_sz = int(14 * ui_scale)
            hint_w = measure_text_modern_width(hint_text, hint_sz)
            
            # Calculate pill dimensions with scaling padding
            pill_w = hint_w + int(24 * ui_scale)
            pill_h = hint_sz + int(12 * ui_scale)
            
            # Position the pill with a margin of 25 pixels from the screen edge
            pill_x = sw - pill_w - 25
            pill_y = int(top_height / 2 - pill_h / 2)
            
            # Center the text inside the pill
            hint_x = pill_x + int(12 * ui_scale)
            hint_y = int(top_height / 2 - hint_sz / 2)
            
            # Slate premium pill
            pr.draw_rectangle_rounded(pr.Rectangle(pill_x, pill_y, pill_w, pill_h), 0.4, 4, pr.Color(241, 245, 249, 255)) # Slate 100
            pr.draw_rectangle_rounded_lines(pr.Rectangle(pill_x, pill_y, pill_w, pill_h), 0.4, 4, pr.Color(203, 213, 225, 255)) # Slate 300
            
            # Text inside the pill (Slate 600)
            draw_text_modern(hint_text, hint_x, hint_y, hint_sz, pr.Color(71, 85, 105, 255))

    # --- Draw Celebration Overlay & Modal ---
    if show_celebration and show_modal:
        # Translucent white backdrop
        pr.draw_rectangle(0, 0, sw, sh, pr.Color(255, 255, 255, 215)) # 85% opacity
        
        # Modal card dimensions
        modal_w = int(360 * ui_scale)
        modal_h = int(430 * ui_scale)
        modal_x = sw // 2 - modal_w // 2
        modal_y = sh // 2 - modal_h // 2
        
        modal_rect = pr.Rectangle(modal_x, modal_y, modal_w, modal_h)
        
        # Premium black outer shadow
        for glow in range(1, 15):
            glow_rect = pr.Rectangle(modal_x - glow, modal_y - glow, modal_w + glow * 2, modal_h + glow * 2)
            pr.draw_rectangle_rounded_lines(glow_rect, 0.1, 4, pr.Color(0, 0, 0, int((15 - glow) * 6.0)))
            
        # Draw modal card body (Clean white design)
        pr.draw_rectangle_rounded(modal_rect, 0.1, 4, pr.WHITE)
        pr.draw_rectangle_rounded_lines(modal_rect, 0.1, 4, pr.Color(200, 200, 200, 255))
        
        # Draw Vector Trophy (Animated bouncing)
        bounce_offset = int(math.sin(pr.get_time() * 4) * 6 * ui_scale)
        trophy_cy = modal_y + int(65 * ui_scale) + bounce_offset
        draw_vector_trophy(sw // 2, trophy_cy, 1.25 * ui_scale)
        
        # Title text (Premium Typography)
        title_txt = "¡Canción Completada!"
        title_sz = int(22 * ui_scale)
        title_w = measure_text_modern_width(title_txt, title_sz)
        draw_text_modern(title_txt, sw // 2 - title_w // 2, modal_y + int(135 * ui_scale), title_sz, pr.BLACK)
        
        sub_txt = "Has finalizado la lección con éxito"
        sub_sz = int(12 * ui_scale)
        sub_w = measure_text_modern_width(sub_txt, sub_sz)
        draw_text_modern(sub_txt, sw // 2 - sub_w // 2, modal_y + int(165 * ui_scale), sub_sz, pr.Color(100, 100, 100, 255))
        
        # Draw Rating Stars
        current_song = next((s for s in SONGS if s["id"] == selected_song_id), None)
        num_stars = 1
        if current_song:
            accuracy = max(0, 100 - int((mistake_count / len(current_song["notes"])) * 100))
            if accuracy >= 95 and mistake_count == 0:
                num_stars = 3
            elif accuracy >= 80:
                num_stars = 2
                
        # Draw vector stars dynamically with pulse animations
        star_r_out = int(16 * ui_scale)
        star_r_in = int(7 * ui_scale)
        star_spacing = int(40 * ui_scale)
        star_start_x = sw // 2 - ((num_stars - 1) * star_spacing) // 2
        for s_idx in range(num_stars):
            cx = star_start_x + s_idx * star_spacing
            cy = modal_y + int(200 * ui_scale)
            pulsing = math.sin(pr.get_time() * 5 + s_idx * 1.5) * 2 * ui_scale
            draw_star(cx, cy, star_r_out + pulsing, star_r_in + pulsing / 2, pr.Color(245, 158, 11, 255))
            
        # Stats breakdown container
        breakdown_y = modal_y + int(235 * ui_scale)
        breakdown_w = modal_w - int(40 * ui_scale)
        breakdown_h = int(110 * ui_scale)
        breakdown_rect = pr.Rectangle(modal_x + int(20 * ui_scale), breakdown_y, breakdown_w, breakdown_h)
        
        pr.draw_rectangle_rounded(breakdown_rect, 0.15, 4, pr.Color(245, 245, 245, 255))
        pr.draw_rectangle_rounded_lines(breakdown_rect, 0.15, 4, pr.Color(220, 220, 220, 255))
        
        # Details stats texts (Enlarged size, high contrast)
        text_sz = int(16 * ui_scale)
        text_y = breakdown_y + int(12 * ui_scale)
        line_spacing = int(32 * ui_scale)
        
        draw_text_modern("Puntuación Final:", int(breakdown_rect.x + 15 * ui_scale), text_y, text_sz, pr.Color(80, 80, 80, 255))
        scr_lbl = str(score)
        draw_text_modern(scr_lbl, int(breakdown_rect.x + breakdown_w - measure_text_modern_width(scr_lbl, text_sz) - 15 * ui_scale), text_y, text_sz, pr.BLACK)
        
        draw_text_modern("Combo Máximo:", int(breakdown_rect.x + 15 * ui_scale), text_y + line_spacing, text_sz, pr.Color(80, 80, 80, 255))
        cmb_lbl = str(max_combo)
        draw_text_modern(cmb_lbl, int(breakdown_rect.x + breakdown_w - measure_text_modern_width(cmb_lbl, text_sz) - 15 * ui_scale), text_y + line_spacing, text_sz, pr.Color(2, 132, 199, 255))
        
        draw_text_modern("Total de Fallos:", int(breakdown_rect.x + 15 * ui_scale), text_y + line_spacing * 2, text_sz, pr.Color(80, 80, 80, 255))
        mst_lbl = str(mistake_count)
        draw_text_modern(mst_lbl, int(breakdown_rect.x + breakdown_w - measure_text_modern_width(mst_lbl, text_sz) - 15 * ui_scale), text_y + line_spacing * 2, text_sz, pr.Color(220, 38, 38, 255))
        
        # Aceptar Button
        btn_y = modal_y + int(365 * ui_scale)
        btn_w = modal_w - int(40 * ui_scale)
        btn_h = int(46 * ui_scale)
        btn_rect = pr.Rectangle(modal_x + int(20 * ui_scale), btn_y, btn_w, btn_h)
        
        btn_hovered = pr.check_collision_point_rec(m_pos, btn_rect)
        btn_col = pr.Color(40, 40, 40, 255) if btn_hovered else pr.BLACK
        
        pr.draw_rectangle_rounded(btn_rect, 0.25, 4, btn_col)
        
        btn_txt = "Aceptar"
        btn_txt_sz = int(14 * ui_scale)
        btn_txt_w = measure_text_modern_width(btn_txt, btn_txt_sz)
        draw_text_modern(btn_txt, int(btn_rect.x + btn_w // 2 - btn_txt_w // 2), int(btn_rect.y + btn_h // 2 - btn_txt_sz // 2), btn_txt_sz, pr.WHITE)
        
        if btn_hovered and pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT):
            close_celebration_modal()

    # --- Draw Countdown Overlay ---
    if in_countdown:
        # Translucent white backdrop (85% opacity)
        pr.draw_rectangle(0, 0, sw, sh, pr.Color(255, 255, 255, 215))
        
        # Calculate seconds left
        seconds_left = int(math.ceil(countdown_timer))
        if seconds_left < 1:
            seconds_left = 1
        elif seconds_left > 3:
            seconds_left = 3
            
        # Select active texture based on seconds left
        active_tex = None
        if seconds_left == 3:
            active_tex = num3_texture
        elif seconds_left == 2:
            active_tex = num2_texture
        else:
            active_tex = num1_texture
            
        # Pulse animation using the fractional part of countdown_timer
        fractional_part = countdown_timer - math.floor(countdown_timer)
        pulse_factor = 1.0 + fractional_part * 0.4
        
        target_h = int(180 * pulse_factor * ui_scale) # base height of 180px
        
        if active_tex and active_tex.id > 0:
            # Draw texture centered
            aspect = active_tex.width / active_tex.height
            dest_w = target_h * aspect
            dest_h = target_h
            
            source_rec = pr.Rectangle(0, 0, active_tex.width, active_tex.height)
            dest_rec = pr.Rectangle(sw // 2, sh // 2, dest_w, dest_h)
            origin = pr.Vector2(dest_w / 2, dest_h / 2)
            
            pr.draw_texture_pro(active_tex, source_rec, dest_rec, origin, 0.0, pr.WHITE)
        else:
            # Fallback to text drawing
            countdown_text = str(seconds_left)
            text_sz = int(120 * pulse_factor * ui_scale)
            text_w = measure_text_modern_width(countdown_text, text_sz)
            draw_text_modern(
                countdown_text,
                sw // 2 - text_w // 2,
                sh // 2 - text_sz // 2,
                text_sz,
                pr.Color(20, 20, 20, 255)
            )

    pr.end_drawing()

# Clean up resources on exit
if fs_synth:
    fs_synth.delete()

if click_sound:
    pr.unload_sound(click_sound)

if select_sound:
    pr.unload_sound(select_sound)

if custom_font:
    pr.unload_font(custom_font)


if logo_texture:
    pr.unload_texture(logo_texture)

if num1_texture:
    pr.unload_texture(num1_texture)
if num2_texture:
    pr.unload_texture(num2_texture)
if num3_texture:
    pr.unload_texture(num3_texture)
    
pr.close_audio_device()
pr.close_window()
