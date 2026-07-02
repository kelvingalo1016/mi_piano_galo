import * as Tone from "tone";

class PianoAudioEngine {
  private sampler: Tone.Sampler | null = null;
  private synth: Tone.PolySynth | null = null;
  private reverb: Tone.Reverb | null = null;
  private delay: Tone.FeedbackDelay | null = null;
  private mainVolume: Tone.Volume | null = null;

  private isLoaded = false;
  private currentInstrument: "piano" | "synth" | "organ" | "guitar" | "accordion" | "marimba" = "piano";

  // Sustain pedal state
  private sustainPedal = false;
  private sustainedNotes: Set<string> = new Set();

  public async init(onLoadCallback?: () => void) {
    if (this.isLoaded) {
      if (onLoadCallback) onLoadCallback();
      return;
    }

    // Create main volume node
    this.mainVolume = new Tone.Volume(-6).toDestination(); // Slight attenuation to prevent clipping

    // Create Reverb and Delay effects
    this.reverb = new Tone.Reverb({
      decay: 1.5,
      wet: 0.15, // Default reverb wet level
    }).connect(this.mainVolume!);

    this.delay = new Tone.FeedbackDelay({
      delayTime: "4n",
      feedback: 0.15,
      wet: 0.0, // Default disabled delay level
    }).connect(this.reverb!);

    // Initialize Synth as fallback
    this.synth = new Tone.PolySynth(Tone.Synth, {
      oscillator: {
        type: "triangle",
      },
      envelope: {
        attack: 0.005,
        decay: 0.3,
        sustain: 0.4,
        release: 1.2,
      },
    }).connect(this.delay!);

    // Initialize Sampler with local audio files
    const sampleMap: Record<string, string> = {
      "A0": "A0.mp3",
      "C1": "C1.mp3",
      "D#1": "Ds1.mp3",
      "F#1": "Fs1.mp3",
      "A1": "A1.mp3",
      "C2": "C2.mp3",
      "D#2": "Ds2.mp3",
      "F#2": "Fs2.mp3",
      "A2": "A2.mp3",
      "C3": "C3.mp3",
      "D#3": "Ds3.mp3",
      "F#3": "Fs3.mp3",
      "A3": "A3.mp3",
      "C4": "C4.mp3",
      "D#4": "Ds4.mp3",
      "F#4": "Fs4.mp3",
      "A4": "A4.mp3",
      "C5": "C5.mp3",
      "D#5": "Ds5.mp3",
      "F#5": "Fs5.mp3",
      "A5": "A5.mp3",
      "C6": "C6.mp3",
      "D#6": "Ds6.mp3",
      "F#6": "Fs6.mp3",
      "A6": "A6.mp3",
      "C7": "C7.mp3",
      "D#7": "Ds7.mp3",
      "F#7": "Fs7.mp3",
      "A7": "A7.mp3",
      "C8": "C8.mp3",
    };

    return new Promise<void>((resolve) => {
      this.sampler = new Tone.Sampler({
        urls: sampleMap,
        baseUrl: "/audio/piano/",
        onload: () => {
          this.isLoaded = true;
          if (onLoadCallback) onLoadCallback();
          resolve();
        },
        onerror: (err) => {
          console.warn("Could not load piano samples, falling back to synth.", err);
          this.currentInstrument = "synth";
          this.isLoaded = true;
          if (onLoadCallback) onLoadCallback();
          resolve();
        },
      }).connect(this.delay!);
    });
  }

  public setInstrument(type: "piano" | "synth" | "organ" | "guitar" | "accordion" | "marimba") {
    this.currentInstrument = type;
    this.applySynthSettings();
  }

  public getInstrument() {
    return this.currentInstrument;
  }

  private applySynthSettings() {
    if (!this.synth) return;

    if (this.currentInstrument === "synth") {
      this.synth.set({
        oscillator: { type: "triangle" },
        envelope: { attack: 0.005, decay: 0.3, sustain: 0.4, release: 1.2 }
      });
    } else if (this.currentInstrument === "organ") {
      this.synth.set({
        oscillator: { type: "sine8" },
        envelope: { attack: 0.05, decay: 0.1, sustain: 1.0, release: 0.3 }
      });
    } else if (this.currentInstrument === "guitar") {
      this.synth.set({
        oscillator: { type: "sawtooth" },
        envelope: { attack: 0.001, decay: 0.6, sustain: 0.0, release: 0.8 }
      });
    } else if (this.currentInstrument === "accordion") {
      this.synth.set({
        oscillator: {
          type: "fatsawtooth",
          count: 3,
          spread: 14,
        } as any,
        envelope: {
          attack: 0.08,
          decay: 0.1,
          sustain: 0.9,
          release: 0.15,
        },
      });
    } else if (this.currentInstrument === "marimba") {
      this.synth.set({
        oscillator: { type: "sine" },
        envelope: { attack: 0.001, decay: 0.22, sustain: 0.0, release: 0.22 }
      });
    }
  }

  public triggerNoteAttack(note: string) {
    if (!this.isLoaded) return;

    if (Tone.context.state !== "running") {
      Tone.start();
    }

    if (this.currentInstrument === "piano" && this.sampler) {
      try {
        this.sampler.triggerAttack(note);
      } catch (err) {
        // Fallback if note isn't in sampler map (should not happen for C2-C7)
        if (this.synth) this.synth.triggerAttack(note);
      }
    } else if (this.synth) {
      this.synth.triggerAttack(note);
    }

    this.sustainedNotes.delete(note);
  }

  public triggerNoteRelease(note: string) {
    if (!this.isLoaded) return;

    if (this.sustainPedal) {
      this.sustainedNotes.add(note);
    } else {
      this.releaseNoteDirectly(note);
    }
  }

  private releaseNoteDirectly(note: string) {
    if (this.currentInstrument === "piano" && this.sampler) {
      try {
        this.sampler.triggerRelease(note);
      } catch (err) {
        if (this.synth) this.synth.triggerRelease(note);
      }
    } else if (this.synth) {
      this.synth.triggerRelease(note);
    }
  }

  private triggerNoteAttackAtTime(note: string, time: number) {
    if (this.currentInstrument === "piano" && this.sampler) {
      try {
        this.sampler.triggerAttack(note, time);
      } catch (err) {
        if (this.synth) this.synth.triggerAttack(note, time);
      }
    } else if (this.synth) {
      this.synth.triggerAttack(note, time);
    }
  }

  private triggerNoteReleaseAtTime(note: string, time: number) {
    if (this.currentInstrument === "piano" && this.sampler) {
      try {
        this.sampler.triggerRelease(note, time);
      } catch (err) {
        if (this.synth) this.synth.triggerRelease(note, time);
      }
    } else if (this.synth) {
      this.synth.triggerRelease(note, time);
    }
  }

  public playCelebrationFanfare() {
    if (!this.isLoaded) return;
    
    if (Tone.context.state !== "running") {
      Tone.start();
    }

    const now = Tone.now();
    
    // Ascending arpeggio (C major: C4 -> E4 -> G4 -> C5)
    this.triggerNoteAttackAtTime("C4", now);
    this.triggerNoteReleaseAtTime("C4", now + 0.4);

    this.triggerNoteAttackAtTime("E4", now + 0.15);
    this.triggerNoteReleaseAtTime("E4", now + 0.55);

    this.triggerNoteAttackAtTime("G4", now + 0.3);
    this.triggerNoteReleaseAtTime("G4", now + 0.7);

    this.triggerNoteAttackAtTime("C5", now + 0.45);
    this.triggerNoteReleaseAtTime("C5", now + 0.85);

    // Final triumphant chord: [C4, E4, G4, C5, E5]
    const chord = ["C4", "E4", "G4", "C5", "E5"];
    chord.forEach((note) => {
      this.triggerNoteAttackAtTime(note, now + 0.65);
      this.triggerNoteReleaseAtTime(note, now + 2.5);
    });
  }


  public setSustain(enabled: boolean) {
    this.sustainPedal = enabled;

    if (!enabled) {
      this.sustainedNotes.forEach((note) => {
        this.releaseNoteDirectly(note);
      });
      this.sustainedNotes.clear();
    }
  }

  public getSustain() {
    return this.sustainPedal;
  }

  public setVolume(volume: number) {
    if (!this.mainVolume) return;
    // volume is 0 to 100, map to decibels: 0 -> -Infinity, 100 -> 0
    if (volume === 0) {
      this.mainVolume.volume.value = -Infinity;
    } else {
      // Logarithmic volume mapping: db = 20 * log10(volume / 100)
      const db = 20 * Math.log10(volume / 100);
      this.mainVolume.volume.value = Math.max(-60, db);
    }
  }

  public setReverb(level: number) {
    if (this.reverb) {
      this.reverb.wet.value = level / 100; // 0 to 1
    }
  }

  public setDelay(level: number) {
    if (this.delay) {
      this.delay.wet.value = level / 100; // 0 to 1
    }
  }
}

export const pianoAudio = new PianoAudioEngine();
export default pianoAudio;
