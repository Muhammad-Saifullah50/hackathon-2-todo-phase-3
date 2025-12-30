"use client";

import { KanbanBoard } from "@/components/kanban/KanbanBoard";

export default function KanbanPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 pt-6 w-full h-[calc(100vh-4rem)] flex flex-col">
      <div className="mb-6 shrink-0">
        <h1 className="text-3xl font-bold">Kanban Board</h1>
        <p className="text-muted-foreground mt-2">
          Organize tasks by status with drag and drop
        </p>
      </div>
      <div className="flex-1 overflow-y-auto overflow-x-hidden min-h-0">
        <KanbanBoard />
      </div>
    </div>
  );
}
