export interface PianoKey {
  note: string;
  keyboardKey: string;
  isBlack: boolean;
  octave: number;
}

// Ordered list of all 61 keys from C2 to C7
export const PIANO_KEYS: PianoKey[] = [
  /*
  // Octave 2
  { note: "C2", keyboardKey: "1", isBlack: false, octave: 2 },
  { note: "C#2", keyboardKey: "!", isBlack: true, octave: 2 },
  { note: "D2", keyboardKey: "2", isBlack: false, octave: 2 },
  { note: "D#2", keyboardKey: "@", isBlack: true, octave: 2 },
  { note: "E2", keyboardKey: "3", isBlack: false, octave: 2 },
  { note: "F2", keyboardKey: "4", isBlack: false, octave: 2 },
  { note: "F#2", keyboardKey: "$", isBlack: true, octave: 2 },
  { note: "G2", keyboardKey: "5", isBlack: false, octave: 2 },
  { note: "G#2", keyboardKey: "%", isBlack: true, octave: 2 },
  { note: "A2", keyboardKey: "6", isBlack: false, octave: 2 },
  { note: "A#2", keyboardKey: "^", isBlack: true, octave: 2 },
  { note: "B2", keyboardKey: "7", isBlack: false, octave: 2 },
  */

  // Octave 3 (a to l)
  { note: "C3", keyboardKey: "a", isBlack: false, octave: 3 },
  { note: "C#3", keyboardKey: "b", isBlack: true, octave: 3 },
  { note: "D3", keyboardKey: "c", isBlack: false, octave: 3 },
  { note: "D#3", keyboardKey: "d", isBlack: true, octave: 3 },
  { note: "E3", keyboardKey: "e", isBlack: false, octave: 3 },
  { note: "F3", keyboardKey: "f", isBlack: false, octave: 3 },
  { note: "F#3", keyboardKey: "g", isBlack: true, octave: 3 },
  { note: "G3", keyboardKey: "h", isBlack: false, octave: 3 },
  { note: "G#3", keyboardKey: "i", isBlack: true, octave: 3 },
  { note: "A3", keyboardKey: "j", isBlack: false, octave: 3 },
  { note: "A#3", keyboardKey: "k", isBlack: true, octave: 3 },
  { note: "B3", keyboardKey: "l", isBlack: false, octave: 3 },

  // Octave 4 (m to x)
  { note: "C4", keyboardKey: "m", isBlack: false, octave: 4 },
  { note: "C#4", keyboardKey: "n", isBlack: true, octave: 4 },
  { note: "D4", keyboardKey: "o", isBlack: false, octave: 4 },
  { note: "D#4", keyboardKey: "p", isBlack: true, octave: 4 },
  { note: "E4", keyboardKey: "q", isBlack: false, octave: 4 },
  { note: "F4", keyboardKey: "r", isBlack: false, octave: 4 },
  { note: "F#4", keyboardKey: "s", isBlack: true, octave: 4 },
  { note: "G4", keyboardKey: "t", isBlack: false, octave: 4 },
  { note: "G#4", keyboardKey: "u", isBlack: true, octave: 4 },
  { note: "A4", keyboardKey: "v", isBlack: false, octave: 4 },
  { note: "A#4", keyboardKey: "w", isBlack: true, octave: 4 },
  { note: "B4", keyboardKey: "x", isBlack: false, octave: 4 },

  // Octave 5 (y to z, then 1 to 0)
  { note: "C5", keyboardKey: "y", isBlack: false, octave: 5 },
  { note: "C#5", keyboardKey: "z", isBlack: true, octave: 5 },
  { note: "D5", keyboardKey: "1", isBlack: false, octave: 5 },
  { note: "D#5", keyboardKey: "2", isBlack: true, octave: 5 },
  { note: "E5", keyboardKey: "3", isBlack: false, octave: 5 },
  { note: "F5", keyboardKey: "4", isBlack: false, octave: 5 },
  { note: "F#5", keyboardKey: "5", isBlack: true, octave: 5 },
  { note: "G5", keyboardKey: "6", isBlack: false, octave: 5 },
  { note: "G#5", keyboardKey: "7", isBlack: true, octave: 5 },
  { note: "A5", keyboardKey: "8", isBlack: false, octave: 5 },
  { note: "A#5", keyboardKey: "9", isBlack: true, octave: 5 },
  { note: "B5", keyboardKey: "0", isBlack: false, octave: 5 },

  /*
  // Octave 6
  { note: "C6", keyboardKey: "l", isBlack: false, octave: 6 },
  { note: "C#6", keyboardKey: "L", isBlack: true, octave: 6 },
  { note: "D6", keyboardKey: "z", isBlack: false, octave: 6 },
  { note: "D#6", keyboardKey: "Z", isBlack: true, octave: 6 },
  { note: "E6", keyboardKey: "x", isBlack: false, octave: 6 },
  { note: "F6", keyboardKey: "c", isBlack: false, octave: 6 },
  { note: "F#6", keyboardKey: "C", isBlack: true, octave: 6 },
  { note: "G6", keyboardKey: "v", isBlack: false, octave: 6 },
  { note: "G#6", keyboardKey: "V", isBlack: true, octave: 6 },
  { note: "A6", keyboardKey: "b", isBlack: false, octave: 6 },
  { note: "A#6", keyboardKey: "B", isBlack: true, octave: 6 },
  { note: "B6", keyboardKey: "n", isBlack: false, octave: 6 },

  // Octave 7
  { note: "C7", keyboardKey: "m", isBlack: false, octave: 7 },
  */
];

// Direct keyboard key to note map
export const keyboardMap: Record<string, string> = PIANO_KEYS.reduce(
  (acc, key) => {
    acc[key.keyboardKey] = key.note;
    return acc;
  },
  {} as Record<string, string>
);

// Direct note to QWERTY keyboard key map
export const noteToKeyMap: Record<string, string> = PIANO_KEYS.reduce(
  (acc, key) => {
    acc[key.note] = key.keyboardKey;
    return acc;
  },
  {} as Record<string, string>
);
