"use client";

import { CalendarDays, AlertTriangle, Clock, CalendarCheck, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useQuickFilters } from "@/hooks/useSearch";

interface QuickFiltersProps {
  activeFilter?: string;
  onFilterChange: (filterId: string) => void;
  className?: string;
}

/**
 * QuickFilters component displays predefined filter chips with task counts.
 * Allows users to quickly filter tasks by Today, This Week, High Priority, or Overdue.
 */
export function QuickFilters({
  activeFilter,
  onFilterChange,
  className,
}: QuickFiltersProps) {
  const { data, isLoading, error } = useQuickFilters();
  const filters = data?.data?.filters || [];

  // Icon mapping for filter IDs
  const filterIcons: Record<string, React.ReactNode> = {
    today: <CalendarCheck className="h-3.5 w-3.5" />,
    this_week: <CalendarDays className="h-3.5 w-3.5" />,
    high_priority: <AlertTriangle className="h-3.5 w-3.5" />,
    overdue: <Clock className="h-3.5 w-3.5" />,
  };

  // Color mapping for filter IDs
  const filterColors: Record<string, string> = {
    today: "text-blue-600 dark:text-blue-400",
    this_week: "text-purple-600 dark:text-purple-400",
    high_priority: "text-red-600 dark:text-red-400",
    overdue: "text-orange-600 dark:text-orange-400",
  };

  if (error) {
    return null; // Silently fail - quick filters are not critical
  }

  return (
    <div
      className={cn("flex flex-wrap items-center gap-2", className)}
      role="group"
      aria-label="Quick filters"
    >
      {isLoading ? (
        // Loading skeleton
        <>
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-8 w-24 animate-pulse rounded-full bg-muted"
            />
          ))}
        </>
      ) : (
        filters.map((filter) => {
          const isActive = activeFilter === filter.id;

          return (
            <Button
              key={filter.id}
              variant={isActive ? "default" : "outline"}
              size="sm"
              className={cn(
                "h-8 gap-1.5 rounded-full px-3 text-sm font-medium transition-all",
                isActive
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : cn(
                      "border-dashed hover:border-solid hover:bg-accent",
                      filterColors[filter.id]
                    )
              )}
              onClick={() => onFilterChange(filter.id)}
              aria-pressed={isActive}
            >
              {filterIcons[filter.id]}
              <span>{filter.label}</span>
              <Badge
                variant={isActive ? "secondary" : "outline"}
                className={cn(
                  "ml-0.5 h-5 min-w-[1.25rem] px-1.5 text-xs",
                  isActive
                    ? "bg-primary-foreground/20 text-primary-foreground"
                    : "bg-muted/50"
                )}
              >
                {filter.count}
              </Badge>
            </Button>
          );
        })
      )}
    </div>
  );
}

/**
 * Compact version of QuickFilters for mobile or sidebar use.
 */
export function QuickFiltersCompact({
  activeFilter,
  onFilterChange,
  className,
}: QuickFiltersProps) {
  const { data, isLoading } = useQuickFilters();
  const filters = data?.data?.filters || [];

  // Icon mapping for filter IDs
  const filterIcons: Record<string, React.ReactNode> = {
    today: <CalendarCheck className="h-4 w-4" />,
    this_week: <CalendarDays className="h-4 w-4" />,
    high_priority: <AlertTriangle className="h-4 w-4" />,
    overdue: <Clock className="h-4 w-4" />,
  };

  if (isLoading) {
    return (
      <div className="flex items-center gap-1">
        <Loader2 className="h-4 w-4 animate-spin" />
      </div>
    );
  }

  return (
    <div
      className={cn("flex items-center gap-1", className)}
      role="group"
      aria-label="Quick filters"
    >
      {filters.map((filter) => {
        const isActive = activeFilter === filter.id;

        return (
          <Button
            key={filter.id}
            variant="ghost"
            size="icon"
            className={cn(
              "relative h-8 w-8",
              isActive && "bg-accent text-accent-foreground"
            )}
            onClick={() => onFilterChange(filter.id)}
            aria-pressed={isActive}
            aria-label={`${filter.label} (${filter.count})`}
          >
            {filterIcons[filter.id]}
            {filter.count > 0 && (
              <span
                className={cn(
                  "absolute -right-0.5 -top-0.5 flex h-4 min-w-[1rem] items-center justify-center rounded-full px-1 text-[10px] font-medium",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground"
                )}
              >
                {filter.count > 99 ? "99+" : filter.count}
              </span>
            )}
          </Button>
        );
      })}
    </div>
  );
}

/**
 * Filter summary showing active filters count and clear button.
 */
export function FilterSummary({
  activeFilterCount,
  onClearAll,
  className,
}: {
  activeFilterCount: number;
  onClearAll: () => void;
  className?: string;
}) {
  if (activeFilterCount === 0) {
    return null;
  }

  return (
    <div className={cn("flex items-center gap-2 text-sm text-muted-foreground", className)}>
      <span>
        {activeFilterCount} filter{activeFilterCount !== 1 ? "s" : ""} active
      </span>
      <Button
        variant="ghost"
        size="sm"
        className="h-auto px-2 py-0.5 text-xs"
        onClick={onClearAll}
      >
        Clear all
      </Button>
    </div>
  );
}
