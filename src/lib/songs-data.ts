export interface NoteEvent {
  note: string;
  time: number;     // Start time in seconds
  duration: number; // Duration in seconds
}

export interface Song {
  id: string;
  title: string;
  composer: string;
  notes: NoteEvent[];
}

export const SONGS: Song[] = [
  {
    id: "twinkle",
    title: "Estrellita Dónde Estás",
    composer: "Tradicional",
    notes: [
      { note: "C4", time: 0.0, duration: 0.4 },
      { note: "C4", time: 0.5, duration: 0.4 },
      { note: "G4", time: 1.0, duration: 0.4 },
      { note: "G4", time: 1.5, duration: 0.4 },
      { note: "A4", time: 2.0, duration: 0.4 },
      { note: "A4", time: 2.5, duration: 0.4 },
      { note: "G4", time: 3.0, duration: 0.8 },

      { note: "F4", time: 4.0, duration: 0.4 },
      { note: "F4", time: 4.5, duration: 0.4 },
      { note: "E4", time: 5.0, duration: 0.4 },
      { note: "E4", time: 5.5, duration: 0.4 },
      { note: "D4", time: 6.0, duration: 0.4 },
      { note: "D4", time: 6.5, duration: 0.4 },
      { note: "C4", time: 7.0, duration: 0.8 },

      { note: "G4", time: 8.0, duration: 0.4 },
      { note: "G4", time: 8.5, duration: 0.4 },
      { note: "F4", time: 9.0, duration: 0.4 },
      { note: "F4", time: 9.5, duration: 0.4 },
      { note: "E4", time: 10.0, duration: 0.4 },
      { note: "E4", time: 10.5, duration: 0.4 },
      { note: "D4", time: 11.0, duration: 0.8 },

      { note: "G4", time: 12.0, duration: 0.4 },
      { note: "G4", time: 12.5, duration: 0.4 },
      { note: "F4", time: 13.0, duration: 0.4 },
      { note: "F4", time: 13.5, duration: 0.4 },
      { note: "E4", time: 14.0, duration: 0.4 },
      { note: "E4", time: 14.5, duration: 0.4 },
      { note: "D4", time: 15.0, duration: 0.8 },

      { note: "C4", time: 16.0, duration: 0.4 },
      { note: "C4", time: 16.5, duration: 0.4 },
      { note: "G4", time: 17.0, duration: 0.4 },
      { note: "G4", time: 17.5, duration: 0.4 },
      { note: "A4", time: 18.0, duration: 0.4 },
      { note: "A4", time: 18.5, duration: 0.4 },
      { note: "G4", time: 19.0, duration: 0.8 },

      { note: "F4", time: 20.0, duration: 0.4 },
      { note: "F4", time: 20.5, duration: 0.4 },
      { note: "E4", time: 21.0, duration: 0.4 },
      { note: "E4", time: 21.5, duration: 0.4 },
      { note: "D4", time: 22.0, duration: 0.4 },
      { note: "D4", time: 22.5, duration: 0.4 },
      { note: "C4", time: 23.0, duration: 0.8 }
    ]
  },
  {
    id: "joy",
    title: "Himno a la Alegría",
    composer: "L.v. Beethoven",
    notes: [
      { note: "E4", time: 0.0, duration: 0.4 },
      { note: "E4", time: 0.5, duration: 0.4 },
      { note: "F4", time: 1.0, duration: 0.4 },
      { note: "G4", time: 1.5, duration: 0.4 },
      { note: "G4", time: 2.0, duration: 0.4 },
      { note: "F4", time: 2.5, duration: 0.4 },
      { note: "E4", time: 3.0, duration: 0.4 },
      { note: "D4", time: 3.5, duration: 0.4 },
      { note: "C4", time: 4.0, duration: 0.4 },
      { note: "C4", time: 4.5, duration: 0.4 },
      { note: "D4", time: 5.0, duration: 0.4 },
      { note: "E4", time: 5.5, duration: 0.4 },
      { note: "E4", time: 6.0, duration: 0.6 },
      { note: "D4", time: 6.5, duration: 0.2 },
      { note: "D4", time: 6.8, duration: 0.8 },

      { note: "E4", time: 8.0, duration: 0.4 },
      { note: "E4", time: 8.5, duration: 0.4 },
      { note: "F4", time: 9.0, duration: 0.4 },
      { note: "G4", time: 9.5, duration: 0.4 },
      { note: "G4", time: 10.0, duration: 0.4 },
      { note: "F4", time: 10.5, duration: 0.4 },
      { note: "E4", time: 11.0, duration: 0.4 },
      { note: "D4", time: 11.5, duration: 0.4 },
      { note: "C4", time: 12.0, duration: 0.4 },
      { note: "C4", time: 12.5, duration: 0.4 },
      { note: "D4", time: 13.0, duration: 0.4 },
      { note: "E4", time: 13.5, duration: 0.4 },
      { note: "D4", time: 14.0, duration: 0.6 },
      { note: "C4", time: 14.5, duration: 0.2 },
      { note: "C4", time: 14.8, duration: 0.8 }
    ]
  },
  {
    id: "birthday",
    title: "Cumpleaños Feliz",
    composer: "Mildred J. Hill & Patty Hill",
    notes: [
      { note: "G4", time: 0.0, duration: 0.3 },
      { note: "G4", time: 0.35, duration: 0.15 },
      { note: "A4", time: 0.5, duration: 0.4 },
      { note: "G4", time: 1.0, duration: 0.4 },
      { note: "C5", time: 1.5, duration: 0.4 },
      { note: "B4", time: 2.0, duration: 0.8 },
      { note: "G4", time: 3.0, duration: 0.3 },
      { note: "G4", time: 3.35, duration: 0.15 },
      { note: "A4", time: 3.5, duration: 0.4 },
      { note: "G4", time: 4.0, duration: 0.4 },
      { note: "D5", time: 4.5, duration: 0.4 },
      { note: "C5", time: 5.0, duration: 0.8 },
      { note: "G4", time: 6.0, duration: 0.3 },
      { note: "G4", time: 6.35, duration: 0.15 },
      { note: "G5", time: 6.5, duration: 0.4 },
      { note: "E5", time: 7.0, duration: 0.4 },
      { note: "C5", time: 7.5, duration: 0.4 },
      { note: "B4", time: 8.0, duration: 0.4 },
      { note: "A4", time: 8.5, duration: 0.4 },
      { note: "F5", time: 9.2, duration: 0.3 },
      { note: "F5", time: 9.55, duration: 0.15 },
      { note: "E5", time: 9.7, duration: 0.4 },
      { note: "C5", time: 10.2, duration: 0.4 },
      { note: "D5", time: 10.7, duration: 0.4 },
      { note: "C5", time: 11.2, duration: 0.8 }
    ]
  }
];
