import React from "react";
import { Badge } from "@/components/ui/badge";
import { Subtask } from "@/lib/types/task";

interface SubtaskProgressProps {
  subtasks: Subtask[];
}

export function SubtaskProgress({ subtasks }: SubtaskProgressProps) {
  if (!subtasks || subtasks.length === 0) {
    return null; // Don't show progress if there are no subtasks
  }

  const completedCount = subtasks.filter(subtask => subtask.is_completed).length;
  const totalCount = subtasks.length;
  const percentage = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  // Determine badge variant based on completion percentage
  let variant: "default" | "secondary" | "destructive" | "outline" = "secondary";
  let badgeClassName = "text-xs";

  if (percentage === 100) {
    variant = "default";
    badgeClassName = "text-xs bg-green-500 hover:bg-green-600"; // Green for completed
  } else if (percentage > 0) {
    variant = "default"; // Default color for in-progress
  }

  return (
    <div className="flex items-center gap-2 text-sm">
      <Badge variant={variant} className={badgeClassName}>
        {completedCount}/{totalCount} ({percentage}%)
      </Badge>
      <div className="h-2 flex-1 rounded-full overflow-hidden bg-muted">
        <div 
          className="h-full bg-primary transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}