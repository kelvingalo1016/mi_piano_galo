import { Volume2, Sliders } from "lucide-react";

interface PianoControlsProps {
  volume: number;
  setVolume: (v: number) => void;
  reverb: number;
  setReverb: (r: number) => void;
  delay: number;
  setDelay: (d: number) => void;
  instrument: "piano" | "synth";
  setInstrument: (i: "piano" | "synth") => void;
  sustain: boolean;
  setSustain: (s: boolean) => void;
  labelType: "key" | "note" | "none";
  setLabelType: (l: "key" | "note" | "none") => void;
  octaveRange: "full" | "medium" | "compact";
  setOctaveRange: (r: "full" | "medium" | "compact") => void;
  isAudioLoaded: boolean;
}

export const PianoControls: React.FC<PianoControlsProps> = ({
  volume,
  setVolume,
  reverb,
  setReverb,
  delay,
  setDelay,
  instrument,
  setInstrument,
  sustain,
  setSustain,
  labelType,
  setLabelType,
  octaveRange,
  setOctaveRange,
  isAudioLoaded,
}) => {
  return (
    <div className="w-full bg-card/60 backdrop-blur-md border border-border/80 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row gap-6 items-center justify-between text-card-foreground">
      {/* Instrument Selection & Status */}
      <div className="flex flex-col gap-2 w-full md:w-auto">
        <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Instrumento
        </label>
        <div className="flex bg-muted/50 p-1 rounded-xl border border-border/40">
          <button
            onClick={() => setInstrument("piano")}
            disabled={!isAudioLoaded}
            className={`flex-1 md:flex-initial px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer ${
              instrument === "piano"
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Piano de Cola
          </button>
          <button
            onClick={() => setInstrument("synth")}
            className={`flex-1 md:flex-initial px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer ${
              instrument === "synth"
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Sintetizador
          </button>
        </div>
        <div className="flex items-center gap-2 mt-1">
          <span
            className={`w-2.5 h-2.5 rounded-full ${
              isAudioLoaded ? "bg-emerald-500 animate-pulse" : "bg-amber-500 animate-pulse"
            }`}
          />
          <span className="text-xs text-muted-foreground font-mono">
            {isAudioLoaded
              ? `Audio Listo (${instrument === "piano" ? "Muestras cargadas" : "Modo sintetizador"})`
              : "Cargando sonidos de piano..."}
          </span>
        </div>
      </div>

      {/* Main Sound Controls (Volume, Reverb, Delay) */}
      <div className="flex flex-wrap gap-6 items-center w-full md:w-auto flex-1 justify-center max-w-lg">
        {/* Volume Slider */}
        <div className="flex flex-col gap-2 flex-1 min-w-[120px]">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
            <Volume2 className="w-3.5 h-3.5" /> Volumen ({volume}%)
          </span>
          <input
            type="range"
            min="0"
            max="100"
            value={volume}
            onChange={(e) => setVolume(Number(e.target.value))}
            className="w-full h-1.5 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
          />
        </div>

        {/* Reverb Slider */}
        <div className="flex flex-col gap-2 flex-1 min-w-[120px]">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
            <Sliders className="w-3.5 h-3.5" /> Reverb ({reverb}%)
          </span>
          <input
            type="range"
            min="0"
            max="100"
            value={reverb}
            onChange={(e) => setReverb(Number(e.target.value))}
            className="w-full h-1.5 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
          />
        </div>

        {/* Delay Slider */}
        <div className="flex flex-col gap-2 flex-1 min-w-[120px]">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
            <Sliders className="w-3.5 h-3.5" /> Eco/Delay ({delay}%)
          </span>
          <input
            type="range"
            min="0"
            max="100"
            value={delay}
            onChange={(e) => setDelay(Number(e.target.value))}
            className="w-full h-1.5 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
          />
        </div>
      </div>

      {/* Toggles (Labels, Sustain Pedal, Octave Zoom) */}
      <div className="flex flex-wrap gap-4 w-full md:w-auto items-center justify-end">
        {/* Sustain Pedal Toggle */}
        <div className="flex flex-col gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Pedal Sustain
          </span>
          <button
            onClick={() => setSustain(!sustain)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 border cursor-pointer ${
              sustain
                ? "bg-amber-500/20 text-amber-500 border-amber-500/40 shadow-sm"
                : "bg-muted/30 text-muted-foreground border-border/40 hover:text-foreground hover:bg-muted/50"
            }`}
          >
            Sustain <span className="text-[10px] font-mono opacity-80 ml-1.5 bg-black/10 px-1.5 py-0.5 rounded border border-black/5">ESPACIO</span>
          </button>
        </div>

        {/* Labels Display Selector */}
        <div className="flex flex-col gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Etiquetas
          </span>
          <div className="flex bg-muted/50 p-1 rounded-xl border border-border/40">
            {(["key", "note", "none"] as const).map((type) => (
              <button
                key={type}
                onClick={() => setLabelType(type)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 cursor-pointer ${
                  labelType === type
                    ? "bg-background text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {type === "key" ? "Teclado" : type === "note" ? "Notas" : "Ninguno"}
              </button>
            ))}
          </div>
        </div>

        {/* Octave Range Selector */}
        <div className="flex flex-col gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Tamaño del Piano
          </span>
          <div className="flex bg-muted/50 p-1 rounded-xl border border-border/40">
            {(["full", "medium", "compact"] as const).map((range) => (
              <button
                key={range}
                onClick={() => setOctaveRange(range)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 cursor-pointer ${
                  octaveRange === range
                    ? "bg-background text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {range === "full" ? "Completo (5 Oct.)" : range === "medium" ? "Medio (3 Oct.)" : "Compacto (2 Oct.)"}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
export default PianoControls;
