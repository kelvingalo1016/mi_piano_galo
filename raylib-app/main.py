import os
import math
import pyray as pr

# Initialize Raylib Window
pr.set_config_flags(pr.FLAG_WINDOW_RESIZABLE)
pr.init_window(1024, 600, "Mi Piano Galo")
pr.set_target_fps(60)

# Initialize Audio
pr.init_audio_device()

# Resolve audio folder relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(SCRIPT_DIR, "..", "public", "audio", "piano")

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

# Load sound sampler step-by-step
loaded_sounds = {}
loading_progress = 0

def load_samples_tick():
    global loading_progress
    if loading_progress >= len(PIANO_KEYS):
        return True
    
    key_data = PIANO_KEYS[loading_progress]
    note = key_data["note"]
    
    closest_sample, semitone_diff = get_closest_sample(note)
    filename = closest_sample.replace("#", "s") + ".mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    
    if os.path.exists(filepath):
        sound = pr.load_sound(filepath)
        pitch = 2.0 ** (semitone_diff / 12.0)
        pr.set_sound_pitch(sound, pitch)
        loaded_sounds[note] = sound
    else:
        print(f"Sample file not found: {filepath}")
        
    loading_progress += 1
    return loading_progress >= len(PIANO_KEYS)

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
fireworks = []

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
    w_width = screen_w / 21
    return pr.Rectangle(index * w_width, kb_y, w_width - 1, kb_h)

def get_black_key_rect(preceding_index, screen_w, kb_y, kb_h):
    w_width = screen_w / 21
    b_width = w_width * 0.6
    b_height = kb_h * 0.6
    left = (preceding_index + 1) * w_width - b_width / 2
    return pr.Rectangle(left, kb_y, b_width, b_height)

# Note key coordinates finder
def get_key_x(note_name, canvas_width):
    white_keys_list = [k for k in PIANO_KEYS if not k["is_black"]]
    total_w_keys = len(white_keys_list)
    w_width = canvas_width / total_w_keys
    b_width = w_width * 0.6

    # Find the target key
    key_info = None
    for k in PIANO_KEYS:
        if k["note"] == note_name:
            key_info = k
            break
            
    if not key_info:
        return 0, False, 10

    if not key_info["is_black"]:
        idx = white_keys_list.index(key_info)
        return int(idx * w_width + w_width / 2), False, int(w_width)
    else:
        # Preceding white key placement
        target_idx = PIANO_KEYS.index(key_info)
        preceding_white_note = PIANO_KEYS[target_idx - 1]["note"]
        idx = white_keys_list.index(next(k for k in white_keys_list if k["note"] == preceding_white_note))
        return int((idx + 1) * w_width), True, int(b_width)

# Handle user key hits
def handle_play_note(note):
    active_notes.add(note)
    
    # Sound trigger
    if note in loaded_sounds:
        pr.play_sound(loaded_sounds[note])
        
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
                    # Only register error for notes near active timing window
                    if next_note["time"] <= playback_time + 1.0:
                        mistake_count += 1
                        combo = 0
                        trigger_mistake(note)

def handle_stop_note(note):
    active_notes.discard(note)

def trigger_mistake(note):
    mistakes_notes_map[note] = 0.3 # duration of shake
    
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
        pr.Color(248, 113, 113, 255),  # Red 400
        pr.Color(251, 146, 60, 255),   # Orange 400
        pr.Color(251, 191, 36, 255),   # Amber 400
        pr.Color(52, 211, 153, 255),   # Emerald 400
        pr.Color(56, 189, 248, 255),   # Sky 400
        pr.Color(167, 139, 250, 255),  # Violet 400
        pr.Color(244, 114, 182, 255)   # Pink 400
    ]
    
    now = pr.get_time()
    for index, key in enumerate(PIANO_KEYS):
        trigger_time = now + index * 0.04
        color = colors[index % len(colors)]
        scheduled_rainbow.append((trigger_time, key["note"], color))

scheduled_rainbow = []
active_rainbow_keys = {}

def close_celebration_modal():
    global show_celebration, show_modal, selected_song_id, is_playing
    show_celebration = False
    show_modal = False
    active_rainbow_keys.clear()
    selected_song_id = "none"
    is_playing = False
    handle_song_change("none")

def stop_song_playback():
    global is_playing
    is_playing = False
    guide_notes.clear()
    active_notes.clear()

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
    
    if song_id == "none":
        is_playing = False
    else:
        is_playing = True
        playback_time = 0.0
        
        # Calculate initial guide notes
        song = next((s for s in SONGS if s["id"] == song_id), None)
        if song:
            update_guide_notes(song)

# Star rendering polygon math
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

# GUI States
song_select_open = False
song_select_rect = pr.Rectangle(0, 0, 0, 0)

# Touch/Mouse held tracking
prev_pressed_notes = set()

# Main Application Loop
while not pr.window_should_close():
    delta_time = pr.get_frame_time()
    
    # ------------------ LOADING PHASE ------------------
    if loading_progress < len(PIANO_KEYS):
        load_samples_tick()
        
        pr.begin_drawing()
        pr.clear_background(pr.Color(10, 10, 10, 255))
        
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()
        
        # Draw title
        pr.draw_text("MI PIANO GALO", sw // 2 - pr.measure_text("MI PIANO GALO", 40) // 2, sh // 2 - 80, 40, pr.WHITE)
        
        # Draw loading bar
        bar_w = 300
        bar_h = 10
        bar_x = sw // 2 - bar_w // 2
        bar_y = sh // 2
        
        pr.draw_rectangle_rounded(pr.Rectangle(bar_x, bar_y, bar_w, bar_h), 1.0, 4, pr.Color(38, 38, 38, 255))
        progress_w = int(bar_w * (loading_progress / len(PIANO_KEYS)))
        pr.draw_rectangle_rounded(pr.Rectangle(bar_x, bar_y, progress_w, bar_h), 1.0, 4, pr.Color(14, 165, 233, 255))
        
        pr.draw_text("Cargando muestras de sonido...", sw // 2 - pr.measure_text("Cargando muestras de sonido...", 16) // 2, sh // 2 + 30, 16, pr.Color(163, 163, 163, 255))
        pr.end_drawing()
        continue
        
    # ------------------ GAMEPLAY PHASE ------------------
    
    # 1. Update Fanfare and Rainbow Cascades (Celebration)
    now_time = pr.get_time()
    
    # Ascending arpeggio scheduled notes playback
    for item in list(scheduled_fanfare):
        trigger_time, note, duration = item
        if now_time >= trigger_time:
            if note in loaded_sounds:
                pr.play_sound(loaded_sounds[note])
            scheduled_releases.append((now_time + duration, note))
            scheduled_fanfare.remove(item)
            
    # Scheduled arpeggio releases
    for item in list(scheduled_releases):
        release_time, note = item
        if now_time >= release_time:
            # We don't strictly need to trigger release since fanfare sounds decay naturally, but we clear it
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

    # 2. Practice/Solo Game Mode Loop
    if is_playing and selected_song_id != "none":
        current_song = next((s for s in SONGS if s["id"] == selected_song_id), None)
        if current_song:
            next_note = next((n for n in current_song["notes"] if f"{n['time']}-{n['note']}" not in user_pressed_notes), None)
            next_time = playback_time + delta_time
            
            if not next_note:
                song_length = max(n["time"] + n["duration"] for n in current_song["notes"]) + 1.0
                if playback_time >= song_length:
                    # Song finished!
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

    # Update modal timer
    if show_celebration and not show_modal:
        modal_animation_timer += delta_time
        if modal_animation_timer >= 1.5:
            show_modal = True

    # Exit celebration if modal is open and key is pressed
    if show_celebration and show_modal:
        if pr.get_key_pressed() != 0:
            close_celebration_modal()

    # 3. Process pointer and QWERTY keyboard inputs
    sw = pr.get_screen_width()
    sh = pr.get_screen_height()
    
    # Layout Coordinates
    top_height = 80
    keyboard_h = int(sh * 0.35)
    visualizer_h = sh - top_height - keyboard_h - 30
    visualizer_y = top_height + 15
    keyboard_y = sh - keyboard_h - 10
    
    # Gather Touch + Mouse positions
    active_points = []
    if pr.is_mouse_button_down(pr.MOUSE_BUTTON_LEFT):
        # Prevent mouse playing if clicking on song select dropdown
        m_pos = pr.get_mouse_position()
        if not (song_select_open and pr.check_collision_point_rec(m_pos, pr.Rectangle(song_select_rect.x, song_select_rect.y, song_select_rect.width, song_select_rect.height + len(SONGS)*40))):
            if not pr.check_collision_point_rec(m_pos, song_select_rect) and not (show_celebration and show_modal):
                active_points.append(m_pos)
                
    for t in range(pr.get_touch_point_count()):
        active_points.append(pr.get_touch_position(t))
        
    # Check notes pressed by mouse/touch
    pressed_by_touch = set()
    if not (show_celebration and show_modal):
        for pt in active_points:
            # Check black keys first (overlay z-order)
            hit_black = False
            for bk in black_keys:
                rect = get_black_key_rect(bk["white_index"], sw, keyboard_y, keyboard_h)
                if pr.check_collision_point_rec(pt, rect):
                    pressed_by_touch.add(bk["note"])
                    hit_black = True
                    break
            if not hit_black:
                # Check white keys
                for index, wk in enumerate(white_keys):
                    rect = get_white_key_rect(index, sw, keyboard_y, keyboard_h)
                    if pr.check_collision_point_rec(pt, rect):
                        pressed_by_touch.add(wk["note"])
                        break
                        
    # Compare with previous frame to trigger attacks/releases
    for note in pressed_by_touch:
        if note not in prev_pressed_notes:
            handle_play_note(note)
            
    for note in prev_pressed_notes:
        if note not in pressed_by_touch:
            handle_stop_note(note)
            
    prev_pressed_notes = pressed_by_touch.copy()

    # Read QWERTY keyboard mappings
    if not (show_celebration and show_modal):
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
    pr.clear_background(pr.Color(10, 10, 10, 255)) # Dark background

    # --- Draw Falling Notes Visualizer Area ---
    pr.draw_rectangle(0, visualizer_y, sw, visualizer_h, pr.Color(10, 10, 10, 255))
    
    # White key vertical guide lines
    w_width = sw / 21
    for i in range(1, 21):
        pr.draw_line(int(i * w_width), visualizer_y, int(i * w_width), visualizer_y + visualizer_h, pr.Color(38, 38, 38, 255))
        
    # Draw guides and falling blocks if a song is playing
    if is_playing and selected_song_id != "none":
        current_song = next((s for s in SONGS if s["id"] == selected_song_id), None)
        if current_song:
            time_window = 3.0
            
            # Active note columns backglow
            for note in current_song["notes"]:
                is_active = playback_time >= note["time"] and playback_time <= note["time"] + note["duration"]
                if is_active:
                    x_coord, is_b, kw = get_key_x(note["note"], sw)
                    col = pr.Color(217, 119, 6, 20) if is_b else pr.Color(2, 132, 199, 20)
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
                    
                    # Rounded rectangle drawing
                    rect = pr.Rectangle(x_coord - kw // 2, block_y, kw, block_h)
                    color = pr.Color(245, 158, 11, 255) if is_b else pr.Color(14, 165, 233, 255) # Orange or Blue
                    if not is_active:
                        color.a = 190 # 75% opacity
                    pr.draw_rectangle_rounded(rect, 0.25, 4, color)
                    
                    # Highlight outline border for active note hitting
                    if is_active:
                        pr.draw_rectangle_rounded_lines(rect, 0.25, 4, pr.WHITE)
                        
                    # Display note name inside block
                    if block_h > 15:
                        label = note["note"].replace("#", "s")
                        text_col = pr.Color(28, 25, 23, 255) if is_b else pr.WHITE
                        font_sz = 10
                        text_w = pr.measure_text(label, font_sz)
                        pr.draw_text(label, x_coord - text_w // 2, block_y + block_h // 2 - font_sz // 2, font_sz, text_col)

    # Draw target line at bottom of visualizer
    pr.draw_line_ex(pr.Vector2(0, visualizer_y + visualizer_h), pr.Vector2(sw, visualizer_y + visualizer_h), 3, pr.Color(64, 64, 64, 255))

    # --- Draw Keyboard Area ---
    # Layer 1: White Keys
    for index, wk in enumerate(white_keys):
        is_active = wk["note"] in active_notes or wk["note"] in guide_notes
        is_rainbow = active_rainbow_keys.get(wk["note"])
        is_shaking = wk["note"] in mistakes_notes_map
        
        rect = get_white_key_rect(index, sw, keyboard_y, keyboard_h)
        
        # Shake effect offset
        if is_shaking:
            rect.x += math.sin(pr.get_time() * 50) * 4
            
        color = pr.Color(245, 245, 245, 255) # Default white
        border_col = pr.Color(212, 212, 212, 255) # Gray
        b_offset = 6
        
        if is_shaking:
            color = pr.Color(239, 68, 68, 255) # Red mistake
            border_col = pr.Color(185, 28, 28, 255)
            b_offset = 2
        elif is_active:
            color = pr.Color(14, 165, 233, 255) # Blue active
            border_col = pr.Color(3, 105, 161, 255)
            b_offset = 2
        elif is_rainbow:
            color = is_rainbow[1]
            border_col = pr.Color(int(color.r*0.7), int(color.g*0.7), int(color.b*0.7), 255)
            b_offset = 2
            
        # Draw Key body
        pr.draw_rectangle_rounded(pr.Rectangle(rect.x, rect.y, rect.width, rect.height - b_offset), 0.15, 4, color)
        # Draw Key bottom border (simulate 3D depth)
        pr.draw_rectangle_rounded(pr.Rectangle(rect.x, rect.y + rect.height - b_offset, rect.width, b_offset), 0.15, 4, border_col)
        
        # Left/Right border dividers
        pr.draw_line(int(rect.x), int(rect.y), int(rect.x), int(rect.y + rect.height), pr.Color(115, 115, 115, 255))
        
        # Draw key label
        font_sz = 12 if sw > 800 else 10
        lbl = wk["note"]
        lbl_w = pr.measure_text(lbl, font_sz)
        lbl_color = pr.WHITE if is_active or is_shaking else pr.Color(115, 115, 115, 255)
        pr.draw_text(lbl, int(rect.x + rect.width // 2 - lbl_w // 2), int(rect.y + rect.height - 25), font_sz, lbl_color)
        
        # Mistake floating oops label
        if oops_label_timer > 0 and oops_label_note == wk["note"]:
            lbl_oops = "Oops!"
            oops_w = pr.measure_text(lbl_oops, 14)
            oops_y = int(rect.y - (0.75 - oops_label_timer) * 60)
            pr.draw_text(lbl_oops, int(rect.x + rect.width // 2 - oops_w // 2), oops_y, 14, pr.Color(239, 68, 68, 255))

    # Layer 2: Black Keys
    for bk in black_keys:
        is_active = bk["note"] in active_notes or bk["note"] in guide_notes
        is_rainbow = active_rainbow_keys.get(bk["note"])
        is_shaking = bk["note"] in mistakes_notes_map
        
        rect = get_black_key_rect(bk["white_index"], sw, keyboard_y, keyboard_h)
        
        # Shake effect offset
        if is_shaking:
            rect.x += math.sin(pr.get_time() * 50) * 4
            
        color = pr.Color(20, 20, 20, 255) # Default black
        border_col = pr.Color(0, 0, 0, 255)
        b_offset = 6
        
        if is_shaking:
            color = pr.Color(239, 68, 68, 255) # Red mistake
            border_col = pr.Color(185, 28, 28, 255)
            b_offset = 2
        elif is_active:
            color = pr.Color(245, 158, 11, 255) # Amber active
            border_col = pr.Color(180, 83, 9, 255)
            b_offset = 2
        elif is_rainbow:
            color = is_rainbow[1]
            border_col = pr.Color(int(color.r*0.7), int(color.g*0.7), int(color.b*0.7), 255)
            b_offset = 2
            
        # Draw Key body
        pr.draw_rectangle_rounded(pr.Rectangle(rect.x - rect.width // 2, rect.y, rect.width, rect.height - b_offset), 0.15, 4, color)
        # Draw Key bottom border
        pr.draw_rectangle_rounded(pr.Rectangle(rect.x - rect.width // 2, rect.y + rect.height - b_offset, rect.width, b_offset), 0.15, 4, border_col)
        
        # Draw key label
        font_sz = 8
        lbl = bk["note"]
        lbl_w = pr.measure_text(lbl, font_sz)
        lbl_color = pr.WHITE if is_active or is_shaking else pr.Color(163, 163, 163, 255)
        pr.draw_text(lbl, int(rect.x - lbl_w // 2), int(rect.y + rect.height - 18), font_sz, lbl_color)
        
        # Mistake floating oops label
        if oops_label_timer > 0 and oops_label_note == bk["note"]:
            lbl_oops = "Oops!"
            oops_w = pr.measure_text(lbl_oops, 14)
            oops_y = int(rect.y - (0.75 - oops_label_timer) * 60)
            pr.draw_text(lbl_oops, int(rect.x - oops_w // 2), oops_y, 14, pr.Color(239, 68, 68, 255))

    # --- Draw Floating Particles ---
    for p in list(particles):
        p.x += p.vx
        p.y += p.vy
        p.alpha -= 0.025
        if p.alpha <= 0:
            particles.remove(p)
        else:
            col_hex = p.color
            # Simple conversion of string color to pr.Color
            p_color = pr.Color(14, 165, 233, int(p.alpha * 255)) if col_hex == "#0ea5e9" else pr.Color(245, 158, 11, int(p.alpha * 255))
            pr.draw_circle(int(p.x), int(p.y), p.size, p_color)

    # --- Draw Top Panel Header ---
    pr.draw_rectangle_rounded(pr.Rectangle(10, 10, sw - 20, top_height), 0.25, 4, pr.Color(23, 23, 23, 255))
    pr.draw_rectangle_rounded_lines(pr.Rectangle(10, 10, sw - 20, top_height), 0.25, 4, pr.Color(38, 38, 38, 255))
    
    # Left Logo & Info
    pr.draw_text("🎹", 25, 23, 28, pr.WHITE)
    pr.draw_text("Mi Piano Galo", 65, 22, 18, pr.WHITE)
    pr.draw_text("Aprende tocando tus canciones favoritas", 65, 45, 11, pr.Color(163, 163, 163, 255))

    # Stats Capsule (in practice mode)
    if selected_song_id != "none":
        stats_x = sw - 320
        stats_y = 25
        stats_w = 300
        stats_h = 36
        pr.draw_rectangle_rounded(pr.Rectangle(stats_x, stats_y, stats_w, stats_h), 0.3, 4, pr.Color(10, 10, 10, 255))
        pr.draw_rectangle_rounded_lines(pr.Rectangle(stats_x, stats_y, stats_w, stats_h), 0.3, 4, pr.Color(38, 38, 38, 255))
        
        stats_text = f"Puntos: {score}  |  Combo: {combo} (Máx: {max_combo})  |  Fallos: {mistake_count}"
        font_sz = 10
        text_w = pr.measure_text(stats_text, font_sz)
        pr.draw_text(stats_text, stats_x + stats_w // 2 - text_w // 2, stats_y + stats_h // 2 - font_sz // 2, font_sz, pr.WHITE)

    # Song Select Dropdown Menu
    select_label = "Canción: "
    select_x = sw - 540 if selected_song_id != "none" else sw - 240
    select_y = 23
    
    pr.draw_text(select_label, select_x, select_y + 10, 12, pr.Color(163, 163, 163, 255))
    
    # Draw select box
    select_box_w = 150
    select_box_h = 32
    select_box_x = select_x + pr.measure_text(select_label, 12) + 5
    song_select_rect = pr.Rectangle(select_box_x, select_y, select_box_w, select_box_h)
    
    pr.draw_rectangle_rounded(song_select_rect, 0.3, 4, pr.Color(10, 10, 10, 255))
    pr.draw_rectangle_rounded_lines(song_select_rect, 0.3, 4, pr.Color(38, 38, 38, 255))
    
    # Display selected song name
    sel_song_title = "Libre (Ninguna)"
    if selected_song_id == "twinkle":
        sel_song_title = "Estrellita"
    elif selected_song_id == "joy":
        sel_song_title = "Himno a la Alegría"
    elif selected_song_id == "birthday":
        sel_song_title = "Cumpleaños"
        
    pr.draw_text(sel_song_title, int(song_select_rect.x + 10), int(song_select_rect.y + 10), 11, pr.WHITE)
    pr.draw_text("v", int(song_select_rect.x + select_box_w - 20), int(song_select_rect.y + 10), 11, pr.Color(163, 163, 163, 255))
    
    # Check click on select box
    m_pos = pr.get_mouse_position()
    if pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT):
        if pr.check_collision_point_rec(m_pos, song_select_rect):
            song_select_open = not song_select_open
        elif song_select_open:
            # Check options selection
            options = ["none", "twinkle", "joy", "birthday"]
            for i, opt in enumerate(options):
                opt_rect = pr.Rectangle(select_box_x, select_y + select_box_h + i * 40, select_box_w, 40)
                if pr.check_collision_point_rec(m_pos, opt_rect):
                    handle_song_change(opt)
                    song_select_open = False
                    break
            else:
                song_select_open = False

    # Draw expanded options dropdown
    if song_select_open:
        options = [
            {"id": "none", "title": "Libre"},
            {"id": "twinkle", "title": "Estrellita"},
            {"id": "joy", "title": "Himno Alegría"},
            {"id": "birthday", "title": "Cumpleaños"}
        ]
        
        dropdown_h = len(options) * 40
        pr.draw_rectangle(int(select_box_x), int(select_y + select_box_h), select_box_w, dropdown_h, pr.Color(10, 10, 10, 245))
        pr.draw_rectangle_lines(int(select_box_x), int(select_y + select_box_h), select_box_w, dropdown_h, pr.Color(38, 38, 38, 255))
        
        for i, opt in enumerate(options):
            opt_rect = pr.Rectangle(select_box_x, select_y + select_box_h + i * 40, select_box_w, 40)
            is_hovered = pr.check_collision_point_rec(m_pos, opt_rect)
            
            # Hover backglow
            if is_hovered:
                pr.draw_rectangle_rec(opt_rect, pr.Color(23, 23, 23, 255))
                
            pr.draw_text(opt["title"], int(opt_rect.x + 10), int(opt_rect.y + 15), 11, pr.WHITE)
            pr.draw_line(int(opt_rect.x), int(opt_rect.y + opt_rect.height), int(opt_rect.x + opt_rect.width), int(opt_rect.y + opt_rect.height), pr.Color(23, 23, 23, 255))

    # --- Draw Celebration Overlay & Modal ---
    if show_celebration and show_modal:
        # Translucent dark backdrop
        pr.draw_rectangle(0, 0, sw, sh, pr.Color(0, 0, 0, 204)) # 80% opacity
        
        # Modal card dimensions
        modal_w = 340
        modal_h = 420
        modal_x = sw // 2 - modal_w // 2
        modal_y = sh // 2 - modal_h // 2
        
        modal_rect = pr.Rectangle(modal_x, modal_y, modal_w, modal_h)
        
        # Soft white outer glow halo
        for glow in range(1, 15):
            glow_rect = pr.Rectangle(modal_x - glow, modal_y - glow, modal_w + glow * 2, modal_h + glow * 2)
            pr.draw_rectangle_rounded_lines(glow_rect, 0.1, 4, pr.Color(255, 255, 255, int((15 - glow) * 1.5)))
            
        # Draw modal card body
        pr.draw_rectangle_rounded(modal_rect, 0.1, 4, pr.Color(10, 10, 10, 255)) # Dark black
        pr.draw_rectangle_rounded_lines(modal_rect, 0.1, 4, pr.Color(38, 38, 38, 120))
        
        # Trophy icon with bounce animation
        bounce_offset = int(math.sin(pr.get_time() * 4) * 8)
        trophy_rect = pr.Rectangle(sw // 2 - 40, modal_y + 30 + bounce_offset, 80, 80)
        
        # Trophy background circle
        pr.draw_circle(sw // 2, int(trophy_rect.y + 40), 40, pr.Color(234, 179, 8, 25))
        # Draw Trophy emoji
        pr.draw_text("🏆", int(trophy_rect.x + 13), int(trophy_rect.y + 12), 48, pr.WHITE)
        
        # Title text
        title_txt = "¡Canción Completada!"
        title_w = pr.measure_text(title_txt, 20)
        pr.draw_text(title_txt, sw // 2 - title_w // 2, modal_y + 130, 20, pr.WHITE)
        
        sub_txt = "Has finalizado la lección con éxito"
        sub_w = pr.measure_text(sub_txt, 11)
        pr.draw_text(sub_txt, sw // 2 - sub_w // 2, modal_y + 160, 11, pr.Color(163, 163, 163, 255))
        
        # Draw Rating Stars (⭐, ⭐⭐, ⭐⭐⭐)
        current_song = next((s for s in SONGS if s["id"] == selected_song_id), None)
        num_stars = 1
        if current_song:
            accuracy = max(0, 100 - int((mistake_count / len(current_song["notes"])) * 100))
            if accuracy >= 95 and mistake_count == 0:
                num_stars = 3
            elif accuracy >= 80:
                num_stars = 2
                
        # Draw vector stars dynamically
        star_r_out = 16
        star_r_in = 7
        star_spacing = 40
        star_start_x = sw // 2 - ((num_stars - 1) * star_spacing) // 2
        for s_idx in range(num_stars):
            cx = star_start_x + s_idx * star_spacing
            cy = modal_y + 195
            # Scale pulsing
            pulsing = math.sin(pr.get_time() * 5 + s_idx * 1.5) * 2
            draw_star(cx, cy, star_r_out + pulsing, star_r_in + pulsing / 2, pr.Color(245, 158, 11, 255))
            
        # Stats breakdown container
        breakdown_y = modal_y + 230
        breakdown_w = modal_w - 40
        breakdown_h = 100
        breakdown_rect = pr.Rectangle(modal_x + 20, breakdown_y, breakdown_w, breakdown_h)
        
        pr.draw_rectangle_rounded(breakdown_rect, 0.15, 4, pr.Color(23, 23, 23, 127))
        pr.draw_rectangle_rounded_lines(breakdown_rect, 0.15, 4, pr.Color(38, 38, 38, 255))
        
        # Details stats texts
        text_y = breakdown_y + 15
        
        pr.draw_text("Puntuación Final:", int(breakdown_rect.x + 15), text_y, 12, pr.Color(163, 163, 163, 255))
        scr_lbl = str(score)
        pr.draw_text(scr_lbl, int(breakdown_rect.x + breakdown_w - pr.measure_text(scr_lbl, 12) - 15), text_y, 12, pr.WHITE)
        
        pr.draw_text("Combo Máximo:", int(breakdown_rect.x + 15), text_y + 25, 12, pr.Color(163, 163, 163, 255))
        cmb_lbl = str(max_combo)
        pr.draw_text(cmb_lbl, int(breakdown_rect.x + breakdown_w - pr.measure_text(cmb_lbl, 12) - 15), text_y + 25, 12, pr.Color(14, 165, 233, 255))
        
        pr.draw_text("Total de Fallos:", int(breakdown_rect.x + 15), text_y + 50, 12, pr.Color(163, 163, 163, 255))
        mst_lbl = str(mistake_count)
        pr.draw_text(mst_lbl, int(breakdown_rect.x + breakdown_w - pr.measure_text(mst_lbl, 12) - 15), text_y + 50, 12, pr.Color(239, 68, 68, 255))
        
        # Aceptar Button
        btn_y = modal_y + 350
        btn_w = modal_w - 40
        btn_h = 46
        btn_rect = pr.Rectangle(modal_x + 20, btn_y, btn_w, btn_h)
        
        btn_hovered = pr.check_collision_point_rec(m_pos, btn_rect)
        btn_col = pr.Color(245, 245, 245, 255) if btn_hovered else pr.WHITE
        
        pr.draw_rectangle_rounded(btn_rect, 0.25, 4, btn_col)
        
        btn_txt = "Aceptar"
        btn_txt_w = pr.measure_text(btn_txt, 14)
        pr.draw_text(btn_txt, int(btn_rect.x + btn_w // 2 - btn_txt_w // 2), int(btn_rect.y + btn_h // 2 - 7), 14, pr.BLACK)
        
        if btn_hovered and pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT):
            close_celebration_modal()

    pr.end_drawing()

# Clean up Raylib resources on exit
for s in loaded_sounds.values():
    pr.unload_sound(s)
    
pr.close_audio_device()
pr.close_window()
