"use client";

import { cn } from "@/lib/utils";
import type { Task } from "@/lib/types/task";

interface CalendarTaskCardProps {
  task: Task;
}

const priorityColors = {
  high: "bg-red-500/80 hover:bg-red-500",
  medium: "bg-yellow-500/80 hover:bg-yellow-500",
  low: "bg-blue-500/80 hover:bg-blue-500",
};

const priorityTextColors = {
  high: "text-red-50",
  medium: "text-yellow-50",
  low: "text-blue-50",
};

export function CalendarTaskCard({ task }: CalendarTaskCardProps) {
  const priorityColor = priorityColors[task.priority] || priorityColors.medium;
  const textColor = priorityTextColors[task.priority] || priorityTextColors.medium;

  const handleDragStart = (e: React.DragEvent) => {
    e.stopPropagation();
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("taskId", task.id);
  };

  return (
    <div
      draggable
      onDragStart={handleDragStart}
      className={cn(
        "text-xs font-medium py-1 px-2 rounded truncate transition-colors cursor-grab active:cursor-grabbing",
        priorityColor,
        textColor,
        task.status === "completed" && "opacity-50 line-through"
      )}
      title={task.title}
    >
      {task.title}
    </div>
  );
}
