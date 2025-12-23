"use client";

import { cn } from "@/lib/utils";
import { useTags } from "@/hooks/useTags";
import { Skeleton } from "@/components/ui/skeleton";

interface TagFiltersProps {
  selectedTagIds: string[];
  onTagFilterChange: (tagIds: string[]) => void;
  className?: string;
}

/**
 * A horizontal filter bar for filtering tasks by tags.
 * Displays all available tags as clickable badges.
 */
export function TagFilters({
  selectedTagIds,
  onTagFilterChange,
  className,
}: TagFiltersProps) {
  const { data: tagsData, isLoading } = useTags();

  const tags = tagsData?.data?.tags || [];

  if (isLoading) {
    return (
      <div className={cn("flex flex-wrap gap-1.5", className)}>
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-6 w-16 rounded-md" />
        ))}
      </div>
    );
  }

  if (tags.length === 0) {
    return null;
  }

  const handleTagClick = (tagId: string) => {
    if (selectedTagIds.includes(tagId)) {
      onTagFilterChange(selectedTagIds.filter((id) => id !== tagId));
    } else {
      onTagFilterChange([...selectedTagIds, tagId]);
    }
  };

  const handleClearAll = () => {
    onTagFilterChange([]);
  };

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-muted-foreground">
          Filter by tags
        </span>
        {selectedTagIds.length > 0 && (
          <button
            type="button"
            onClick={handleClearAll}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            Clear filters
          </button>
        )}
      </div>

      <div className="flex flex-wrap gap-1.5">
        {tags.map((tag) => {
          const isSelected = selectedTagIds.includes(tag.id);

          return (
            <button
              key={tag.id}
              type="button"
              onClick={() => handleTagClick(tag.id)}
              className={cn(
                "inline-flex items-center gap-1 rounded-md font-medium transition-all px-2 py-0.5 text-xs",
                isSelected
                  ? "ring-2 ring-offset-1 ring-primary"
                  : "opacity-70 hover:opacity-100"
              )}
              style={{
                backgroundColor: tag.color,
                color: getContrastColor(tag.color),
              }}
              aria-pressed={isSelected}
              aria-label={`Filter by ${tag.name}${isSelected ? " (active)" : ""}`}
            >
              <span className="truncate max-w-[100px]">{tag.name}</span>
              <span
                className="rounded px-1 text-xs opacity-80"
                style={{
                  backgroundColor:
                    getContrastColor(tag.color) === "#FFFFFF"
                      ? "rgba(255,255,255,0.2)"
                      : "rgba(0,0,0,0.1)",
                }}
              >
                {tag.task_count}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

/**
 * Calculate contrasting text color based on background.
 */
function getContrastColor(hexColor: string): string {
  const hex = hexColor.replace("#", "");
  const r = parseInt(hex.slice(0, 2), 16);
  const g = parseInt(hex.slice(2, 4), 16);
  const b = parseInt(hex.slice(4, 6), 16);
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.5 ? "#000000" : "#FFFFFF";
}
