"use client";

import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Tag as TaskTag } from "@/lib/types/task";
import type { Tag, TagWithCount } from "@/lib/types/tag";

// Allow both Task's Tag type and our extended Tag type
type AnyTag = Tag | TagWithCount | TaskTag;

interface TagBadgeProps {
  tag: AnyTag;
  size?: "sm" | "md";
  showCount?: boolean;
  onRemove?: () => void;
  onClick?: () => void;
  className?: string;
}

/**
 * A colored badge component for displaying a tag.
 * Can optionally show a remove button and task count.
 */
export function TagBadge({
  tag,
  size = "sm",
  showCount = false,
  onRemove,
  onClick,
  className,
}: TagBadgeProps) {
  // Calculate contrasting text color based on background
  const getContrastColor = (hexColor: string) => {
    const hex = hexColor.replace("#", "");
    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    // Calculate relative luminance
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    return luminance > 0.5 ? "#000000" : "#FFFFFF";
  };

  const textColor = getContrastColor(tag.color);
  const taskCount = "task_count" in tag ? tag.task_count : undefined;

  return (
    <span
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      onClick={onClick}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onClick();
              }
            }
          : undefined
      }
      className={cn(
        "inline-flex items-center gap-1 rounded-md font-medium transition-all",
        size === "sm" && "px-2 py-0.5 text-xs",
        size === "md" && "px-2.5 py-1 text-sm",
        onClick && "cursor-pointer hover:opacity-80 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-1",
        className
      )}
      style={{
        backgroundColor: tag.color,
        color: textColor,
      }}
      aria-label={`Tag: ${tag.name}${taskCount !== undefined ? `, ${taskCount} tasks` : ""}`}
    >
      <span className="truncate max-w-[120px]">{tag.name}</span>

      {showCount && taskCount !== undefined && (
        <span
          className="rounded px-1 text-xs opacity-80"
          style={{
            backgroundColor: textColor === "#FFFFFF" ? "rgba(255,255,255,0.2)" : "rgba(0,0,0,0.1)",
          }}
        >
          {taskCount}
        </span>
      )}

      {onRemove && (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="ml-0.5 rounded-sm hover:opacity-70 focus:outline-none focus:ring-1 focus:ring-current"
          aria-label={`Remove ${tag.name} tag`}
        >
          <X className={cn(size === "sm" ? "h-3 w-3" : "h-3.5 w-3.5")} />
        </button>
      )}
    </span>
  );
}

/**
 * A list of tag badges, with optional "and N more" indicator.
 */
interface TagBadgeListProps {
  tags: AnyTag[];
  maxVisible?: number;
  size?: "sm" | "md";
  onRemove?: (tagId: string) => void;
  onTagClick?: (tag: AnyTag) => void;
  className?: string;
}

export function TagBadgeList({
  tags,
  maxVisible = 3,
  size = "sm",
  onRemove,
  onTagClick,
  className,
}: TagBadgeListProps) {
  if (tags.length === 0) return null;

  const visibleTags = tags.slice(0, maxVisible);
  const hiddenCount = tags.length - maxVisible;

  return (
    <div className={cn("flex flex-wrap items-center gap-1", className)}>
      {visibleTags.map((tag) => (
        <TagBadge
          key={tag.id}
          tag={tag}
          size={size}
          onRemove={onRemove ? () => onRemove(tag.id) : undefined}
          onClick={onTagClick ? () => onTagClick(tag) : undefined}
        />
      ))}
      {hiddenCount > 0 && (
        <span className="text-xs text-muted-foreground px-1">
          +{hiddenCount} more
        </span>
      )}
    </div>
  );
}
