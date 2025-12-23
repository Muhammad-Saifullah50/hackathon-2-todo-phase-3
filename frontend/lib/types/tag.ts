/**
 * Tag-related TypeScript interfaces and types.
 */

export interface Tag {
  id: string;
  name: string;
  color: string;
  created_at: string;
  updated_at?: string;
}

export interface TagWithCount extends Tag {
  task_count: number;
}

export interface TagListResponse {
  tags: TagWithCount[];
}

export interface TagAssignResponse {
  tags: TagWithCount[];
}

export interface CreateTagRequest {
  name: string;
  color: string;
}

export interface UpdateTagRequest {
  name?: string;
  color?: string;
}

export interface TagAssignRequest {
  tag_ids: string[];
}

/**
 * Predefined color palette for tags.
 */
export const TAG_COLORS = [
  "#EF4444", // Red
  "#F97316", // Orange
  "#F59E0B", // Amber
  "#EAB308", // Yellow
  "#84CC16", // Lime
  "#22C55E", // Green
  "#10B981", // Emerald
  "#14B8A6", // Teal
  "#06B6D4", // Cyan
  "#0EA5E9", // Sky
  "#3B82F6", // Blue
  "#6366F1", // Indigo
  "#8B5CF6", // Violet
  "#A855F7", // Purple
  "#D946EF", // Fuchsia
  "#EC4899", // Pink
] as const;

export type TagColor = (typeof TAG_COLORS)[number];
