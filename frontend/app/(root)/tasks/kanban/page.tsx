"use client";

import { KanbanBoard } from "@/components/kanban/KanbanBoard";

export default function KanbanPage() {
  return (
    <div className="max-w-7xl mx-auto p-6 w-full">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Kanban Board</h1>
        <p className="text-muted-foreground mt-2">
          Organize tasks by status with drag and drop
        </p>
      </div>
      <KanbanBoard />
    </div>
  );
}
