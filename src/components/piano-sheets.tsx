import React, { useState, useEffect, useRef } from "react";
import { Play, Square, RefreshCw, ChevronRight, Info, Music } from "lucide-react";

interface Song {
  title: string;
  artist: string;
  sheet: string; // Space-separated notes/chords, e.g. "s s h h j j h" or "[80e] r t"
  bpm: number;
}

const PRESET_SONGS: Song[] = [
  {
    title: "Estrellita Dónde Estás (Twinkle Twinkle)",
    artist: "Tradicional",
    sheet: "s s h h j j h  g g f f d d s  h h g g f f d  h h g g f f d  s s h h j j h  g g f f d d s",
    bpm: 100,
  },
  {
    title: "Para Elisa (Für Elise - Intro)",
    artist: "Ludwig van Beethoven",
    sheet: "f D f D f k d s j [80e] t u a j [w0r] y u o a f [qe0] u a s f f D f D f k d s j [80e] t u a j [w0r] y u o s a [80e]",
    bpm: 110,
  },
  {
    title: "Interstellar Theme (Main Theme)",
    artist: "Hans Zimmer",
    sheet: "f j f j f j f j f k f k f k f k f l f l f l f l f k f k f k f k f j f j f j f j f k f k f k f k f l f l f l f l f k f k f k f k [sf] [dg] [fh] [dg]",
    bpm: 130,
  },
  {
    title: "Feliz Cumpleaños (Happy Birthday)",
    artist: "Tradicional",
    sheet: "s s d s g f  s s d s h g  s s l j g f d  p p j g h g",
    bpm: 110,
  },
];

interface PianoSheetsProps {
  onPlayNote: (note: string) => void;
  onStopNote: (note: string) => void;
  activeNotes: Set<string>;
}

export const PianoSheets: React.FC<PianoSheetsProps> = ({
  onPlayNote,
  onStopNote,
}) => {
  const [selectedSongIndex, setSelectedSongIndex] = useState(0);
  const [customSheet, setCustomSheet] = useState("");
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentNoteIndex, setCurrentNoteIndex] = useState(-1);
  const [bpm, setBpm] = useState(PRESET_SONGS[0].bpm);

  // Playback timer refs
  const playTimeoutRef = useRef<any>(null);

  const selectedSong = PRESET_SONGS[selectedSongIndex];
  const sheetToPlay = customSheet.trim() ? customSheet : selectedSong.sheet;

  // Parse the sheet music into an array of notes/chords
  // Example input: "s s [80e] h"
  // Output: ["s", "s", "80e", "h"]
  const parseSheet = (sheetStr: string): string[] => {
    const tokens: string[] = [];
    let currentToken = "";
    let insideBrackets = false;

    for (let i = 0; i < sheetStr.length; i++) {
      const char = sheetStr[i];

      if (char === "[") {
        insideBrackets = true;
        continue;
      } else if (char === "]") {
        insideBrackets = false;
        if (currentToken) {
          tokens.push(currentToken);
          currentToken = "";
        }
        continue;
      }

      if (insideBrackets) {
        currentToken += char;
      } else {
        if (char === " " || char === "\n" || char === "\t") {
          if (currentToken) {
            tokens.push(currentToken);
            currentToken = "";
          }
        } else {
          currentToken += char;
        }
      }
    }

    if (currentToken) {
      tokens.push(currentToken);
    }

    return tokens.filter((t) => t.length > 0);
  };

  const parsedNotes = parseSheet(sheetToPlay);

  // Stop playback when component unmounts or song changes
  useEffect(() => {
    return () => {
      stopAutoplay();
    };
  }, []);

  // Update BPM when song changes
  useEffect(() => {
    if (!customSheet) {
      setBpm(PRESET_SONGS[selectedSongIndex].bpm);
    }
  }, [selectedSongIndex, customSheet]);

  const stopAutoplay = () => {
    setIsPlaying(false);
    setCurrentNoteIndex(-1);
    if (playTimeoutRef.current) {
      clearTimeout(playTimeoutRef.current);
      playTimeoutRef.current = null;
    }
  };

  // Convert piano sheet character (e.g. 's') to note string (e.g. 'C5') using a local keyboard mapping resolver
  // We mirror the mapping defined in keyboard-map.ts
  const resolveNoteFromChar = (char: string): string | null => {
    // Import piano key map dynamically or replicate mapping here for quick resolution
    const map: Record<string, string> = {
      "1": "C2", "!": "C#2", "2": "D2", "@": "D#2", "3": "E2", "4": "F2", "$": "F#2", "5": "G2", "%": "G#2", "6": "A2", "^": "A#2", "7": "B2",
      "8": "C3", "*": "C#3", "9": "D3", "(": "D#3", "0": "E3", "q": "F3", "Q": "F#3", "w": "G3", "W": "G#3", "e": "A3", "E": "A#3", "r": "B3",
      "t": "C4", "T": "C#4", "y": "D4", "Y": "D#4", "u": "E4", "i": "F4", "I": "F#4", "o": "G4", "O": "G#4", "p": "A4", "P": "A#4", "a": "B4",
      "s": "C5", "S": "C#5", "d": "D5", "D": "D#5", "f": "E5", "g": "F5", "G": "F#5", "h": "G5", "H": "G#5", "j": "A5", "J": "A#5", "k": "B5",
      "l": "C6", "L": "C#6", "z": "D6", "Z": "D#6", "x": "E6", "c": "F6", "C": "F#6", "v": "G6", "V": "G#6", "b": "A6", "B": "A#6", "n": "B6",
      "m": "C7"
    };
    return map[char] || null;
  };

  const playNoteOrChord = (token: string) => {
    // A token can be a single character 's' or a chord '80e'
    const chars = token.split("");
    const notesToPlay: string[] = [];

    chars.forEach((char) => {
      const note = resolveNoteFromChar(char);
      if (note) {
        notesToPlay.push(note);
        onPlayNote(note);
      }
    });

    // Automatically release after a short duration in autoplay mode
    const noteReleaseDelay = Math.max(100, (60000 / bpm) * 0.7);
    setTimeout(() => {
      notesToPlay.forEach((note) => {
        onStopNote(note);
      });
    }, noteReleaseDelay);
  };

  const startAutoplay = () => {
    if (parsedNotes.length === 0) return;
    setIsPlaying(true);
    let index = 0;
    setCurrentNoteIndex(0);

    const playNext = () => {
      if (index >= parsedNotes.length) {
        stopAutoplay();
        return;
      }

      const token = parsedNotes[index];
      playNoteOrChord(token);

      index++;
      setCurrentNoteIndex(index);

      // Duration of a beat based on BPM
      const beatDurationMs = 60000 / bpm;
      
      // Delay before the next note
      playTimeoutRef.current = setTimeout(playNext, beatDurationMs);
    };

    playNext();
  };

  const handleTogglePlay = () => {
    if (isPlaying) {
      stopAutoplay();
    } else {
      startAutoplay();
    }
  };

  const handleSelectSong = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const idx = Number(e.target.value);
    setSelectedSongIndex(idx);
    setCustomSheet(""); // Clear custom sheet when changing preset
    stopAutoplay();
  };

  return (
    <div className="w-full bg-card/60 backdrop-blur-md border border-border/80 rounded-2xl p-6 shadow-xl flex flex-col gap-4 text-card-foreground">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-border/50 pb-4">
        <div>
          <h2 className="text-lg font-bold flex items-center gap-2">
            <Music className="w-5 h-5 text-primary animate-pulse" /> Partituras Virtuales (Sheets)
          </h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            Selecciona una canción o escribe tu propia partitura al estilo de virtualpiano.net
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Song Selector */}
          <select
            value={selectedSongIndex}
            onChange={handleSelectSong}
            className="bg-muted/80 text-foreground text-sm font-medium px-3 py-2 rounded-xl border border-border/40 focus:outline-none focus:ring-1 focus:ring-primary max-w-[200px]"
          >
            {PRESET_SONGS.map((song, i) => (
              <option key={i} value={i}>
                {song.title}
              </option>
            ))}
          </select>

          {/* BPM input */}
          <div className="flex items-center gap-2 bg-muted/40 px-3 py-1 rounded-xl border border-border/20 text-xs">
            <span className="text-muted-foreground font-semibold">BPM:</span>
            <input
              type="number"
              min="40"
              max="240"
              value={bpm}
              onChange={(e) => setBpm(Math.max(40, Math.min(240, Number(e.target.value))))}
              className="bg-transparent text-foreground text-center font-mono w-10 border-none focus:outline-none"
            />
          </div>

          {/* Autoplay Button */}
          <button
            onClick={handleTogglePlay}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200 cursor-pointer shadow-md ${
              isPlaying
                ? "bg-rose-500 hover:bg-rose-600 text-white animate-pulse"
                : "bg-emerald-500 hover:bg-emerald-600 text-white"
            }`}
          >
            {isPlaying ? (
              <>
                <Square className="w-4 h-4 fill-white" /> Detener
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" /> Reproducción Auto
              </>
            )}
          </button>

          {/* Restart/Reset Button */}
          {isPlaying && (
            <button
              onClick={() => {
                stopAutoplay();
                setTimeout(startAutoplay, 100);
              }}
              className="p-2 rounded-xl bg-muted/80 hover:bg-muted text-foreground border border-border/30 cursor-pointer"
              title="Reiniciar"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Song Info */}
      {!customSheet && (
        <div className="flex justify-between text-xs text-muted-foreground bg-muted/20 px-3 py-2 rounded-lg border border-border/10">
          <span><strong>Canción:</strong> {selectedSong.title}</span>
          <span><strong>Artista:</strong> {selectedSong.artist}</span>
        </div>
      )}

      {/* Sheet Content / Visualizer */}
      <div className="flex flex-col gap-2">
        <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Contenido de la Partitura (Edítalo a tu gusto)
        </label>
        
        {/* Sheet Music Text Area */}
        <textarea
          value={customSheet ? customSheet : selectedSong.sheet}
          onChange={(e) => {
            setCustomSheet(e.target.value);
            stopAutoplay();
          }}
          placeholder="Pega tu partitura aquí, ej: s s d s g f ... las letras entre corchetes [sfg] se tocan juntas como acordes."
          className="w-full h-24 bg-muted/40 font-mono text-sm border border-border/50 rounded-xl p-4 focus:outline-none focus:ring-1 focus:ring-primary text-foreground resize-none leading-relaxed"
        />
      </div>

      {/* Note Reader Display */}
      {parsedNotes.length > 0 && (
        <div className="flex flex-col gap-2">
          <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1">
            <Info className="w-3.5 h-3.5 text-sky-500" /> Guía Visual de Notas (Presiona las teclas indicadas)
          </label>
          <div className="flex items-center gap-2 overflow-x-auto py-3 px-4 bg-neutral-950 rounded-xl border border-neutral-900 scrollbar-thin scrollbar-thumb-neutral-800">
            {parsedNotes.map((token, index) => {
              const isChord = token.length > 1;
              const isCurrent = index === currentNoteIndex - 1 && isPlaying;
              const isNext = index === currentNoteIndex && isPlaying;

              return (
                <div
                  key={index}
                  className={`flex-shrink-0 px-2.5 py-1.5 rounded-lg border font-mono font-bold transition-all duration-200 text-xs flex items-center gap-1 ${
                    isCurrent
                      ? "bg-emerald-500 border-emerald-400 text-neutral-950 scale-110 shadow-[0_0_12px_rgba(16,185,129,0.4)]"
                      : isNext
                        ? "bg-sky-500/20 border-sky-500 text-sky-400 shadow-[0_0_8px_rgba(56,189,248,0.2)] animate-pulse"
                        : "bg-neutral-900 border-neutral-800 text-neutral-400"
                  }`}
                >
                  {isChord ? `[${token}]` : token}
                  {index < parsedNotes.length - 1 && (
                    <ChevronRight className="w-3 h-3 text-neutral-600 flex-shrink-0" />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
export default PianoSheets;
