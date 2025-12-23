/**
 * Task-related TypeScript types matching the backend API.
 * Generated based on the backend models and OpenAPI schema.
 */

export type TaskStatus = "pending" | "completed";

export type TaskPriority = "low" | "medium" | "high";

export interface Tag {
  id: string;
  name: string;
  color: string;
  created_at: string;
}

export interface Subtask {
  id: string;
  task_id: string;
  description: string;
  is_completed: boolean;
  order_index: number;
}

export interface SubtaskListResponse {
  subtasks: Subtask[];
  total_count: number;
  completed_count: number;
  pending_count: number;
  completion_percentage?: number;
}

export interface RecurrencePattern {
  id: string;
  frequency: "daily" | "weekly" | "monthly" | "custom";
  interval: number;
  days_of_week?: number[];
  day_of_month?: number;
  end_date?: string;
  next_occurrence_date: string;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  user_id: string;
  due_date: string | null;
  notes: string | null;
  manual_order: number | null;
  template_id?: string | null;
  recurrence_pattern_id?: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  deleted_at: string | null;
  tags?: Tag[];
  subtasks?: Subtask[];
  recurrence_pattern?: RecurrencePattern | null;
}

export interface CreateTaskRequest {
  title: string;
  description?: string | null;
  priority?: TaskPriority;
  due_date?: string | null;
  notes?: string | null;
}

export interface StandardizedResponse<T> {
  success: boolean;
  message: string;
  data?: T;
  meta?: Record<string, unknown>;
}

export interface ErrorDetail {
  code: string;
  message: string;
  field?: string;
}

export interface ErrorResponse {
  success: false;
  error: ErrorDetail;
  details?: Array<{
    field: string;
    message: string;
  }>;
}

/**
 * Task metadata with count statistics.
 */
export interface TaskMetadata {
  total_pending: number;
  total_completed: number;
  total_active: number;
  total_deleted: number;
}

/**
 * Pagination information for task lists.
 */
export interface PaginationInfo {
  page: number;
  limit: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

/**
 * Task list response with metadata and pagination.
 */
export interface TaskListResponse {
  tasks: Task[];
  metadata: TaskMetadata;
  pagination: PaginationInfo;
}

/**
 * Query parameters for fetching tasks.
 */
export interface TaskQueryParams {
  page?: number;
  limit?: number;
  status?: TaskStatus | null;
  priority?: TaskPriority | null;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  search?: string;
  due_date_from?: string;
  due_date_to?: string;
  has_due_date?: boolean;
  tags?: string[];
}

/**
 * Update task request interface.
 */
export interface UpdateTaskRequest {
  title?: string;
  description?: string | null;
  priority?: TaskPriority;
  status?: TaskStatus;
  due_date?: string | null;
  notes?: string | null;
  manual_order?: number | null;
}
