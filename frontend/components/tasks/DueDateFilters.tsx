"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Calendar, AlertCircle, CalendarX2 } from "lucide-react";

interface DueDateFiltersProps {
  activeFilter: string | null;
  onFilterChange: (filter: string | null) => void;
  className?: string;
}

const filters = [
  {
    value: "today",
    label: "Today",
    icon: Calendar,
    color: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
  },
  {
    value: "this_week",
    label: "This Week",
    icon: Calendar,
    color: "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400",
  },
  {
    value: "overdue",
    label: "Overdue",
    icon: AlertCircle,
    color: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
  },
  {
    value: "no_due_date",
    label: "No Due Date",
    icon: CalendarX2,
    color: "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400",
  },
];

/**
 * Due date filter chips component.
 * Quick filter buttons for Today, This Week, Overdue, and No Due Date.
 */
export function DueDateFilters({
  activeFilter,
  onFilterChange,
  className,
}: DueDateFiltersProps) {
  const handleFilterClick = (filterValue: string) => {
    // Toggle off if clicking the same filter
    if (activeFilter === filterValue) {
      onFilterChange(null);
    } else {
      onFilterChange(filterValue);
    }
  };

  return (
    <div className={cn("flex flex-wrap gap-2", className)}>
      {filters.map((filter) => {
        const Icon = filter.icon;
        const isActive = activeFilter === filter.value;

        return (
          <Badge
            key={filter.value}
            variant={isActive ? "default" : "outline"}
            className={cn(
              "cursor-pointer transition-all hover:scale-105",
              isActive ? filter.color : "hover:bg-accent",
              "flex items-center gap-1.5 px-3 py-1.5"
            )}
            onClick={() => handleFilterClick(filter.value)}
          >
            <Icon className="h-3.5 w-3.5" />
            {filter.label}
          </Badge>
        );
      })}
    </div>
  );
}
