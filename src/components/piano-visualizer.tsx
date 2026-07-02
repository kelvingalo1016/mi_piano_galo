import React, { useEffect, useRef, useState } from "react";
import { Application, Graphics, Text } from "pixi.js";
import { PIANO_KEYS, type PianoKey } from "@/lib/keyboard-map";
import { type NoteEvent } from "@/lib/songs-data";

interface PianoVisualizerProps {
  notes: NoteEvent[];
  playbackTime: number;
  isPlaying: boolean;
  timeWindow?: number; // seconds shown in the vertical window
  showCelebration?: boolean;
  labelType?: "key" | "note" | "none";
}

interface VisualParticle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  color: number;
  alpha: number;
  size: number;
}

interface ConfettiParticle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  color: number;
  alpha: number;
  width: number;
  height: number;
  rotation: number;
  rotationSpeed: number;
  swaySpeed: number;
  swayAmount: number;
  swayPhase: number;
}

interface FireworkRocket {
  x: number;
  y: number;
  targetY: number;
  vy: number;
  color: number;
  size: number;
}

interface FireworkParticle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  color: number;
  alpha: number;
  size: number;
  gravity: number;
  fadeSpeed: number;
}

const CELEBRATION_COLORS = [
  0xf43f5e, // Rose
  0xec4899, // Pink
  0x8b5cf6, // Violet
  0x3b82f6, // Blue
  0x06b6d4, // Cyan
  0x10b981, // Emerald
  0xeab308, // Yellow
  0xf97316, // Orange
  0xef4444, // Red
];

export const PianoVisualizer: React.FC<PianoVisualizerProps> = ({
  notes,
  playbackTime,
  isPlaying,
  timeWindow = 3.0,
  showCelebration = false,
  labelType = "key",
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const appRef = useRef<Application | null>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 220 });
  const textLabelsRef = useRef<any[]>([]);

  // Separate white and black keys to match layout positioning
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

  const totalWhiteKeysCount = whiteKeys.length || 21;

  // Function to calculate key X coordinate
  const getKeyX = (noteName: string, width: number): { x: number; isBlack: boolean; keyWidth: number } => {
    const whiteWidth = width / totalWhiteKeysCount;

    // Find in white keys
    const wIndex = whiteKeys.findIndex((k) => k.note === noteName);
    if (wIndex !== -1) {
      return {
        x: (wIndex + 0.5) * whiteWidth,
        isBlack: false,
        keyWidth: Math.max(1, whiteWidth * 0.75),
      };
    }

    // Find in black keys
    const bKey = blackKeys.find((k) => k.note === noteName);
    if (bKey) {
      return {
        x: ((bKey.whiteIndex + 1) / totalWhiteKeysCount) * width,
        isBlack: true,
        keyWidth: Math.max(1, whiteWidth * 0.6 * 0.8),
      };
    }

    return { x: 0, isBlack: false, keyWidth: 10 };
  };

  const notesRef = useRef(notes);
  const playbackTimeRef = useRef(playbackTime);
  const isPlayingRef = useRef(isPlaying);
  const dimensionsRef = useRef(dimensions);
  const showCelebrationRef = useRef(showCelebration);

  // Sync refs to avoid re-initializing PixiJS Application on prop changes
  useEffect(() => {
    notesRef.current = notes;
  }, [notes]);

  useEffect(() => {
    playbackTimeRef.current = playbackTime;
  }, [playbackTime]);

  useEffect(() => {
    isPlayingRef.current = isPlaying;
  }, [isPlaying]);

  useEffect(() => {
    dimensionsRef.current = dimensions;
  }, [dimensions]);

  useEffect(() => {
    showCelebrationRef.current = showCelebration;
  }, [showCelebration]);

  const recreateLabels = React.useCallback(() => {
    const app = appRef.current;
    if (!app) return;

    // Clear existing text labels
    textLabelsRef.current.forEach(label => {
      if (label && !label.destroyed) {
        label.destroy();
      }
    });
    textLabelsRef.current = [];

    if (labelType === "none") return;

    const labels = notes.map(note => {
      const keyInfo = PIANO_KEYS.find(k => k.note === note.note);
      const isBlack = keyInfo?.isBlack ?? false;
      const keyboardKey = keyInfo?.keyboardKey ?? "";
      
      const displayText = labelType === "key" 
        ? keyboardKey 
        : note.note.replace("#", "♯");

      const label = new Text({
        text: displayText,
        style: {
          fontFamily: "Outfit, Inter, system-ui, sans-serif",
          fontSize: isBlack ? 9 : 11,
          fontWeight: "bold",
          fill: isBlack ? 0x1c1917 : 0xffffff,
        },
      });
      label.anchor.set(0.5);
      label.visible = false;
      app.stage.addChild(label);
      return label;
    });

    textLabelsRef.current = labels;
  }, [notes, labelType]);

  useEffect(() => {
    recreateLabels();
  }, [notes, labelType, recreateLabels]);

  // Handle Resize
  useEffect(() => {
    const handleResize = () => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const width = rect.width || 800; // fallback to 800 if 0
      const height = Math.max(140, Math.min(240, width * (1.8 / 12)));
      setDimensions({ width, height });
    };

    // Run once on mount to get initial size
    handleResize();

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Initialize PixiJS
  useEffect(() => {
    if (!canvasRef.current) return;

    let destroyed = false;
    let app: Application | null = null;

    const initPixi = async () => {
      try {
        app = new Application();
        appRef.current = app;

        const w = dimensionsRef.current.width || 800;
        const h = dimensionsRef.current.height || 220;

        await app.init({
          canvas: canvasRef.current!,
          width: w,
          height: h,
          backgroundAlpha: 0, // transparent canvas to inherit parent dark styling
          antialias: true,
          resolution: window.devicePixelRatio || 1,
          autoDensity: true,
        });

        if (destroyed) {
          if (app) {
            app.destroy({ removeView: false, releaseGlobalResources: true }, { children: true });
          }
          return;
        }

        // Resize immediately to correct any layout updates that happened during async initialization
        if (app.renderer) {
          app.renderer.resize(dimensionsRef.current.width, dimensionsRef.current.height);
        }

        // Setup draw graphics
        const graphics = new Graphics();
        app.stage.addChild(graphics);

        recreateLabels();

        // Particle system state
        let particles: VisualParticle[] = [];
        let confetti: ConfettiParticle[] = [];
        let rockets: FireworkRocket[] = [];
        let fireworkParticles: FireworkParticle[] = [];
        let frameCount = 0;

        // PixiJS animation loop ticker
        app.ticker.add(() => {
          try {
            graphics.clear();
            const { width, height } = app!.screen;

            // If the canvas is not visible or has no size, skip drawing to prevent triangulation math crashes
            if (width <= 0 || height <= 0) return;

            // 1. Draw grid guides for white key dividers
            const whiteWidth = width / totalWhiteKeysCount;
            graphics.beginPath();
            for (let i = 1; i < totalWhiteKeysCount; i++) {
              graphics.moveTo(i * whiteWidth, 0);
              graphics.lineTo(i * whiteWidth, height);
            }
            graphics.stroke({ width: 1, color: 0x262626 });

            if (showCelebrationRef.current) {
              // Hide all labels
              textLabelsRef.current.forEach((label) => {
                if (label && !label.destroyed) {
                  label.visible = false;
                }
              });

              frameCount++;

              // Spawn new firework rocket occasionally
              if (frameCount % 25 === 0 && rockets.length < 3) {
                rockets.push({
                  x: Math.random() * width,
                  y: height,
                  targetY: height * (0.15 + Math.random() * 0.45),
                  vy: -(Math.random() * 3.5 + 4),
                  color: CELEBRATION_COLORS[Math.floor(Math.random() * CELEBRATION_COLORS.length)],
                  size: Math.random() * 2 + 3,
                });
              }

              // Spawn new confetti
              if (frameCount % 2 === 0 && confetti.length < 80) {
                confetti.push({
                  x: Math.random() * width,
                  y: -10,
                  vx: (Math.random() - 0.5) * 1.0,
                  vy: Math.random() * 1.2 + 1.2,
                  color: CELEBRATION_COLORS[Math.floor(Math.random() * CELEBRATION_COLORS.length)],
                  alpha: 1.0,
                  width: Math.random() * 5 + 6,
                  height: Math.random() * 4 + 4,
                  rotation: Math.random() * Math.PI * 2,
                  rotationSpeed: (Math.random() - 0.5) * 0.15,
                  swaySpeed: Math.random() * 0.05 + 0.02,
                  swayAmount: Math.random() * 1.5 + 0.5,
                  swayPhase: Math.random() * Math.PI * 2,
                });
              }

              // Update and Draw Rockets
              rockets.forEach((r) => {
                r.y += r.vy;
                
                // Draw rocket
                graphics.beginPath();
                graphics.circle(r.x, r.y, r.size)
                  .fill({ color: 0xffffff }); // Bright white core
                
                // Draw a small colored glow
                graphics.beginPath();
                graphics.circle(r.x, r.y, r.size * 1.8)
                  .fill({ color: r.color, alpha: 0.3 });

                // Explode when reaching targetY
                if (r.y <= r.targetY) {
                  const numParticles = Math.floor(Math.random() * 15) + 25;
                  for (let i = 0; i < numParticles; i++) {
                    const angle = Math.random() * Math.PI * 2;
                    const speed = Math.random() * 3.5 + 1.0;
                    fireworkParticles.push({
                      x: r.x,
                      y: r.y,
                      vx: Math.cos(angle) * speed,
                      vy: Math.sin(angle) * speed,
                      color: r.color,
                      alpha: 1.0,
                      size: Math.random() * 2.5 + 1.5,
                      gravity: 0.06,
                      fadeSpeed: Math.random() * 0.015 + 0.015,
                    });
                  }
                }
              });
              rockets = rockets.filter((r) => r.y > r.targetY);

              // Update and Draw Firework Particles
              fireworkParticles.forEach((p) => {
                p.x += p.vx;
                p.y += p.vy;
                p.vy += p.gravity;
                p.alpha -= p.fadeSpeed;

                graphics.beginPath();
                graphics.circle(p.x, p.y, p.size)
                  .fill({ color: p.color, alpha: p.alpha });
                
                // Draw a tiny secondary spark occasionally for magic effect
                if (Math.random() < 0.15 && p.alpha > 0.4) {
                  graphics.beginPath();
                  graphics.circle(p.x, p.y, p.size * 0.6)
                    .fill({ color: 0xffffff, alpha: p.alpha * 0.8 });
                }
              });
              fireworkParticles = fireworkParticles.filter((p) => p.alpha > 0);

              // Update and Draw Confetti
              confetti.forEach((c) => {
                c.y += c.vy;
                c.x += Math.sin(c.swayPhase) * c.swayAmount;
                c.swayPhase += c.swaySpeed;
                c.rotation += c.rotationSpeed;

                // Rotated rectangle using polygon vertices
                const cos = Math.cos(c.rotation);
                const sin = Math.sin(c.rotation);
                const hw = c.width / 2;
                const hh = c.height / 2;
                const p1x = c.x + (-hw * cos - -hh * sin);
                const p1y = c.y + (-hw * sin + -hh * cos);
                const p2x = c.x + (hw * cos - -hh * sin);
                const p2y = c.y + (hw * sin + -hh * cos);
                const p3x = c.x + (hw * cos - hh * sin);
                const p3y = c.y + (hw * sin + hh * cos);
                const p4x = c.x + (-hw * cos - hh * sin);
                const p4y = c.y + (-hw * sin + hh * cos);

                graphics.beginPath();
                graphics.poly([p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y], true)
                  .fill({ color: c.color, alpha: c.alpha });
              });
              confetti = confetti.filter((c) => c.y < height + 20);
            } else {
              // Reset celebration states if disabled
              if (rockets.length > 0) rockets = [];
              if (confetti.length > 0) confetti = [];
              if (fireworkParticles.length > 0) fireworkParticles = [];
              frameCount = 0;

              // 2. Draw active note columns background glow
              notesRef.current.forEach((note) => {
                const isActive = playbackTimeRef.current >= note.time && playbackTimeRef.current <= note.time + note.duration;
                if (isActive) {
                  const { x, isBlack, keyWidth } = getKeyX(note.note, width);
                  graphics.beginPath();
                  graphics.rect(x - keyWidth / 2, 0, keyWidth, height)
                    .fill({
                      color: isBlack ? 0xd97706 : 0x0284c7,
                      alpha: 0.08,
                    });
                }
              });

              // 3. Draw falling notes
              notesRef.current.forEach((note, idx) => {
                // Is it visible in the window?
                const noteEnd = note.time + note.duration;
                const isVisible = noteEnd >= playbackTimeRef.current && note.time <= playbackTimeRef.current + timeWindow;

                const label = textLabelsRef.current[idx];

                if (isVisible) {
                  const { x, isBlack, keyWidth } = getKeyX(note.note, width);

                  // Calculate positions
                  let bottomY = height - ((note.time - playbackTimeRef.current) / timeWindow) * height;
                  let topY = height - ((noteEnd - playbackTimeRef.current) / timeWindow) * height;

                  // Clamp bottomY to canvas bottom if it is currently playing
                  const isActive = playbackTimeRef.current >= note.time && playbackTimeRef.current <= noteEnd;
                  if (isActive) {
                    bottomY = height;
                    // Spawn particles at key hit point
                    if (isPlayingRef.current && Math.random() < 0.4) {
                      particles.push({
                        x: x + (Math.random() - 0.5) * keyWidth,
                        y: height - 2,
                        vx: (Math.random() - 0.5) * 1.5,
                        vy: -(Math.random() * 2 + 1),
                        color: isBlack ? 0xf59e0b : 0x0ea5e9,
                        alpha: 1.0,
                        size: Math.random() * 3 + 2,
                      });
                    }
                  }

                  const rectHeight = Math.max(8, bottomY - topY);

                  // Draw note flat rect (no roundRect to prevent corner triangulation loops/bugs)
                  graphics.beginPath();
                  graphics.rect(x - keyWidth / 2, topY, keyWidth, rectHeight)
                    .fill({
                      color: isBlack ? 0xf59e0b : 0x0ea5e9, // Amber for black keys, Sky-blue for white
                      alpha: isActive ? 1.0 : 0.75,
                    });

                  // Add a bright border highlights to active notes
                  if (isActive) {
                    graphics.stroke({ width: 1.5, color: 0xffffff });
                  }

                  // Update label position and visibility
                  if (label && !label.destroyed) {
                    label.x = x;
                    label.y = topY + rectHeight / 2;
                    // Only show text if rectHeight is tall enough to fit it cleanly
                    label.visible = rectHeight > 14;
                  }
                } else {
                  if (label && !label.destroyed) {
                    label.visible = false;
                  }
                }
              });

              // 4. Update and Draw Particles
              particles.forEach((p) => {
                p.x += p.vx;
                p.y += p.vy;
                p.alpha -= 0.025; // fade out speed
              });

              particles = particles.filter((p) => p.alpha > 0);

              particles.forEach((p) => {
                graphics.beginPath();
                graphics.circle(p.x, p.y, p.size)
                  .fill({
                    color: p.color,
                    alpha: p.alpha,
                  });
              });
            }

            // 5. Draw target hit line at the bottom
            graphics.beginPath();
            graphics.moveTo(0, height - 1.5);
            graphics.lineTo(width, height - 1.5);
            graphics.stroke({ width: 3, color: 0x404040 });
          } catch (tickErr) {
            console.error("Error in visualizer ticker loop:", tickErr);
          }
        });
      } catch (err) {
        console.error("Failed to initialize PixiJS application:", err);
      }
    };

    initPixi();

    return () => {
      destroyed = true;
      if (app) {
        if (app.renderer) {
          try {
            app.destroy(
              { removeView: false, releaseGlobalResources: true }, // DO NOT delete canvas view from DOM (React owns it)
              { children: true, texture: true, textureSource: true }
            );
          } catch (destroyErr) {
            console.error("Error during PixiJS app destroy:", destroyErr);
          }
        }
        app = null;
        appRef.current = null;
      }
    };
  }, []);

  // Handle Resize updates on canvas size
  useEffect(() => {
    if (appRef.current && appRef.current.renderer) {
      try {
        appRef.current.renderer.resize(dimensions.width, dimensions.height);
      } catch (resizeErr) {
        console.error("Failed to resize PixiJS renderer:", resizeErr);
      }
    }
  }, [dimensions]);

  return (
    <div
      ref={containerRef}
      className="w-full max-w-[1500px] bg-neutral-950 rounded-2xl md:rounded-3xl border border-neutral-800 shadow-md relative overflow-hidden flex items-center justify-center mx-auto mb-4"
      style={{ height: `${dimensions.height}px` }}
    >
      <canvas ref={canvasRef} className="block w-full h-full" />
    </div>
  );
};

export default PianoVisualizer;
