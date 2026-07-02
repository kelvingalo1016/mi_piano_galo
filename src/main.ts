import "./index.css";
import { PIANO_KEYS, type PianoKey } from "./lib/keyboard-map";
import { SONGS, type Song } from "./lib/songs-data";
import { pianoAudio } from "./lib/piano-audio";

// App State
let selectedSongId = "none";
let isPlaying = false;
let playbackTime = 0;
let lastTickTime = performance.now();

// Scoring & Stats
let score = 0;
let combo = 0;
let maxCombo = 0;
let mistakeCount = 0;

const activeNotes = new Set<string>();
const guideNotes = new Set<string>();
const userPressedNotes = new Set<string>();
const rainbowNotesMap = new Map<string, string>();
const mistakesNotesMap = new Map<string, string>();

let showCelebration = false;

// DOM Elements
const loadingOverlay = document.getElementById("loading-overlay")!;
const loadingBar = document.getElementById("loading-bar")!;
const loadingStatus = document.getElementById("loading-status")!;
const songSelect = document.getElementById("song-select") as HTMLSelectElement;
const statsContainer = document.getElementById("stats-container")!;
const statScore = document.getElementById("stat-score")!;
const statCombo = document.getElementById("stat-combo")!;
const statMaxCombo = document.getElementById("stat-max-combo")!;
const statMistakes = document.getElementById("stat-mistakes")!;
const visualizerContainer = document.getElementById("visualizer-container")!;
const visualizerCanvas = document.getElementById("visualizer-canvas") as HTMLCanvasElement;
const keyboardContainer = document.getElementById("keyboard-container")!;
const celebrationModal = document.getElementById("celebration-modal")!;
const modalStars = document.getElementById("modal-stars")!;
const modalScore = document.getElementById("modal-score")!;
const modalMaxCombo = document.getElementById("modal-max-combo")!;
const modalMistakes = document.getElementById("modal-mistakes")!;
const modalAcceptBtn = document.getElementById("modal-accept-btn")!;

// Canvas Context & Particles
const ctx = visualizerCanvas.getContext("2d")!;
let particles: Array<{
  x: number;
  y: number;
  vx: number;
  vy: number;
  color: string;
  alpha: number;
  size: number;
}> = [];

// Separate white and black keys list
const whiteKeys: PianoKey[] = [];
const blackKeys: (PianoKey & { whiteIndex: number })[] = [];

PIANO_KEYS.forEach((key) => {
  if (!key.isBlack) {
    whiteKeys.push(key);
  } else {
    const precedingWhiteIndex = whiteKeys.length - 1;
    if (precedingWhiteIndex >= 0) {
      blackKeys.push({
        ...key,
        whiteIndex: precedingWhiteIndex,
      });
    }
  }
});

const keyElements = new Map<string, HTMLElement>();

// Keyboard layout generation
function buildKeyboard() {
  keyboardContainer.innerHTML = "";

  const boardWrapper = document.createElement("div");
  boardWrapper.className = "min-w-[800px] md:min-w-0 w-full max-w-[1500px] aspect-[12/3.2] md:aspect-[12/3.1] flex bg-neutral-950 p-3 md:p-4 rounded-2xl md:rounded-3xl border border-neutral-800 shadow-md relative mx-auto";

  const keyboardInner = document.createElement("div");
  keyboardInner.className = "flex w-full h-full relative";

  // White Keys layer
  const whiteKeysLayer = document.createElement("div");
  whiteKeysLayer.className = "flex w-full h-full z-10 relative";

  whiteKeys.forEach((key, index) => {
    const keyEl = document.createElement("div");
    keyEl.className = "relative flex-1 h-full select-none cursor-pointer transition-all duration-75 border-l border-r border-t border-neutral-300 rounded-b-[10px] bg-gradient-to-b from-neutral-50 via-white to-neutral-200 border-b-[6px] border-b-neutral-300 hover:from-neutral-100 hover:to-neutral-150";
    
    // Rounded corners for boundaries
    if (index === 0) keyEl.style.borderBottomLeftRadius = "16px";
    if (index === whiteKeys.length - 1) keyEl.style.borderBottomRightRadius = "16px";

    // Text Label
    const label = document.createElement("div");
    label.className = "key-label absolute bottom-4 left-0 right-0 text-center flex flex-col items-center pointer-events-none text-neutral-500 dark:text-neutral-600";
    const labelSpan = document.createElement("span");
    labelSpan.className = "text-xs md:text-sm font-semibold";
    labelSpan.innerText = key.note;
    label.appendChild(labelSpan);
    keyEl.appendChild(label);

    // Event Listeners
    keyEl.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      try { keyEl.setPointerCapture(e.pointerId); } catch(err) {}
      handlePlayNote(key.note);
    });
    const handleRelease = (e: PointerEvent) => {
      try { keyEl.releasePointerCapture(e.pointerId); } catch(err) {}
      handleStopNote(key.note);
    };
    keyEl.addEventListener("pointerup", handleRelease);
    keyEl.addEventListener("pointercancel", handleRelease);

    whiteKeysLayer.appendChild(keyEl);
    keyElements.set(key.note, keyEl);
  });

  // Black Keys layer (Absolute overlay)
  const blackKeysLayer = document.createElement("div");
  blackKeysLayer.className = "absolute inset-0 pointer-events-none z-25";

  blackKeys.forEach((key) => {
    const keyEl = document.createElement("div");
    keyEl.className = "absolute pointer-events-auto select-none cursor-pointer rounded-b-[6px] transition-all duration-75 shadow-md border-l border-r border-t border-neutral-950 bg-gradient-to-b from-neutral-950 to-neutral-950 border-b-[6px] border-b-black";

    const totalWhiteKeys = whiteKeys.length;
    const leftPercent = ((key.whiteIndex + 1) / totalWhiteKeys) * 100;
    const whiteKeyWidthPercent = 100 / totalWhiteKeys;
    const blackKeyWidthPercent = whiteKeyWidthPercent * 0.6;

    keyEl.style.left = `${leftPercent}%`;
    keyEl.style.transform = "translateX(-50%)";
    keyEl.style.width = `${blackKeyWidthPercent}%`;
    keyEl.style.height = "calc(60% + 6px)";
    keyEl.style.top = "-6px";

    // Text label for black key
    const label = document.createElement("div");
    label.className = "key-label absolute bottom-2 left-0 right-0 text-center flex flex-col items-center pointer-events-none text-neutral-400";
    const labelSpan = document.createElement("span");
    labelSpan.className = "text-[9px] font-semibold";
    labelSpan.innerText = key.note;
    label.appendChild(labelSpan);
    keyEl.appendChild(label);

    // Event Listeners
    keyEl.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      e.stopPropagation();
      try { keyEl.setPointerCapture(e.pointerId); } catch(err) {}
      handlePlayNote(key.note);
    });
    const handleRelease = (e: PointerEvent) => {
      e.stopPropagation();
      try { keyEl.releasePointerCapture(e.pointerId); } catch(err) {}
      handleStopNote(key.note);
    };
    keyEl.addEventListener("pointerup", handleRelease);
    keyEl.addEventListener("pointercancel", handleRelease);

    blackKeysLayer.appendChild(keyEl);
    keyElements.set(key.note, keyEl);
  });

  keyboardInner.appendChild(whiteKeysLayer);
  keyboardInner.appendChild(blackKeysLayer);
  boardWrapper.appendChild(keyboardInner);
  keyboardContainer.appendChild(boardWrapper);
}

// Update Keyboard UI classes dynamically
function updateKeyboardUI() {
  whiteKeys.forEach((key) => {
    const el = keyElements.get(key.note);
    if (!el) return;
    const isActive = activeNotes.has(key.note) || guideNotes.has(key.note);
    const rainbowColor = rainbowNotesMap.get(key.note);
    const mistakeStyle = mistakesNotesMap.get(key.note);

    el.className = "relative flex-1 h-full select-none cursor-pointer transition-all duration-75 border-l border-r border-t border-neutral-300 rounded-b-[10px] ";
    
    if (mistakeStyle) {
      el.className += "bg-red-500 border-red-400 border-b-[2px] border-b-red-700 translate-y-[4px] shadow-inner z-20 animate-shake";
    } else if (isActive) {
      el.className += "bg-gradient-to-b from-sky-400 via-sky-500 to-sky-600 border-sky-500 border-b-[2px] border-b-sky-700 translate-y-[4px] shadow-inner shadow-[inset_0_4px_6px_rgba(0,0,0,0.25)] z-20";
    } else if (rainbowColor) {
      el.className += `${rainbowColor} border-b-[2px] translate-y-[4px] shadow-inner z-20`;
    } else {
      el.className += "bg-gradient-to-b from-neutral-50 via-white to-neutral-200 border-b-[6px] border-b-neutral-300 hover:from-neutral-100 hover:to-neutral-150";
    }

    const label = el.querySelector(".key-label");
    if (label) {
      label.className = `key-label absolute bottom-4 left-0 right-0 text-center flex flex-col items-center pointer-events-none ${
        isActive ? "text-white font-bold" : "text-neutral-500 dark:text-neutral-600"
      }`;
    }
  });

  blackKeys.forEach((key) => {
    const el = keyElements.get(key.note);
    if (!el) return;
    const isActive = activeNotes.has(key.note) || guideNotes.has(key.note);
    const rainbowColor = rainbowNotesMap.get(key.note);
    const mistakeStyle = mistakesNotesMap.get(key.note);

    el.className = "absolute pointer-events-auto select-none cursor-pointer rounded-b-[6px] transition-all duration-75 shadow-md border-l border-r border-t border-neutral-950 ";
    
    if (mistakeStyle) {
      el.className += "bg-red-500 border-red-450 border-b-[2px] border-b-red-700 z-30 animate-shake";
      el.style.transform = "translateX(-50%) translateY(4px)";
    } else if (isActive) {
      el.className += "bg-gradient-to-b from-amber-400 via-amber-500 to-amber-600 border-amber-300 border-b-[2px] border-b-amber-700 shadow-inner shadow-[inset_0_3px_4px_rgba(0,0,0,0.4)] z-30";
      el.style.transform = "translateX(-50%) translateY(4px)";
    } else if (rainbowColor) {
      el.className += `${rainbowColor} border-b-[2px] z-30`;
      el.style.transform = "translateX(-50%) translateY(4px)";
    } else {
      el.className += "bg-gradient-to-b from-neutral-950 to-neutral-950 border-b-[6px] border-b-black";
      el.style.transform = "translateX(-50%)";
    }

    const label = el.querySelector(".key-label");
    if (label) {
      label.className = `key-label absolute bottom-2 left-0 right-0 text-center flex flex-col items-center pointer-events-none ${
        isActive ? "text-white font-bold" : "text-neutral-400"
      }`;
    }
  });
}

function triggerMistake(note: string) {
  mistakesNotesMap.set(note, "bg-red-500 text-white font-bold border-red-400");
  updateKeyboardUI();

  // Create floating "Oops!" element
  const keyEl = keyElements.get(note);
  if (keyEl) {
    const oops = document.createElement("span");
    oops.className = "absolute -top-10 left-1/2 -translate-x-1/2 text-red-500 font-black text-sm animate-float-up pointer-events-none z-40 whitespace-nowrap";
    oops.innerText = "¡Oops!";
    keyEl.appendChild(oops);

    setTimeout(() => {
      oops.remove();
    }, 1000);
  }

  setTimeout(() => {
    mistakesNotesMap.delete(note);
    updateKeyboardUI();
  }, 300);
}

// Update Stats UI values
function updateStatsUI() {
  statScore.innerText = score.toString();
  statCombo.innerText = combo.toString();
  statMaxCombo.innerText = maxCombo.toString();
  statMistakes.innerText = mistakeCount.toString();
}

// Update Solo mode guide note indicators
function updateGuideNotes(song: Song) {
  guideNotes.clear();
  if (!isPlaying || selectedSongId === "none") return;

  const nextNote = song.notes.find(
    n => !userPressedNotes.has(`${n.time}-${n.note}`)
  );

  if (nextNote) {
    const notesAtTime = song.notes.filter(n => n.time === nextNote.time);
    notesAtTime.forEach(n => guideNotes.add(n.note));
  }
}

// Play note trigger
function handlePlayNote(note: string) {
  activeNotes.add(note);
  pianoAudio.triggerNoteAttack(note);

  if (isPlaying && selectedSongId !== "none") {
    const currentSong = SONGS.find(s => s.id === selectedSongId);
    if (currentSong) {
      const nextNote = currentSong.notes.find(
        n => !userPressedNotes.has(`${n.time}-${n.note}`)
      );

      if (nextNote) {
        if (note === nextNote.note) {
          // Correct note hit!
          userPressedNotes.add(`${nextNote.time}-${nextNote.note}`);
          
          // Calculate score based on timing precision
          const hitScore = Math.max(10, 100 - Math.floor(Math.abs(playbackTime - nextNote.time) * 100));
          score += hitScore;
          combo++;
          if (combo > maxCombo) maxCombo = combo;
          
          updateStatsUI();
          updateGuideNotes(currentSong);
        } else {
          // Wrong note hit!
          // Only register error for notes near active timing window
          if (nextNote.time <= playbackTime + 1.0) {
            mistakeCount++;
            combo = 0;
            updateStatsUI();
            triggerMistake(note);
          }
        }
      }
    }
  }

  updateKeyboardUI();
}

// Stop note trigger
function handleStopNote(note: string) {
  activeNotes.delete(note);
  pianoAudio.triggerNoteRelease(note);
  updateKeyboardUI();
}

// Keyboard Mapping Input Listener
const keyboardMap: Record<string, string> = {};
PIANO_KEYS.forEach((k) => {
  keyboardMap[k.keyboardKey] = k.note;
});

window.addEventListener("keydown", (e) => {
  // If celebration modal is open, pressing any key exits celebration
  if (showCelebration) {
    closeCelebrationModal();
    return;
  }

  if (e.repeat) return;
  const note = keyboardMap[e.key];
  if (note) {
    handlePlayNote(note);
  }
});

window.addEventListener("keyup", (e) => {
  const note = keyboardMap[e.key];
  if (note) {
    handleStopNote(note);
  }
});

// Canvas Drawing Coordinates Calculation
function getKeyX(noteName: string, canvasWidth: number): { x: number; isBlack: boolean; keyWidth: number } {
  const whiteKeysList = PIANO_KEYS.filter(k => !k.isBlack);
  const totalWhiteKeys = whiteKeysList.length;
  const whiteKeyWidth = canvasWidth / totalWhiteKeys;
  const blackKeyWidth = whiteKeyWidth * 0.6;

  const keyInfo = PIANO_KEYS.find(k => k.note === noteName);
  if (!keyInfo) return { x: 0, isBlack: false, keyWidth: 10 };

  if (!keyInfo.isBlack) {
    const idx = whiteKeysList.findIndex(k => k.note === noteName);
    return {
      x: idx * whiteKeyWidth + whiteKeyWidth / 2,
      isBlack: false,
      keyWidth: whiteKeyWidth,
    };
  } else {
    // Preceding white key placement
    const precedingWhiteNote = PIANO_KEYS[PIANO_KEYS.indexOf(keyInfo) - 1]?.note;
    const idx = whiteKeysList.findIndex(k => k.note === precedingWhiteNote);
    return {
      x: (idx + 1) * whiteKeyWidth,
      isBlack: true,
      keyWidth: blackKeyWidth,
    };
  }
}

// Main Canvas rendering and particles
function drawVisualizer() {
  const width = visualizerCanvas.width;
  const height = visualizerCanvas.height;

  // Clear Canvas background
  ctx.fillStyle = "#0a0a0a";
  ctx.fillRect(0, 0, width, height);

  // 1. Draw Guides
  const whiteKeysList = PIANO_KEYS.filter(k => !k.isBlack);
  const totalWhiteKeys = whiteKeysList.length;
  const whiteWidth = width / totalWhiteKeys;

  ctx.strokeStyle = "#262626";
  ctx.lineWidth = 1;
  for (let i = 1; i < totalWhiteKeys; i++) {
    ctx.beginPath();
    ctx.moveTo(i * whiteWidth, 0);
    ctx.lineTo(i * whiteWidth, height);
    ctx.stroke();
  }

  if (!isPlaying || selectedSongId === "none") {
    // Draw target line and return
    ctx.beginPath();
    ctx.moveTo(0, height - 1.5);
    ctx.lineTo(width, height - 1.5);
    ctx.strokeStyle = "#404040";
    ctx.lineWidth = 3;
    ctx.stroke();
    return;
  }

  const currentSong = SONGS.find(s => s.id === selectedSongId);
  if (!currentSong) return;

  const timeWindow = 3.0; // seconds

  // 2. Draw active note columns background glow
  currentSong.notes.forEach((note) => {
    const isActive = playbackTime >= note.time && playbackTime <= note.time + note.duration;
    if (isActive) {
      const { x, isBlack, keyWidth } = getKeyX(note.note, width);
      ctx.fillStyle = isBlack ? "rgba(217, 119, 6, 0.08)" : "rgba(2, 132, 199, 0.08)";
      ctx.fillRect(x - keyWidth / 2, 0, keyWidth, height);
    }
  });

  // 3. Draw falling notes
  currentSong.notes.forEach((note) => {
    const noteEnd = note.time + note.duration;
    const isVisible = noteEnd >= playbackTime && note.time <= playbackTime + timeWindow;

    if (isVisible) {
      const { x, isBlack, keyWidth } = getKeyX(note.note, width);

      // Positions
      let bottomY = height - ((note.time - playbackTime) / timeWindow) * height;
      let topY = height - ((noteEnd - playbackTime) / timeWindow) * height;

      // Active clamp at line threshold
      const isActive = playbackTime >= note.time && playbackTime <= noteEnd;
      if (isActive) {
        bottomY = height;
        if (Math.random() < 0.4) {
          particles.push({
            x: x + (Math.random() - 0.5) * keyWidth,
            y: height - 2,
            vx: (Math.random() - 0.5) * 1.5,
            vy: -(Math.random() * 2 + 1),
            color: isBlack ? "#f59e0b" : "#0ea5e9",
            alpha: 1.0,
            size: Math.random() * 3 + 2,
          });
        }
      }

      const rectHeight = Math.max(8, bottomY - topY);

      ctx.fillStyle = isBlack ? "#f59e0b" : "#0ea5e9";
      ctx.globalAlpha = isActive ? 1.0 : 0.75;
      
      // Note block rendering
      ctx.beginPath();
      const rectX = x - keyWidth / 2;
      const radius = 4;
      if (ctx.roundRect) {
        ctx.roundRect(rectX, topY, keyWidth, rectHeight, radius);
      } else {
        ctx.rect(rectX, topY, keyWidth, rectHeight);
      }
      ctx.fill();

      // Border outline for active playing note
      if (isActive) {
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }
      ctx.globalAlpha = 1.0;

      // Label text name inside visualizer note block
      if (rectHeight > 4) {
        ctx.fillStyle = isBlack ? "#1c1917" : "#ffffff";
        ctx.font = "bold 10px sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(note.note.replace("#", "♯"), x, topY + rectHeight / 2);
      }
    }
  });

  // 4. Update and Draw Particles
  particles.forEach((p) => {
    p.x += p.vx;
    p.y += p.vy;
    p.alpha -= 0.025;
  });
  particles = particles.filter((p) => p.alpha > 0);

  particles.forEach((p) => {
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
    ctx.fillStyle = p.color;
    ctx.globalAlpha = p.alpha;
    ctx.fill();
    ctx.globalAlpha = 1.0;
  });

  // 5. Draw target hit line
  ctx.beginPath();
  ctx.moveTo(0, height - 1.5);
  ctx.lineTo(width, height - 1.5);
  ctx.strokeStyle = "#404040";
  ctx.lineWidth = 3;
  ctx.stroke();
}

// Bucle de ticks y animaciones con rAF
function tick() {
  const now = performance.now();
  const delta = (now - lastTickTime) / 1000;
  lastTickTime = now;

  if (isPlaying && selectedSongId !== "none") {
    const currentSong = SONGS.find(s => s.id === selectedSongId);
    if (currentSong) {
      const nextNote = currentSong.notes.find(
        n => !userPressedNotes.has(`${n.time}-${n.note}`)
      );

      let nextTime = playbackTime + delta;

      if (!nextNote) {
        const songLength = Math.max(...currentSong.notes.map(n => n.time + n.duration)) + 1;
        if (playbackTime >= songLength) {
          // Song completed!
          stopSongPlayback();
          showCelebrationScreen(currentSong);
        }
      } else {
        if (playbackTime >= nextNote.time) {
          nextTime = nextNote.time;
        } else if (nextTime >= nextNote.time) {
          nextTime = nextNote.time;
        }
      }

      playbackTime = nextTime;
    }
  }

  drawVisualizer();
  requestAnimationFrame(tick);
}

// Trigger celebration logic and screen
function showCelebrationScreen(song: Song) {
  showCelebration = true;
  pianoAudio.playCelebrationFanfare();
  triggerRainbowCascade();

  // Prepare stats
  const accuracy = Math.max(0, 100 - Math.floor((mistakeCount / song.notes.length) * 100));
  let stars = "⭐";
  if (accuracy >= 95 && mistakeCount === 0) stars = "⭐⭐⭐";
  else if (accuracy >= 80) stars = "⭐⭐";

  modalStars.innerHTML = "";
  for (let i = 0; i < stars.length; i++) {
    const starSpan = document.createElement("span");
    starSpan.className = "text-yellow-500 animate-pulse";
    starSpan.innerText = "⭐";
    modalStars.appendChild(starSpan);
  }

  modalScore.innerText = score.toString();
  modalMaxCombo.innerText = maxCombo.toString();
  modalMistakes.innerText = mistakeCount.toString();

  // Show Modal card after brief delay
  setTimeout(() => {
    if (!showCelebration) return;
    celebrationModal.classList.remove("pointer-events-none", "opacity-0");
    celebrationModal.querySelector(".bg-neutral-950")!.classList.remove("scale-95");
  }, 1500);
}

function triggerRainbowCascade() {
  const colors = [
    "bg-gradient-to-b from-red-400 via-red-500 to-red-600 border-red-500 border-b-red-700 text-white font-bold",
    "bg-gradient-to-b from-orange-400 via-orange-500 to-orange-600 border-orange-500 border-b-orange-700 text-white font-bold",
    "bg-gradient-to-b from-amber-400 via-amber-500 to-amber-600 border-amber-500 border-b-amber-700 text-amber-950 font-bold",
    "bg-gradient-to-b from-emerald-400 via-emerald-500 to-emerald-600 border-emerald-500 border-b-emerald-700 text-white font-bold",
    "bg-gradient-to-b from-sky-400 via-sky-500 to-sky-600 border-sky-500 border-b-sky-700 text-white font-bold",
    "bg-gradient-to-b from-violet-400 via-violet-500 to-violet-600 border-violet-500 border-b-violet-700 text-white font-bold",
    "bg-gradient-to-b from-pink-400 via-pink-500 to-pink-600 border-pink-500 border-b-pink-700 text-white font-bold",
  ];

  PIANO_KEYS.forEach((key, index) => {
    setTimeout(() => {
      if (!showCelebration) return;
      const color = colors[index % colors.length];
      rainbowNotesMap.set(key.note, color);
      updateKeyboardUI();

      setTimeout(() => {
        rainbowNotesMap.delete(key.note);
        updateKeyboardUI();
      }, 1500);
    }, index * 40);
  });
}

function closeCelebrationModal() {
  showCelebration = false;
  celebrationModal.classList.add("pointer-events-none", "opacity-0");
  celebrationModal.querySelector(".bg-neutral-950")!.classList.add("scale-95");
  rainbowNotesMap.clear();
  updateKeyboardUI();

  // Reset to Modo Libre (Ninguna)
  songSelect.value = "none";
  handleSongChange("none");
}

function stopSongPlayback() {
  isPlaying = false;
  guideNotes.clear();
  activeNotes.clear();
  updateKeyboardUI();
}

function resetStats() {
  score = 0;
  combo = 0;
  maxCombo = 0;
  mistakeCount = 0;
  userPressedNotes.clear();
  updateStatsUI();
}

function handleSongChange(songId: string) {
  selectedSongId = songId;
  resetStats();

  if (songId === "none") {
    isPlaying = false;
    statsContainer.classList.add("hidden");
    visualizerContainer.classList.add("hidden");
  } else {
    isPlaying = true;
    playbackTime = 0;
    statsContainer.classList.remove("hidden");
    visualizerContainer.classList.remove("hidden");

    // Recalculate guide notes
    const song = SONGS.find(s => s.id === songId);
    if (song) {
      updateGuideNotes(song);
    }
  }

  resizeCanvas();
  updateKeyboardUI();
}

// Song Select listener
songSelect.addEventListener("change", (e) => {
  const value = (e.target as HTMLSelectElement).value;
  handleSongChange(value);
});

// Modal button click listener
modalAcceptBtn.addEventListener("click", () => {
  closeCelebrationModal();
});

// Window Resize Canvas sync
function resizeCanvas() {
  const rect = visualizerCanvas.getBoundingClientRect();
  visualizerCanvas.width = rect.width;
  visualizerCanvas.height = rect.height;
}
window.addEventListener("resize", resizeCanvas);

// Initialize App
buildKeyboard();
resizeCanvas();

// Fake progress indicator to let the loading bar move dynamically
let progress = 0;
const pInterval = setInterval(() => {
  progress = Math.min(85, progress + Math.random() * 15);
  loadingBar.style.width = `${progress}%`;
}, 200);

// Initialize Tone sampler
pianoAudio.init(() => {
  clearInterval(pInterval);
  loadingBar.style.width = "100%";
  loadingStatus.innerText = "¡Listo!";
  
  setTimeout(() => {
    loadingOverlay.classList.add("opacity-0");
    setTimeout(() => {
      loadingOverlay.classList.add("hidden");
      // Start main tick loop
      requestAnimationFrame(tick);
    }, 500);
  }, 400);
});
