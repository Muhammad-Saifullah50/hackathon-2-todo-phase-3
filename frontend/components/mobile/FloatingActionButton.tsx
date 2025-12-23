"use client";

/**
 * FloatingActionButton Component - Fixed FAB for creating new tasks on mobile.
 * Positioned bottom-right, above the bottom navigation.
 * Opens the CreateTaskDialog when tapped.
 */

import { usePathname } from "next/navigation";
import { Plus } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface FloatingActionButtonProps {
  className?: string;
}

/**
 * Trigger haptic feedback for FAB tap.
 */
function triggerHapticFeedback() {
  if (typeof navigator !== "undefined" && "vibrate" in navigator) {
    try {
      navigator.vibrate([25]);
    } catch {
      // Vibration not supported
    }
  }
}

export function FloatingActionButton({ className }: FloatingActionButtonProps) {
  const pathname = usePathname();

  const handleClick = () => {
    triggerHapticFeedback();
    // Dispatch event to open the create task dialog
    window.dispatchEvent(new CustomEvent("open-create-task-dialog"));
  };

  // Don't show on landing page, settings, or desktop
  const hiddenPaths = ["/", "/settings"];
  if (hiddenPaths.includes(pathname)) {
    return null;
  }

  // Hide on desktop - only show on mobile/tablet
  return (
    <>
      <AnimatePresence>
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0, opacity: 0 }}
          transition={{ type: "spring", stiffness: 400, damping: 25 }}
          className={cn(
            "fixed z-50",
            "bottom-20 right-4 sm:bottom-4 sm:right-4",
            "md:hidden", // Hide on desktop (768px and up)
            className
          )}
        >
          <Button
            onClick={handleClick}
            size="icon"
            className={cn(
              "h-14 w-14 rounded-full", // 56px = larger than 44x44 minimum
              "shadow-lg shadow-primary/25",
              "bg-primary hover:bg-primary/90",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            )}
            aria-label="Create new task"
          >
            <motion.div
              whileHover={{ rotate: 90 }}
              whileTap={{ scale: 0.9 }}
              transition={{ type: "spring", stiffness: 400, damping: 25 }}
            >
              <Plus className="h-7 w-7" />
            </motion.div>
          </Button>
        </motion.div>
      </AnimatePresence>

    </>
  );
}
