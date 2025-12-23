"use client";

import { Calendar } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { getDueDateStatus, formatDueDate } from "@/lib/date-utils";
import { cn } from "@/lib/utils";

interface DueDateBadgeProps {
  dueDate: string | null;
  className?: string;
  showIcon?: boolean;
}

/**
 * Due date badge with color-coded styling based on due date status.
 * Colors: red (overdue), orange (due soon), blue (upcoming), gray (none).
 * Displays relative time: "Due tomorrow", "3 days overdue", etc.
 */
export function DueDateBadge({ dueDate, className, showIcon = true }: DueDateBadgeProps) {
  if (!dueDate) {
    return null;
  }

  const status = getDueDateStatus(dueDate);
  const displayText = formatDueDate(dueDate);

  // Use static Tailwind classes that can be properly detected
  const colorClasses = {
    overdue: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400 border-red-200 dark:border-red-800",
    due_soon: "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400 border-orange-200 dark:border-orange-800",
    upcoming: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200 dark:border-blue-800",
    none: "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400 border-gray-200 dark:border-gray-800",
  };

  return (
    <Badge variant="outline" className={cn("text-xs font-normal", colorClasses[status], className)}>
      {showIcon && <Calendar className="mr-1 h-3 w-3" />}
      {displayText}
    </Badge>
  );
}
