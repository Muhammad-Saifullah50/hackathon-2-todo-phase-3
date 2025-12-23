"use client";

import { useState, useCallback } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";
import { CommandPalette } from "@/components/ui/command-palette";

interface KeyboardShortcutsProviderProps {
  children: React.ReactNode;
}

export function KeyboardShortcutsProvider({
  children,
}: KeyboardShortcutsProviderProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);

  const handleNewTask = useCallback(() => {
    // Dispatch custom event that CreateTaskDialog can listen to
    window.dispatchEvent(new CustomEvent("open-create-task-dialog"));
  }, []);

  const handleEditTask = useCallback(() => {
    // Dispatch custom event that EditTaskDialog can listen to
    window.dispatchEvent(new CustomEvent("open-edit-task-dialog"));
  }, []);

  const handleDeleteTask = useCallback(() => {
    // Dispatch custom event for task deletion
    window.dispatchEvent(new CustomEvent("delete-selected-task"));
  }, []);

  const handleSearch = useCallback(() => {
    // Focus search input if on tasks page, otherwise navigate to tasks
    if (pathname === "/tasks") {
      const searchInput = document.querySelector(
        'input[placeholder*="Search"]'
      ) as HTMLInputElement;
      if (searchInput) {
        searchInput.focus();
      }
    } else {
      router.push("/tasks");
    }
  }, [pathname, router]);

  const handleNavigateUp = useCallback(() => {
    window.dispatchEvent(new CustomEvent("navigate-task-up"));
  }, []);

  const handleNavigateDown = useCallback(() => {
    window.dispatchEvent(new CustomEvent("navigate-task-down"));
  }, []);

  const handleSelectTask = useCallback(() => {
    window.dispatchEvent(new CustomEvent("select-task"));
  }, []);

  const handleApplyFilter = useCallback(
    (filter: string) => {
      router.push(`/tasks?filter=${filter}`);
    },
    [router]
  );

  useKeyboardShortcuts({
    onCommandPalette: () => setCommandPaletteOpen(true),
    onNewTask: handleNewTask,
    onEditTask: handleEditTask,
    onDeleteTask: handleDeleteTask,
    onSearch: handleSearch,
    onNavigateUp: handleNavigateUp,
    onNavigateDown: handleNavigateDown,
    onSelectTask: handleSelectTask,
    enabled: true,
  });

  return (
    <>
      {children}
      <CommandPalette
        open={commandPaletteOpen}
        onOpenChange={setCommandPaletteOpen}
        onNewTask={handleNewTask}
        onApplyFilter={handleApplyFilter}
      />
    </>
  );
}
