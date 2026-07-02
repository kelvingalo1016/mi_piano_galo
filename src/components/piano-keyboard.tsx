import { PIANO_KEYS, type PianoKey } from "@/lib/keyboard-map";

interface PianoKeyboardProps {
  activeNotes: Set<string>;
  guideNotes?: Set<string>;
  onNotePlay: (note: string) => void;
  onNoteStop: (note: string) => void;
  labelType: "key" | "note" | "none";
  rainbowNotes?: Record<string, string>;
  mistakeNotes?: Record<string, string>;
}

export const PianoKeyboard: React.FC<PianoKeyboardProps> = ({
  activeNotes,
  guideNotes = new Set(),
  onNotePlay,
  onNoteStop,
  labelType,
  rainbowNotes = {},
  mistakeNotes = {},
}) => {

  // Filter keys based on range selection
  const getFilteredKeys = (): PianoKey[] => {
    return PIANO_KEYS;
  };

  const keys = getFilteredKeys();

  // Create separated white and black keys list
  const whiteKeys: PianoKey[] = [];
  const blackKeys: (PianoKey & { whiteIndex: number })[] = [];

  keys.forEach((key) => {
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

  // Handle note triggering
  const handlePress = (note: string) => {
    onNotePlay(note);
  };

  const handleRelease = (note: string) => {
    onNoteStop(note);
  };

  return (
    <section 
      className="w-full flex justify-start md:justify-center py-4 md:py-8 select-none overflow-x-auto custom-scrollbar"
      aria-label="Teclado de Piano"
    >
      <div className="min-w-[800px] md:min-w-0 w-full max-w-[1500px] aspect-[12/3.2] md:aspect-[12/3.1] flex bg-neutral-950 p-3 md:p-4 rounded-2xl md:rounded-3xl border border-neutral-800 shadow-md relative mx-auto">
        <div className="flex w-full h-full relative">
          
          {/* Layer 1: White Keys */}
          <div className="flex w-full h-full z-10 relative">
            {whiteKeys.map((white, index) => {
              const isWhiteActive = activeNotes.has(white.note) || guideNotes.has(white.note);
              const rainbowColor = rainbowNotes[white.note];
              const mistakeStyle = mistakeNotes[white.note];

              return (
                <div
                  key={white.note}
                  className={`relative flex-1 h-full select-none cursor-pointer transition-all duration-75 border-l border-r border-t border-neutral-300 rounded-b-[10px] ${
                    mistakeStyle
                      ? `${mistakeStyle} translate-y-[4px] shadow-inner z-20`
                      : isWhiteActive
                      ? "bg-gradient-to-b from-sky-400 via-sky-500 to-sky-600 border-sky-500 border-b-[2px] border-b-sky-700 translate-y-[4px] shadow-inner shadow-[inset_0_4px_6px_rgba(0,0,0,0.25)] z-20"
                      : rainbowColor
                      ? `${rainbowColor} border-b-[2px] translate-y-[4px] shadow-inner z-20`
                      : "bg-gradient-to-b from-neutral-50 via-white to-neutral-200 border-b-[6px] border-b-neutral-300 hover:from-neutral-100 hover:to-neutral-150"
                  }`}
                  onPointerDown={(e) => {
                    e.preventDefault();
                    e.currentTarget.setPointerCapture(e.pointerId);
                    handlePress(white.note);
                  }}
                  onPointerUp={(e) => {
                    try {
                      e.currentTarget.releasePointerCapture(e.pointerId);
                    } catch (err) {}
                    handleRelease(white.note);
                  }}
                  onPointerCancel={(e) => {
                    try {
                      e.currentTarget.releasePointerCapture(e.pointerId);
                    } catch (err) {}
                    handleRelease(white.note);
                  }}
                  style={{
                    // Add rounded corners to start and end keys of the piano
                    borderBottomLeftRadius: index === 0 ? "16px" : undefined,
                    borderBottomRightRadius: index === whiteKeys.length - 1 ? "16px" : undefined,
                  }}
                >
                  {mistakeNotes[white.note] && (
                    <span className="absolute -top-10 left-1/2 -translate-x-1/2 text-red-500 font-black text-sm animate-float-up pointer-events-none z-40 whitespace-nowrap">
                      ¡Oops!
                    </span>
                  )}

                  {/* White Key Label */}
                  {labelType !== "none" && (
                    <div className={`absolute bottom-4 left-0 right-0 text-center flex flex-col items-center pointer-events-none ${
                      isWhiteActive ? "text-white font-bold" : "text-neutral-500 dark:text-neutral-600"
                    }`}>
                      <span className="text-xs md:text-sm font-semibold">
                        {labelType === "key" ? white.keyboardKey : white.note}
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Layer 2: Black Keys (Absolute Overlay Container) */}
          <div className="absolute inset-0 pointer-events-none z-20">
            {blackKeys.map((black) => {
              const isBlackActive = activeNotes.has(black.note) || guideNotes.has(black.note);
              const rainbowColor = rainbowNotes[black.note];
              const mistakeStyle = mistakeNotes[black.note];
              const totalWhiteKeys = whiteKeys.length;
              const leftPercent = ((black.whiteIndex + 1) / totalWhiteKeys) * 100;
              const whiteKeyWidthPercent = 100 / totalWhiteKeys;
              const blackKeyWidthPercent = whiteKeyWidthPercent * 0.6; // Black key is 60% width of a white key

              return (
                <div
                  key={black.note}
                  className={`absolute pointer-events-auto select-none cursor-pointer rounded-b-[6px] transition-all duration-75 shadow-md border-l border-r border-t border-neutral-950 ${
                    mistakeStyle
                      ? `${mistakeStyle} border-b-[2px] z-30`
                      : isBlackActive
                      ? "bg-gradient-to-b from-amber-400 via-amber-500 to-amber-600 border-amber-300 border-b-[2px] border-b-amber-700 shadow-inner shadow-[inset_0_3px_4px_rgba(0,0,0,0.4)] z-30"
                      : rainbowColor
                      ? `${rainbowColor} border-b-[2px] z-30`
                      : "bg-gradient-to-b from-neutral-950 to-neutral-950 border-b-[6px] border-b-black"
                  }`}
                  style={{
                    left: `${leftPercent}%`,
                    transform: (isBlackActive || rainbowColor || mistakeStyle) ? "translateX(-50%) translateY(4px)" : "translateX(-50%)",
                    width: `${blackKeyWidthPercent}%`,
                    height: "calc(60% + 6px)",
                    top: "-6px",
                  }}
                  onPointerDown={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    e.currentTarget.setPointerCapture(e.pointerId);
                    handlePress(black.note);
                  }}
                  onPointerUp={(e) => {
                    e.stopPropagation();
                    try {
                      e.currentTarget.releasePointerCapture(e.pointerId);
                    } catch (err) {}
                    handleRelease(black.note);
                  }}
                  onPointerCancel={(e) => {
                    e.stopPropagation();
                    try {
                      e.currentTarget.releasePointerCapture(e.pointerId);
                    } catch (err) {}
                    handleRelease(black.note);
                  }}
                >
                  {mistakeNotes[black.note] && (
                    <span className="absolute -top-10 left-1/2 -translate-x-1/2 text-red-500 font-black text-[10px] md:text-xs animate-float-up pointer-events-none z-40 whitespace-nowrap">
                      ¡Oops!
                    </span>
                  )}

                  {/* Black Key Label */}
                  {labelType !== "none" && (
                    <div className={`absolute bottom-2 left-0 right-0 text-center pointer-events-none ${
                      isBlackActive ? "text-amber-950 font-bold" : "text-neutral-400"
                    }`}>
                      <span className="text-[10px] md:text-xs font-semibold block">
                        {labelType === "key" ? black.keyboardKey : black.note.replace("#", "♯")}
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

        </div>
      </div>
    </section>
  );
};
export default PianoKeyboard;
