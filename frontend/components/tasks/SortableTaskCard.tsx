"use client";

/**
 * SortableTaskCard Component - A draggable wrapper for TaskCard using dnd-kit.
 * Enables drag-and-drop reordering of tasks with visual feedback.
 * Supports long-press to drag on mobile devices.
 */

import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical } from "lucide-react";
import { Task } from "@/lib/types/task";
import { TaskCard } from "./TaskCard";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface SortableTaskCardProps {
  task: Task;
  variant?: "list" | "grid";
  searchQuery?: string;
  isDragDisabled?: boolean;
  isSelected?: boolean;
  onSelect?: () => void;
}

export function SortableTaskCard({
  task,
  variant = "list",
  searchQuery = "",
  isDragDisabled = false,
  isSelected = false,
  onSelect,
}: SortableTaskCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: task.id,
    disabled: isDragDisabled,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 1000 : undefined,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cn(
        "flex items-start gap-2 group touch-manipulation",
        isDragging && "shadow-lg",
        isSelected && "ring-2 ring-primary ring-offset-2 rounded-lg"
      )}
      onClick={onSelect}
    >
      {/* Drag Handle */}
      {!isDragDisabled && (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                {...attributes}
                {...listeners}
                className={cn(
                  "mt-4 p-1 cursor-grab rounded hover:bg-muted transition-colors",
                  // Show on hover for desktop, always show with lower opacity for touch
                  "opacity-30 sm:opacity-0 sm:group-hover:opacity-100 sm:focus:opacity-100",
                  isDragging && "cursor-grabbing opacity-100"
                )}
                aria-label="Drag to reorder (long-press on mobile)"
              >
                <GripVertical className="h-4 w-4 text-muted-foreground" />
              </button>
            </TooltipTrigger>
            <TooltipContent side="left" className="hidden sm:block">
              <p>Drag to reorder</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      )}

      {/* Disabled drag indicator */}
      {isDragDisabled && (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="mt-4 p-1 opacity-20 cursor-not-allowed">
                <GripVertical className="h-4 w-4 text-muted-foreground" />
              </div>
            </TooltipTrigger>
            <TooltipContent side="left" className="hidden sm:block">
              <p>Clear filters to reorder</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      )}

      {/* Task Card */}
      <div className="flex-1">
        <TaskCard task={task} variant={variant} searchQuery={searchQuery} />
      </div>
    </div>
  );
}
