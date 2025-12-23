"use client";

import { useEffect, useCallback } from "react";

interface KeyboardShortcutsOptions {
  onCommandPalette?: () => void;
  onNewTask?: () => void;
  onEditTask?: () => void;
  onDeleteTask?: () => void;
  onSearch?: () => void;
  onNavigateUp?: () => void;
  onNavigateDown?: () => void;
  onSelectTask?: () => void;
  enabled?: boolean;
}

/**
 * Hook to register global keyboard shortcuts
 * Prevents shortcuts from firing when user is typing in input/textarea fields
 */
export function useKeyboardShortcuts(options: KeyboardShortcutsOptions) {
  const {
    onCommandPalette,
    onNewTask,
    onEditTask,
    onDeleteTask,
    onSearch,
    onNavigateUp,
    onNavigateDown,
    onSelectTask,
    enabled = true,
  } = options;

  const isTyping = useCallback((target: EventTarget | null): boolean => {
    if (!target || !(target instanceof HTMLElement)) return false;

    const tagName = target.tagName.toLowerCase();
    const isContentEditable = target.isContentEditable;
    const isInput =
      tagName === "input" ||
      tagName === "textarea" ||
      tagName === "select";

    return isInput || isContentEditable;
  }, []);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      const { key, ctrlKey, metaKey, shiftKey } = event;
      const isMod = ctrlKey || metaKey; // Cmd on Mac, Ctrl on Windows/Linux
      const target = event.target;

      // Cmd/Ctrl+K - Open command palette (works everywhere)
      if (isMod && key.toLowerCase() === "k") {
        event.preventDefault();
        onCommandPalette?.();
        return;
      }

      // Don't handle other shortcuts if user is typing
      if (isTyping(target)) {
        return;
      }

      // N - New task
      if (key.toLowerCase() === "n" && !isMod && !shiftKey) {
        event.preventDefault();
        onNewTask?.();
        return;
      }

      // E - Edit task
      if (key.toLowerCase() === "e" && !isMod && !shiftKey) {
        event.preventDefault();
        onEditTask?.();
        return;
      }

      // Delete or Backspace - Delete task
      if (
        (key === "Delete" || key === "Backspace") &&
        !isMod &&
        !shiftKey
      ) {
        event.preventDefault();
        onDeleteTask?.();
        return;
      }

      // / - Focus search
      if (key === "/" && !isMod && !shiftKey) {
        event.preventDefault();
        onSearch?.();
        return;
      }

      // Arrow Up - Navigate up
      if (key === "ArrowUp" && !isMod && !shiftKey) {
        event.preventDefault();
        onNavigateUp?.();
        return;
      }

      // Arrow Down - Navigate down
      if (key === "ArrowDown" && !isMod && !shiftKey) {
        event.preventDefault();
        onNavigateDown?.();
        return;
      }

      // Enter - Select/open task
      if (key === "Enter" && !isMod && !shiftKey) {
        event.preventDefault();
        onSelectTask?.();
        return;
      }
    },
    [
      enabled,
      isTyping,
      onCommandPalette,
      onNewTask,
      onEditTask,
      onDeleteTask,
      onSearch,
      onNavigateUp,
      onNavigateDown,
      onSelectTask,
    ]
  );

  useEffect(() => {
    if (!enabled) return;

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [enabled, handleKeyDown]);
}

/**
 * Hook to get platform-specific modifier key label
 * @returns "⌘" on Mac, "Ctrl" on Windows/Linux
 */
export function useModifierKey(): string {
  const isMac =
    typeof navigator !== "undefined" &&
    navigator.platform.toUpperCase().indexOf("MAC") >= 0;
  return isMac ? "⌘" : "Ctrl";
}

/**
 * Hook to format shortcut display text
 * @param shortcut - Shortcut string (e.g., "Cmd+K", "N", "Delete")
 * @returns Formatted shortcut for current platform
 */
export function useShortcutText(shortcut: string): string {
  const modKey = useModifierKey();

  return shortcut
    .replace("Cmd", modKey)
    .replace("Ctrl", modKey)
    .replace("+", " + ");
}
