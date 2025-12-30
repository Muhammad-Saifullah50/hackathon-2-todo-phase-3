"use client";

/**
 * MobileProvider Component - Provides mobile-specific UI elements.
 * Includes BottomNav for mobile viewports.
 * These components handle their own visibility based on viewport.
 */

import { BottomNav } from "./BottomNav";

export function MobileProvider() {
  return (
    <>
      <BottomNav />
    </>
  );
}
