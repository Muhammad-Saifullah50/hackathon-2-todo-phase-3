"use client";

import { format } from "date-fns";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { CalendarTaskCard } from "./CalendarTaskCard";
import type { Task } from "@/lib/types/task";

interface CalendarDayCellProps {
  date: Date;
  tasks: Task[];
  isCurrentMonth: boolean;
  isSelected: boolean;
  isToday: boolean;
  onClick: () => void;
  onTaskDrop?: (taskId: string, newDate: Date) => void;
}

const MAX_VISIBLE_TASKS = 3;

export function CalendarDayCell({
  date,
  tasks,
  isCurrentMonth,
  isSelected,
  isToday,
  onClick,
  onTaskDrop,
}: CalendarDayCellProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const dayNumber = format(date, "d");
  const visibleTasks = tasks.slice(0, MAX_VISIBLE_TASKS);
  const hiddenCount = tasks.length - MAX_VISIBLE_TASKS;

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const taskId = e.dataTransfer.getData("taskId");
    if (taskId && onTaskDrop) {
      onTaskDrop(taskId, date);
    }
  };

  return (
    <div
      onClick={onClick}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={cn(
        "min-h-[120px] border rounded-lg p-2 cursor-pointer transition-all hover:shadow-md",
        isCurrentMonth ? "bg-background" : "bg-muted/30",
        isSelected && "ring-2 ring-primary",
        isToday && "bg-primary/5 border-primary",
        isDragOver && "bg-primary/10 border-primary border-2"
      )}
    >
      {/* Day number */}
      <div
        className={cn(
          "text-sm font-medium mb-2",
          isToday && "inline-flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground",
          !isCurrentMonth && "text-muted-foreground"
        )}
      >
        {dayNumber}
      </div>

      {/* Task badges */}
      <div className="space-y-1">
        {visibleTasks.map((task) => (
          <CalendarTaskCard key={task.id} task={task} />
        ))}

        {/* Show "+N more" badge if there are hidden tasks */}
        {hiddenCount > 0 && (
          <div className="text-xs text-muted-foreground font-medium py-1 px-2 bg-muted/50 rounded">
            +{hiddenCount} more
          </div>
        )}
      </div>
    </div>
  );
}
