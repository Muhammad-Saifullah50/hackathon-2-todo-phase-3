"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface ConfettiPiece {
  id: number;
  x: number;
  y: number;
  color: string;
  rotation: number;
  scale: number;
}

interface CelebrationAnimationProps {
  isActive: boolean;
  onComplete?: () => void;
}

const colors = [
  "#FF6B6B", // Red
  "#4ECDC4", // Teal
  "#FFE66D", // Yellow
  "#95E1D3", // Mint
  "#F38181", // Coral
  "#AA96DA", // Purple
  "#6C5CE7", // Indigo
  "#00B894", // Green
];

/**
 * Celebration animation component with confetti effect.
 * Triggers when a task is marked as completed.
 */
export function CelebrationAnimation({ isActive, onComplete }: CelebrationAnimationProps) {
  const [confetti, setConfetti] = useState<ConfettiPiece[]>([]);

  useEffect(() => {
    if (isActive) {
      // Generate confetti pieces
      const pieces: ConfettiPiece[] = Array.from({ length: 20 }, (_, i) => ({
        id: i,
        x: Math.random() * 100 - 50, // -50 to 50
        y: Math.random() * -100 - 50, // -50 to -150
        color: colors[Math.floor(Math.random() * colors.length)],
        rotation: Math.random() * 720 - 360, // -360 to 360
        scale: Math.random() * 0.5 + 0.5, // 0.5 to 1
      }));
      setConfetti(pieces);

      // Clear confetti after animation
      const timeout = setTimeout(() => {
        setConfetti([]);
        onComplete?.();
      }, 1500);

      return () => clearTimeout(timeout);
    }
  }, [isActive, onComplete]);

  return (
    <AnimatePresence>
      {confetti.length > 0 && (
        <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
          {confetti.map((piece) => (
            <motion.div
              key={piece.id}
              className="absolute left-1/2 top-1/2"
              initial={{
                opacity: 1,
                x: 0,
                y: 0,
                scale: 0,
                rotate: 0,
              }}
              animate={{
                opacity: [1, 1, 0],
                x: piece.x,
                y: piece.y,
                scale: piece.scale,
                rotate: piece.rotation,
              }}
              exit={{ opacity: 0 }}
              transition={{
                duration: 1.2,
                ease: "easeOut",
              }}
            >
              <div
                className="w-3 h-3 rounded-sm"
                style={{ backgroundColor: piece.color }}
              />
            </motion.div>
          ))}
        </div>
      )}
    </AnimatePresence>
  );
}

/**
 * Hook to trigger celebration animation.
 * Returns a trigger function and the animation component.
 */
export function useCelebration() {
  const [isActive, setIsActive] = useState(false);

  const triggerCelebration = () => {
    setIsActive(true);
  };

  const handleComplete = () => {
    setIsActive(false);
  };

  return {
    isActive,
    triggerCelebration,
    CelebrationComponent: () => (
      <CelebrationAnimation isActive={isActive} onComplete={handleComplete} />
    ),
  };
}
