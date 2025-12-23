"use client";

/**
 * MobileProvider Component - Provides mobile-specific UI elements.
 * Includes BottomNav and FloatingActionButton for mobile viewports.
 * These components handle their own visibility based on viewport.
 */

import { BottomNav } from "./BottomNav";
import { FloatingActionButton } from "./FloatingActionButton";

export function MobileProvider() {
  return (
    <>
      <BottomNav />
      <FloatingActionButton />
    </>
  );
}
