"use client";

/**
 * SwipeableTaskCard Component - Wraps TaskCard with swipe gestures for mobile.
 * Swipe left to reveal delete action, swipe right to toggle completion.
 * Uses @use-gesture/react for smooth, performant touch interactions.
 */

import { useState, useCallback, useRef } from "react";
import { motion, useMotionValue, useTransform, animate } from "framer-motion";
import { useDrag } from "@use-gesture/react";
import { Task } from "@/lib/types/task";
import { TaskCard } from "@/components/tasks/TaskCard";
import { Trash2, Check, X } from "lucide-react";
import { useToggleTask, useDeleteTask } from "@/hooks/useTasks";
import { useCelebration } from "@/components/tasks/CelebrationAnimation";
import { cn } from "@/lib/utils";

interface SwipeableTaskCardProps {
  task: Task;
  variant?: "list" | "grid";
  searchQuery?: string;
  disabled?: boolean;
}

const SWIPE_THRESHOLD = 80; // Minimum swipe distance to trigger action
const MAX_SWIPE = 100; // Maximum swipe distance

/**
 * Trigger haptic feedback if supported by the device.
 * Uses the Vibration API for Android and attempts to use
 * more subtle patterns for different actions.
 */
function triggerHapticFeedback(intensity: "light" | "medium" | "heavy" = "medium") {
  if (typeof navigator !== "undefined" && "vibrate" in navigator) {
    const patterns = {
      light: [10],
      medium: [25],
      heavy: [50],
    };
    try {
      navigator.vibrate(patterns[intensity]);
    } catch {
      // Vibration not supported or not allowed
    }
  }
}

export function SwipeableTaskCard({
  task,
  variant = "list",
  searchQuery = "",
  disabled = false,
}: SwipeableTaskCardProps) {
  const [isSwipingLeft, setIsSwipingLeft] = useState(false);
  const [isSwipingRight, setIsSwipingRight] = useState(false);
  const hasTriggeredFeedback = useRef(false);

  const { mutate: toggleTask } = useToggleTask();
  const { mutate: deleteTask } = useDeleteTask();
  const { triggerCelebration, CelebrationComponent } = useCelebration();

  const isCompleted = task.status === "completed";

  // Motion value for tracking swipe position
  const x = useMotionValue(0);

  // Transform values for background indicators
  const leftOpacity = useTransform(x, [-SWIPE_THRESHOLD, 0], [1, 0]);
  const rightOpacity = useTransform(x, [0, SWIPE_THRESHOLD], [0, 1]);
  const leftScale = useTransform(x, [-MAX_SWIPE, -SWIPE_THRESHOLD], [1.2, 1]);
  const rightScale = useTransform(x, [SWIPE_THRESHOLD, MAX_SWIPE], [1, 1.2]);
  const borderOpacity = useTransform(x, [-20, 0, 20], [1, 0, 1]);

  // Handle the swipe action completion
  const handleSwipeComplete = useCallback(
    (direction: "left" | "right") => {
      triggerHapticFeedback("heavy");

      if (direction === "left") {
        // Delete action
        deleteTask(task.id);
      } else {
        // Toggle completion
        if (!isCompleted) {
          triggerCelebration();
        }
        toggleTask(task.id);
      }

      // Reset position
      animate(x, 0, { type: "spring", stiffness: 400, damping: 30 });
    },
    [deleteTask, isCompleted, task.id, toggleTask, triggerCelebration, x]
  );

  // Drag gesture handler
  const bind = useDrag(
    ({ active, movement: [mx], cancel }) => {
      if (disabled) {
        cancel();
        return;
      }

      // Determine swipe direction
      const newIsSwipingLeft = mx < -20;
      const newIsSwipingRight = mx > 20;

      // Update visual states
      if (newIsSwipingLeft !== isSwipingLeft) setIsSwipingLeft(newIsSwipingLeft);
      if (newIsSwipingRight !== isSwipingRight) setIsSwipingRight(newIsSwipingRight);

      // Trigger haptic feedback when reaching threshold
      if (active && Math.abs(mx) >= SWIPE_THRESHOLD && !hasTriggeredFeedback.current) {
        triggerHapticFeedback("medium");
        hasTriggeredFeedback.current = true;
      }

      if (active && Math.abs(mx) < SWIPE_THRESHOLD) {
        hasTriggeredFeedback.current = false;
      }

      if (active) {
        // Limit the swipe distance with rubber-band effect
        const clampedX = Math.max(-MAX_SWIPE, Math.min(MAX_SWIPE, mx));
        const rubberBandX =
          Math.abs(mx) > MAX_SWIPE
            ? clampedX + (mx - clampedX) * 0.2
            : mx;
        x.set(rubberBandX);
      } else {
        // On release
        if (Math.abs(mx) >= SWIPE_THRESHOLD) {
          handleSwipeComplete(mx < 0 ? "left" : "right");
        } else {
          // Spring back to center
          animate(x, 0, { type: "spring", stiffness: 400, damping: 30 });
        }

        // Reset states
        setIsSwipingLeft(false);
        setIsSwipingRight(false);
        hasTriggeredFeedback.current = false;
      }
    },
    {
      axis: "x",
      filterTaps: true,
      rubberband: true,
    }
  );

  return (
    <div className="relative overflow-hidden rounded-lg">
      {/* Celebration Animation */}
      <CelebrationComponent />

      {/* Left swipe background (Delete - Red) */}
      <motion.div
        className={cn(
          "absolute inset-y-0 right-0 flex items-center justify-end px-4",
          "bg-destructive text-destructive-foreground rounded-lg"
        )}
        style={{
          opacity: leftOpacity,
          width: "100%",
        }}
      >
        <motion.div
          style={{ scale: leftScale }}
          className="flex flex-col items-center gap-1"
        >
          <Trash2 className="h-6 w-6" />
          <span className="text-xs font-medium">Delete</span>
        </motion.div>
      </motion.div>

      {/* Right swipe background (Complete/Uncomplete - Green/Gray) */}
      <motion.div
        className={cn(
          "absolute inset-y-0 left-0 flex items-center justify-start px-4 rounded-lg",
          isCompleted
            ? "bg-gray-500 text-white"
            : "bg-green-500 text-white"
        )}
        style={{
          opacity: rightOpacity,
          width: "100%",
        }}
      >
        <motion.div
          style={{ scale: rightScale }}
          className="flex flex-col items-center gap-1"
        >
          {isCompleted ? (
            <>
              <X className="h-6 w-6" />
              <span className="text-xs font-medium">Undo</span>
            </>
          ) : (
            <>
              <Check className="h-6 w-6" />
              <span className="text-xs font-medium">Done</span>
            </>
          )}
        </motion.div>
      </motion.div>

      {/* Swipeable Card */}
      <motion.div
        style={{
          x,
          touchAction: "pan-y", // Allow vertical scrolling
        }}
        className="relative bg-background cursor-grab active:cursor-grabbing"
      >
        <div {...bind()}>
          <TaskCard task={task} variant={variant} searchQuery={searchQuery} />
        </div>

        {/* Visual indicator border when swiping */}
        <motion.div
          className={cn(
            "absolute inset-0 pointer-events-none rounded-lg border-2 transition-colors",
            isSwipingLeft && "border-destructive",
            isSwipingRight && (isCompleted ? "border-gray-500" : "border-green-500"),
            !isSwipingLeft && !isSwipingRight && "border-transparent"
          )}
          style={{
            opacity: borderOpacity,
          }}
        />
      </motion.div>
    </div>
  );
}
