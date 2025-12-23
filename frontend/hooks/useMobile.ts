"use client";

/**
 * Mobile detection hooks for responsive behavior.
 * Uses window.matchMedia for accurate, SSR-safe detection.
 */

import { useState, useEffect } from "react";

/**
 * Check if the current viewport is mobile (< 768px).
 * Returns false during SSR to avoid hydration mismatches.
 */
export function useIsMobile(): boolean {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    // Only run on client
    if (typeof window === "undefined") return;

    const mediaQuery = window.matchMedia("(max-width: 767px)");

    // Set initial value
    setIsMobile(mediaQuery.matches);

    // Listen for changes
    const handler = (event: MediaQueryListEvent) => {
      setIsMobile(event.matches);
    };

    mediaQuery.addEventListener("change", handler);

    return () => {
      mediaQuery.removeEventListener("change", handler);
    };
  }, []);

  return isMobile;
}

/**
 * Check if the current viewport is tablet (768px - 1024px).
 */
export function useIsTablet(): boolean {
  const [isTablet, setIsTablet] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const mediaQuery = window.matchMedia(
      "(min-width: 768px) and (max-width: 1024px)"
    );

    setIsTablet(mediaQuery.matches);

    const handler = (event: MediaQueryListEvent) => {
      setIsTablet(event.matches);
    };

    mediaQuery.addEventListener("change", handler);

    return () => {
      mediaQuery.removeEventListener("change", handler);
    };
  }, []);

  return isTablet;
}

/**
 * Check if the device is a touch device.
 * Note: This is a heuristic and may not be 100% accurate.
 */
export function useIsTouchDevice(): boolean {
  const [isTouch, setIsTouch] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;

    // Check for touch support
    const hasTouch =
      "ontouchstart" in window ||
      navigator.maxTouchPoints > 0 ||
      // @ts-expect-error - msMaxTouchPoints is IE-specific
      navigator.msMaxTouchPoints > 0;

    setIsTouch(hasTouch);
  }, []);

  return isTouch;
}

/**
 * Combined mobile detection with touch support.
 * Returns true if viewport is mobile OR device is touch-enabled on small screens.
 */
export function useMobileExperience(): {
  isMobile: boolean;
  isTablet: boolean;
  isTouch: boolean;
  showMobileUI: boolean;
} {
  const isMobile = useIsMobile();
  const isTablet = useIsTablet();
  const isTouch = useIsTouchDevice();

  // Show mobile UI if viewport is mobile, or if it's a touch tablet
  const showMobileUI = isMobile || (isTablet && isTouch);

  return {
    isMobile,
    isTablet,
    isTouch,
    showMobileUI,
  };
}
