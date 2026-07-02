import { useState, useEffect, useCallback, useRef, useMemo } from "react";
// import { PianoControls } from "@/components/piano-controls";
import { PianoKeyboard } from "@/components/piano-keyboard";
// import { PianoSheets } from "@/components/piano-sheets";
import { pianoAudio } from "@/lib/piano-audio";
import { keyboardMap, PIANO_KEYS } from "@/lib/keyboard-map";
import { PianoVisualizer } from "@/components/piano-visualizer";
import { SONGS } from "@/lib/songs-data";

export function App() {
  // const { theme, setTheme } = useTheme();
  const [isAudioLoaded, setIsAudioLoaded] = useState(false);
  
  // App states
  const [activeNotes, setActiveNotes] = useState<Set<string>>(new Set());
  const [volume, setVolumeState] = useState(85);
  const [reverb, setReverbState] = useState(15);
  const [delay, setDelayState] = useState(0);
  const [instrument, setInstrumentState] = useState<"piano" | "synth" | "organ" | "guitar" | "accordion" | "marimba">("piano");
  const [sustain, setSustainState] = useState(false);
  const [labelType, setLabelType] = useState<"key" | "note" | "none">("note");
  const [octaveRange, setOctaveRange] = useState<"full" | "medium" | "compact">("medium");
  const [errorLog, setErrorLog] = useState<string | null>(null);

  // Global Error Listener
  useEffect(() => {
    const handleGlobalError = (event: ErrorEvent) => {
      setErrorLog(event.message + "\n" + (event.error?.stack || "No stack trace available"));
    };
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      setErrorLog("Promise Rejection: " + event.reason);
    };

    window.addEventListener("error", handleGlobalError);
    window.addEventListener("unhandledrejection", handleUnhandledRejection);

    return () => {
      window.removeEventListener("error", handleGlobalError);
      window.removeEventListener("unhandledrejection", handleUnhandledRejection);
    };
  }, []);

  // Song player states
  const [selectedSongId, setSelectedSongId] = useState<string>("none");
  const [playMode, setPlayMode] = useState<"autoplay" | "practice">("practice");
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackTime, setPlaybackTime] = useState(0);
  const [showCelebration, setShowCelebration] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [rainbowNotes, setRainbowNotes] = useState<Record<string, string>>({});
  const [mistakeNotes, setMistakeNotes] = useState<Record<string, string>>({});
  const [score, setScore] = useState(0);
  const [combo, setCombo] = useState(0);
  const [maxCombo, setMaxCombo] = useState(0);
  const [mistakeCount, setMistakeCount] = useState(0);

  const modalTimeoutRef = useRef<any>(null);
  const scoreRef = useRef(0);
  const comboRef = useRef(0);
  const maxComboRef = useRef(0);
  const mistakeCountRef = useRef(0);

  const selectedSong = SONGS.find((s) => s.id === selectedSongId);
  const activeSongNotes = selectedSong ? selectedSong.notes : [];

  // Refs for requestAnimationFrame loops
  const playbackTimeRef = useRef(0);
  const logicalPlaybackTimeRef = useRef(0);
  const isPlayingRef = useRef(false);
  const playModeRef = useRef<"autoplay" | "practice">("practice");
  const selectedSongIdRef = useRef<string>("none");
  const lastTriggeredTimeRef = useRef<number>(-1);
  const userPressedNotesRef = useRef<Set<string>>(new Set());
  const noteLastTriggerTimeRef = useRef<Record<string, number>>({});

  // Calculate next notes to play in practice mode as a guide
  const guideNotes = useMemo(() => {
    if (!isPlaying || playMode !== "practice" || selectedSongId === "none" || !selectedSong) {
      return new Set<string>();
    }

    const nextNote = selectedSong.notes.find(
      n => !userPressedNotesRef.current.has(`${n.time}-${n.note}`)
    );

    if (nextNote) {
      const notesAtTime = selectedSong.notes.filter(n => n.time === nextNote.time);
      return new Set<string>(notesAtTime.map(n => n.note));
    }
    return new Set<string>();
  }, [playMode, selectedSongId, playbackTime, selectedSong, isPlaying]);

  // Keep refs synchronized
  useEffect(() => {
    playbackTimeRef.current = playbackTime;
  }, [playbackTime]);

  useEffect(() => {
    isPlayingRef.current = isPlaying;
  }, [isPlaying]);

  useEffect(() => {
    playModeRef.current = playMode;
  }, [playMode]);

  useEffect(() => {
    selectedSongIdRef.current = selectedSongId;
  }, [selectedSongId]);


  // Initialize Audio Engine
  useEffect(() => {
    pianoAudio.init(() => {
      setIsAudioLoaded(true);
      // Synchronize initial audio engine settings
      pianoAudio.setVolume(85);
      pianoAudio.setReverb(15);
      pianoAudio.setDelay(0);
      pianoAudio.setInstrument("piano");
      pianoAudio.setSustain(false);
    });
  }, []);

  // Update handlers that synchronize React state with Tone.js Audio Engine
  const setVolume = useCallback((val: number) => {
    setVolumeState(val);
    pianoAudio.setVolume(val);
  }, []);

  const setReverb = useCallback((val: number) => {
    setReverbState(val);
    pianoAudio.setReverb(val);
  }, []);

  const setDelay = useCallback((val: number) => {
    setDelayState(val);
    pianoAudio.setDelay(val);
  }, []);

  const setInstrument = useCallback((val: "piano" | "synth" | "organ" | "guitar" | "accordion" | "marimba") => {
    setInstrumentState(val);
    pianoAudio.setInstrument(val);
  }, []);

  const setSustain = useCallback((val: boolean) => {
    setSustainState(val);
    pianoAudio.setSustain(val);
  }, []);

  // Direct trigger play note (called by click, touch, autoplay, or keyboard keydown)
  const handlePlayNote = useCallback((note: string) => {
    const triggerTime = performance.now();
    noteLastTriggerTimeRef.current[note] = triggerTime;

    if (isPlayingRef.current && playModeRef.current === "practice") {
      const currentSong = SONGS.find(s => s.id === selectedSongIdRef.current);
      if (currentSong) {
        const nextNote = currentSong.notes.find(
          n => !userPressedNotesRef.current.has(`${n.time}-${n.note}`)
        );

        if (nextNote) {
          if (note === nextNote.note) {
            // Correct note hit!
            userPressedNotesRef.current.add(`${nextNote.time}-${nextNote.note}`);
            
            // Update stats
            const currentCombo = comboRef.current;
            scoreRef.current += (100 + currentCombo * 10);
            comboRef.current += 1;
            if (comboRef.current > maxComboRef.current) {
              maxComboRef.current = comboRef.current;
            }

            setScore(scoreRef.current);
            setCombo(comboRef.current);
            setMaxCombo(maxComboRef.current);

            // Release activeNote highlight after its duration
            setTimeout(() => {
              if (noteLastTriggerTimeRef.current[note] === triggerTime) {
                pianoAudio.triggerNoteRelease(note);
                setActiveNotes((prev) => {
                  const next = new Set(prev);
                  next.delete(note);
                  return next;
                });
              }
            }, nextNote.duration * 1000);
          } else {
            // Incorrect note hit!
            scoreRef.current = Math.max(0, scoreRef.current - 50);
            comboRef.current = 0;
            mistakeCountRef.current += 1;

            setScore(scoreRef.current);
            setCombo(0);
            setMistakeCount(mistakeCountRef.current);

            // Trigger mistake feedback (red key + Oops! text)
            setMistakeNotes((prev) => ({
              ...prev,
              [note]: "animate-shake bg-gradient-to-b from-red-500 via-red-600 to-red-700 border-red-400 border-b-[2px] border-b-red-800 text-white font-bold",
            }));
            setTimeout(() => {
              setMistakeNotes((prev) => {
                const next = { ...prev };
                delete next[note];
                return next;
              });
            }, 750);
          }
        }
      }
    }

    pianoAudio.triggerNoteAttack(note);
    setActiveNotes((prev) => {
      const next = new Set(prev);
      next.add(note);
      return next;
    });
  }, []);

  // Direct trigger stop note (called by click release, touch end, autoplay, or keyboard keyup)
  const handleStopNote = useCallback((note: string) => {
    pianoAudio.triggerNoteRelease(note);
    setActiveNotes((prev) => {
      const next = new Set(prev);
      next.delete(note);
      return next;
    });
  }, []);

  // Keyboard Event Handlers
  useEffect(() => {
    const isTyping = (target: EventTarget | null) => {
      if (!(target instanceof HTMLElement)) return false;
      return target.closest("input, textarea, select, [contenteditable='true']") !== null;
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (isTyping(e.target)) return;
      if (e.repeat) return; // Prevent repeated attack triggers

      // Spacebar toggles or holds sustain pedal
      if (e.key === " ") {
        e.preventDefault();
        setSustain(true);
        return;
      }

      // Check if key is mapped
      const note = keyboardMap[e.key];
      if (note) {
        e.preventDefault();
        handlePlayNote(note);
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      if (isTyping(e.target)) return;

      if (e.key === " ") {
        e.preventDefault();
        setSustain(false);
        return;
      }

      const note = keyboardMap[e.key];
      if (note) {
        e.preventDefault();
        handleStopNote(note);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("keyup", handleKeyUp);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("keyup", handleKeyUp);
    };
  }, [handlePlayNote, handleStopNote, setSustain]);

  // Autoplay Time Updater & Note Trigger Loop
  useEffect(() => {
    if (!isPlaying || playMode !== "autoplay") return;
    let lastTime = performance.now();
    let frameId: number;

    logicalPlaybackTimeRef.current = playbackTime;
    lastTriggeredTimeRef.current = playbackTime;

    const tick = () => {
      const now = performance.now();
      const delta = (now - lastTime) / 1000;
      lastTime = now;

      const prevTime = logicalPlaybackTimeRef.current;
      const nextTime = prevTime + delta;
      logicalPlaybackTimeRef.current = nextTime;

      const currentSong = SONGS.find(s => s.id === selectedSongId);
      if (currentSong) {
        const songLength = Math.max(...currentSong.notes.map(n => n.time + n.duration)) + 1;

        currentSong.notes.forEach(note => {
          if (note.time > lastTriggeredTimeRef.current && note.time <= nextTime) {
            const triggerTime = performance.now();
            noteLastTriggerTimeRef.current[note.note] = triggerTime;

            // Trigger attack
            pianoAudio.triggerNoteAttack(note.note);
            setActiveNotes(prevActive => {
              const nextActive = new Set(prevActive);
              nextActive.add(note.note);
              return nextActive;
            });

            // Schedule release
            setTimeout(() => {
              if (noteLastTriggerTimeRef.current[note.note] === triggerTime) {
                pianoAudio.triggerNoteRelease(note.note);
                setActiveNotes(prevActive => {
                  const nextActive = new Set(prevActive);
                  nextActive.delete(note.note);
                  return nextActive;
                });
              }
            }, note.duration * 1000);
          }
        });
        lastTriggeredTimeRef.current = nextTime;

        if (nextTime >= songLength) {
          setIsPlaying(false);
          setPlaybackTime(0);
          logicalPlaybackTimeRef.current = 0;
          lastTriggeredTimeRef.current = -1;
          userPressedNotesRef.current.clear();
          setShowCelebration(true);
          pianoAudio.playCelebrationFanfare();
          triggerRainbowCascade();

          if (modalTimeoutRef.current) clearTimeout(modalTimeoutRef.current);
          modalTimeoutRef.current = setTimeout(() => {
            setShowModal(true);
          }, 1500);
          return;
        }
      }

      setPlaybackTime(nextTime);
      frameId = requestAnimationFrame(tick);
    };

    frameId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frameId);
  }, [isPlaying, playMode, selectedSongId]);

  // Practice Mode Time Updater Loop
  useEffect(() => {
    if (!isPlaying || playMode !== "practice") return;
    let lastTime = performance.now();
    let frameId: number;

    logicalPlaybackTimeRef.current = playbackTime;

    const tick = () => {
      const now = performance.now();
      const delta = (now - lastTime) / 1000;
      lastTime = now;

      const prevTime = logicalPlaybackTimeRef.current;
      const currentSong = SONGS.find(s => s.id === selectedSongId);

      if (!currentSong) {
        frameId = requestAnimationFrame(tick);
        return;
      }

      // Find the next note that is not yet pressed by the user
      const nextNote = currentSong.notes.find(
        n => !userPressedNotesRef.current.has(`${n.time}-${n.note}`)
      );

      let nextTime = prevTime + delta;

      if (!nextNote) {
        // Song completed!
        const songLength = Math.max(...currentSong.notes.map(n => n.time + n.duration)) + 1;
        if (prevTime >= songLength) {
          setIsPlaying(false);
          setPlaybackTime(0);
          logicalPlaybackTimeRef.current = 0;
          userPressedNotesRef.current.clear();
          setShowCelebration(true);
          pianoAudio.playCelebrationFanfare();
          triggerRainbowCascade();

          if (modalTimeoutRef.current) clearTimeout(modalTimeoutRef.current);
          modalTimeoutRef.current = setTimeout(() => {
            setShowModal(true);
          }, 1500);
          return;
        }
      } else {
        // If the next note is at the hit threshold, wait for user keyhit
        if (prevTime >= nextNote.time) {
          nextTime = nextNote.time;
        } else if (nextTime >= nextNote.time) {
          nextTime = nextNote.time;
        }
      }

      logicalPlaybackTimeRef.current = nextTime;
      setPlaybackTime(nextTime);
      frameId = requestAnimationFrame(tick);
    };

    frameId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frameId);
  }, [isPlaying, playMode, selectedSongId]);

  const triggerRainbowCascade = useCallback(() => {
    const keys = PIANO_KEYS;
    const colors = [
      "bg-gradient-to-b from-red-400 via-red-500 to-red-600 border-red-500 border-b-red-700 text-white font-bold",
      "bg-gradient-to-b from-orange-400 via-orange-500 to-orange-600 border-orange-500 border-b-orange-700 text-white font-bold",
      "bg-gradient-to-b from-amber-400 via-amber-500 to-amber-600 border-amber-500 border-b-amber-700 text-amber-950 font-bold",
      "bg-gradient-to-b from-emerald-400 via-emerald-500 to-emerald-600 border-emerald-500 border-b-emerald-700 text-white font-bold",
      "bg-gradient-to-b from-sky-400 via-sky-500 to-sky-600 border-sky-500 border-b-sky-700 text-white font-bold",
      "bg-gradient-to-b from-violet-400 via-violet-500 to-violet-600 border-violet-500 border-b-violet-700 text-white font-bold",
      "bg-gradient-to-b from-pink-400 via-pink-500 to-pink-600 border-pink-500 border-b-pink-700 text-white font-bold",
    ];

    keys.forEach((key, index) => {
      setTimeout(() => {
        const color = colors[index % colors.length];
        setRainbowNotes((prev) => ({
          ...prev,
          [key.note]: color,
        }));

        setTimeout(() => {
          setRainbowNotes((prev) => {
            const next = { ...prev };
            delete next[key.note];
            return next;
          });
        }, 350);
      }, index * 30);
    });
  }, []);

  // Song player control callbacks
  const stopPlayback = useCallback(() => {
    setIsPlaying(false);
    setPlaybackTime(0);
    logicalPlaybackTimeRef.current = 0;
    lastTriggeredTimeRef.current = -1;
    userPressedNotesRef.current.clear();
    setActiveNotes(new Set());
    setShowCelebration(false);
    setShowModal(false);
    setRainbowNotes({});
    setMistakeNotes({});
    
    scoreRef.current = 0;
    comboRef.current = 0;
    maxComboRef.current = 0;
    mistakeCountRef.current = 0;
    setScore(0);
    setCombo(0);
    setMaxCombo(0);
    setMistakeCount(0);

    if (modalTimeoutRef.current) {
      clearTimeout(modalTimeoutRef.current);
      modalTimeoutRef.current = null;
    }
  }, []);

  const togglePlay = useCallback(() => {
    setIsPlaying(p => {
      const next = !p;
      if (next) {
        setShowCelebration(false);
        setShowModal(false);
        setRainbowNotes({});
        setMistakeNotes({});

        if (playbackTimeRef.current === 0) {
          userPressedNotesRef.current.clear();
          scoreRef.current = 0;
          comboRef.current = 0;
          maxComboRef.current = 0;
          mistakeCountRef.current = 0;
          setScore(0);
          setCombo(0);
          setMaxCombo(0);
          setMistakeCount(0);
        }

        if (modalTimeoutRef.current) {
          clearTimeout(modalTimeoutRef.current);
          modalTimeoutRef.current = null;
        }
      }
      return next;
    });
  }, []);

  const handleSongChange = useCallback((songId: string) => {
    setSelectedSongId(songId);
    setIsPlaying(songId !== "none");
    setPlayMode("practice");
    setPlaybackTime(0);
    logicalPlaybackTimeRef.current = 0;
    lastTriggeredTimeRef.current = -1;
    userPressedNotesRef.current.clear();
    setActiveNotes(new Set());
    setShowCelebration(false);
    setShowModal(false);
    setRainbowNotes({});
    setMistakeNotes({});

    scoreRef.current = 0;
    comboRef.current = 0;
    maxComboRef.current = 0;
    mistakeCountRef.current = 0;
    setScore(0);
    setCombo(0);
    setMaxCombo(0);
    setMistakeCount(0);

    if (modalTimeoutRef.current) {
      clearTimeout(modalTimeoutRef.current);
      modalTimeoutRef.current = null;
    }
  }, []);
  // Exit celebration modal and reset to Modo Libre when any key is pressed
  useEffect(() => {
    if (!showModal) return;

    const handleKeyDown = () => {
      setShowCelebration(false);
      setShowModal(false);
      handleSongChange("none");
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [showModal, handleSongChange]);

  // Dummy check to satisfy TypeScript unused locals while controls are commented out
  if (false as boolean) {
    console.log(
      volume,
      reverb,
      delay,
      instrument,
      sustain,
      octaveRange,
      setLabelType,
      setOctaveRange,
      setVolume,
      setReverb,
      setDelay,
      setInstrument,
      stopPlayback,
      togglePlay
    );
  }

  return (
    <main className="min-h-svh w-full bg-white text-neutral-900 flex items-center justify-center p-4 md:p-8 font-sans selection:bg-neutral-200 relative overflow-x-hidden overflow-y-hidden">
      {/* Main Centered Container */}
      <div className="w-full max-w-[1500px] flex flex-col items-center justify-center relative z-10">
        {errorLog && (
          <div className="w-full max-w-[1500px] bg-red-50 border-2 border-red-300 rounded-2xl p-4 mb-4 font-mono text-xs text-red-800 whitespace-pre-wrap select-text z-50 text-left">
            <h4 className="font-bold text-sm mb-1">⚠️ Error detectado en la aplicación:</h4>
            {errorLog}
          </div>
        )}
        
        {/* Header Section
        <header className="w-full flex items-center justify-between bg-card/40 backdrop-blur-md border border-border/40 rounded-2xl px-6 py-4 shadow-lg">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
              <Music className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-black tracking-tight bg-gradient-to-r from-sky-400 to-indigo-400 bg-clip-text text-transparent">
                Mi Piano Virtual
              </h1>
              <p className="text-[10px] text-muted-foreground font-mono">
                Optimizado para Raspberry Pi 4 | Offline Ready
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {sustain && (
              <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30 animate-pulse">
                PEDAL ACTIVE
              </span>
            )}
            
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="p-2 rounded-xl bg-muted/40 hover:bg-muted text-foreground border border-border/20 transition-colors cursor-pointer"
              title="Alternar Tema (Alt + D)"
            >
              {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
          </div>
        </header>
        */}

        {/* Loading Overlay */}
        {!isAudioLoaded && (
          <div className="w-full max-w-[500px] bg-neutral-50 border border-neutral-250 rounded-2xl p-12 shadow-md flex flex-col items-center justify-center gap-4 text-center">
            <div className="w-12 h-12 border-4 border-neutral-400 border-t-transparent rounded-full animate-spin" />
            <div>
              <h3 className="text-lg font-bold text-neutral-800">Cargando Sonido de Piano de Cola</h3>
              <p className="text-sm text-neutral-500 max-w-sm mt-1">
                Por favor espera mientras cargamos las muestras de audio directamente del almacenamiento local de tu Raspberry Pi.
              </p>
            </div>
          </div>
        )}

        {isAudioLoaded && (
          <>
            {/* Controls Panel
            <PianoControls
              volume={volume}
              setVolume={setVolume}
              reverb={reverb}
              setReverb={setReverb}
              delay={delay}
              setDelay={setDelay}
              instrument={instrument}
              setInstrument={setInstrument}
              sustain={sustain}
              setSustain={setSustain}
              labelType={labelType}
              setLabelType={setLabelType}
              octaveRange={octaveRange}
              setOctaveRange={setOctaveRange}
              isAudioLoaded={isAudioLoaded}
            />
            */}

            {/* Sheets Selector & Guide
            <PianoSheets
              onPlayNote={handlePlayNote}
              onStopNote={handleStopNote}
              activeNotes={activeNotes}
            />
            */}

            {/* Instrument Selector
            <div className="flex items-center gap-3 mb-4 select-none bg-neutral-50 px-4 py-2 rounded-xl border border-neutral-200 shadow-sm">
              <label htmlFor="instrument-select" className="text-sm font-bold text-neutral-700 tracking-wide">
                Sonido:
              </label>
              <select
                id="instrument-select"
                value={instrument}
                onChange={(e) => setInstrument(e.target.value as any)}
                className="bg-white border border-neutral-300 text-neutral-800 text-sm font-semibold rounded-lg focus:ring-neutral-400 focus:border-neutral-400 block p-1 px-2.5 shadow-sm hover:bg-neutral-50 cursor-pointer outline-none transition-all"
              >
                <option value="piano">Gran Piano Clásico</option>
                <option value="organ">Órgano de Iglesia</option>
                <option value="guitar">Guitarra Acústica</option>
                <option value="accordion">Acordeón</option>
                <option value="marimba">Marimba de Madera</option>
                <option value="synth">Sintetizador</option>
              </select>
            </div>
            */}

            {/* Song Player Controls */}
            <div className="w-full max-w-[1500px] bg-neutral-50 px-4 py-3 rounded-2xl border border-neutral-200 shadow-sm flex flex-wrap items-center justify-between gap-4 mb-4 select-none">
              <div className="flex items-center gap-3">
                <label htmlFor="song-select" className="text-sm font-bold text-neutral-700 tracking-wide">
                  Canción:
                </label>
                <select
                  id="song-select"
                  value={selectedSongId}
                  onChange={(e) => {
                    handleSongChange(e.target.value as any);
                    e.target.blur();
                  }}
                  className="bg-white border border-neutral-300 text-neutral-800 text-sm font-semibold rounded-lg focus:ring-neutral-400 focus:border-neutral-400 block p-1 px-2.5 shadow-sm hover:bg-neutral-50 cursor-pointer outline-none transition-all"
                >
                  <option value="none">Ninguna (Modo Libre)</option>
                  <option value="twinkle">Estrellita Dónde Estás</option>
                  <option value="joy">Himno a la Alegría</option>
                  <option value="birthday">Cumpleaños Feliz</option>
                </select>
              </div>

              {selectedSongId !== "none" && (
                <div className="flex items-center gap-4 bg-neutral-100/80 border border-neutral-200/55 rounded-xl px-3 py-1 text-xs font-bold text-neutral-750 shadow-sm animate-fade-in">
                  <div className="flex items-center gap-1">
                    <span className="text-neutral-450">Puntos:</span>
                    <span className="text-neutral-900 font-black">{score}</span>
                  </div>
                  <div className="w-[1px] h-3.5 bg-neutral-300" />
                  <div className="flex items-center gap-1">
                    <span className="text-neutral-450">Combo:</span>
                    <span className="text-amber-600 font-black">x{combo}</span>
                  </div>
                  <div className="w-[1px] h-3.5 bg-neutral-300" />
                  <div className="flex items-center gap-1">
                    <span className="text-neutral-450">Fallos:</span>
                    <span className={`font-black ${mistakeCount > 0 ? "text-red-500" : "text-neutral-500"}`}>{mistakeCount}</span>
                  </div>
                </div>
              )}
            </div>

            {/* PixiJS Falling Notes Visualizer */}
            {selectedSongId !== "none" && (
              <PianoVisualizer
                notes={activeSongNotes}
                playbackTimeRef={playbackTimeRef}
                isPlaying={isPlaying}
                showCelebration={showCelebration}
                labelType={labelType}
              />
            )}

            {/* Interactive Keyboard Layout */}
            <PianoKeyboard
              activeNotes={activeNotes}
              guideNotes={guideNotes}
              onNotePlay={handlePlayNote}
              onNoteStop={handleStopNote}
              labelType={labelType}
              rainbowNotes={rainbowNotes}
              mistakeNotes={mistakeNotes}
            />
          </>
        )}

        {/* Celebration Modal */}
        {showModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/45 backdrop-blur-sm animate-fade-in p-4">
            <div className="bg-neutral-950/95 border border-neutral-800/50 backdrop-blur-xl rounded-3xl p-8 max-w-sm w-full text-center shadow-[0_0_30px_rgba(255,255,255,0.2)] animate-scale-in flex flex-col items-center gap-5 select-none">
              {/* Trophy Icon with a floating glow */}
              <div className="w-20 h-20 bg-amber-950/40 rounded-full flex items-center justify-center text-amber-500 shadow-inner relative animate-bounce-slow">
                <span className="text-4xl">🏆</span>
                <span className="absolute inset-0 rounded-full bg-amber-400/20 blur animate-pulse" />
              </div>

              <div>
                <h3 className="text-2xl font-black text-white tracking-tight">
                  {playMode === "autoplay" ? "¡Espectáculo Completado!" : "¡Excelente Trabajo!"}
                </h3>
                <p className="text-sm text-neutral-400 mt-1.5 font-medium">
                  Has completado la canción:
                </p>
                <p className="text-base font-bold text-white mt-0.5">
                  {selectedSong?.title}
                </p>
              </div>

              {/* Gold Stars */}
              <div className="flex gap-2 justify-center my-1">
                {Array.from({ length: playMode === "autoplay" ? 3 : mistakeCount === 0 ? 3 : mistakeCount <= 3 ? 2 : 1 }).map((_, idx) => (
                  <span
                    key={idx}
                    className="text-4xl text-amber-400 animate-pop-star"
                    style={{ animationDelay: `${(idx + 1) * 200}ms` }}
                  >
                    ⭐
                  </span>
                ))}
              </div>

              {/* Small stats info */}
              <div className="w-full bg-neutral-900/40 border border-neutral-800/50 rounded-2xl py-3 px-4 flex justify-around text-xs font-semibold text-neutral-400">
                <div>
                  <span className="block text-[10px] uppercase tracking-wider text-neutral-500 font-bold">
                    Puntaje
                  </span>
                  <span className="text-sm font-bold text-white">
                    {score}
                  </span>
                </div>
                <div className="border-r border-neutral-800/50" />
                <div>
                  <span className="block text-[10px] uppercase tracking-wider text-neutral-500 font-bold">
                    Max Combo
                  </span>
                  <span className="text-sm font-bold text-amber-500">
                    x{maxCombo}
                  </span>
                </div>
                <div className="border-r border-neutral-800/50" />
                <div>
                  <span className="block text-[10px] uppercase tracking-wider text-neutral-500 font-bold">
                    Fallos
                  </span>
                  <span className={`text-sm font-bold ${mistakeCount > 0 ? "text-red-500" : "text-neutral-400"}`}>
                    {mistakeCount}
                  </span>
                </div>
              </div>

               {/* Action Buttons */}
              <div className="flex w-full mt-2">
                <button
                  onClick={() => {
                    setShowCelebration(false);
                    setShowModal(false);
                    handleSongChange("none");
                  }}
                  className="w-full bg-white hover:bg-neutral-100 text-neutral-900 font-bold py-2.5 px-4 text-sm rounded-xl shadow transition-all cursor-pointer"
                >
                  Aceptar
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </main>
  );
}

export default App;
