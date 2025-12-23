/**
 * API client for task-related operations.
 * Provides typed functions for interacting with the backend Task API.
 */

import api from '../api';
import type {
  Task,
  CreateTaskRequest,
  StandardizedResponse,
  TaskListResponse,
  TaskQueryParams
} from '../types/task';

/**
 * Create a new task.
 *
 * @param data - Task creation data (title, description, priority)
 * @returns Promise resolving to the created task wrapped in StandardizedResponse
 * @throws Error if the request fails
 */
export async function createTask(
  data: CreateTaskRequest
): Promise<StandardizedResponse<Task>> {
  const response = await api.post<StandardizedResponse<Task>>('/api/v1/tasks/', data);
  return response.data;
}

/**
 * Get tasks with filtering, sorting, and pagination.
 *
 * @param params - Query parameters for filtering, sorting, and pagination
 * @returns Promise resolving to TaskListResponse with tasks, metadata, and pagination
 * @throws Error if the request fails
 */
export async function getTasks(
  params: TaskQueryParams = {}
): Promise<StandardizedResponse<TaskListResponse>> {
  const response = await api.get<StandardizedResponse<TaskListResponse>>('/api/v1/tasks/', {
    params: {
      page: params.page || 1,
      limit: params.limit || 20,
      status_filter: params.status || undefined,
      priority: params.priority || undefined,
      sort_by: params.sort_by || 'created_at',
      sort_order: params.sort_order || 'desc',
      search: params.search || undefined,
      due_date_from: params.due_date_from || undefined,
      due_date_to: params.due_date_to || undefined,
      has_due_date: params.has_due_date !== undefined ? params.has_due_date : undefined,
      tags: params.tags && params.tags.length > 0 ? params.tags.join(',') : undefined,
    },
  });
  return response.data;
}

/**
 * Update a task's title and/or description.
 *
 * @param taskId - UUID of the task to update
 * @param data - Update data (title and/or description)
 * @returns Promise resolving to the updated task
 * @throws Error if the request fails
 */
export async function updateTask(
  taskId: string,
  data: {
    title?: string;
    description?: string | null;
    priority?: 'low' | 'medium' | 'high';
    status?: 'pending' | 'completed';
    due_date?: string | null;
    notes?: string | null;
    manual_order?: number | null;
  }
): Promise<StandardizedResponse<Task>> {
  const response = await api.put<StandardizedResponse<Task>>(
    `/api/v1/tasks/${taskId}`,
    data
  );
  return response.data;
}

/**
 * Toggle a task's status between pending and completed.
 *
 * @param taskId - UUID of the task to toggle
 * @returns Promise resolving to the updated task
 * @throws Error if the request fails
 */
export async function toggleTask(taskId: string): Promise<StandardizedResponse<Task>> {
  const response = await api.patch<StandardizedResponse<Task>>(
    `/api/v1/tasks/${taskId}/toggle`
  );
  return response.data;
}

/**
 * Bulk toggle multiple tasks to a target status.
 *
 * @param taskIds - Array of task UUIDs to toggle
 * @param targetStatus - The status to set for all tasks
 * @returns Promise resolving to bulk operation response
 * @throws Error if the request fails
 */
export async function bulkToggleTasks(
  taskIds: string[],
  targetStatus: 'pending' | 'completed'
): Promise<StandardizedResponse<{ updated_count: number; tasks: Task[] }>> {
  const response = await api.post<StandardizedResponse<{ updated_count: number; tasks: Task[] }>>(
    '/api/v1/tasks/bulk-toggle',
    { task_ids: taskIds, target_status: targetStatus }
  );
  return response.data;
}

/**
 * Soft delete a task (move to trash).
 *
 * @param taskId - UUID of the task to delete
 * @returns Promise resolving to the soft-deleted task
 * @throws Error if the request fails
 */
export async function deleteTask(taskId: string): Promise<StandardizedResponse<Task>> {
  const response = await api.delete<StandardizedResponse<Task>>(`/api/v1/tasks/${taskId}`);
  return response.data;
}

/**
 * Bulk soft delete multiple tasks (move to trash).
 *
 * @param taskIds - Array of task UUIDs to delete
 * @returns Promise resolving to bulk operation response
 * @throws Error if the request fails
 */
export async function bulkDeleteTasks(
  taskIds: string[]
): Promise<StandardizedResponse<{ updated_count: number; tasks: Task[] }>> {
  const response = await api.post<StandardizedResponse<{ updated_count: number; tasks: Task[] }>>(
    '/api/v1/tasks/bulk-delete',
    { task_ids: taskIds }
  );
  return response.data;
}

/**
 * Get trash (soft-deleted tasks) with pagination.
 *
 * @param params - Query parameters for pagination
 * @returns Promise resolving to TaskListResponse with deleted tasks
 * @throws Error if the request fails
 */
export async function getTrash(
  params: TaskQueryParams = {}
): Promise<StandardizedResponse<TaskListResponse>> {
  const response = await api.get<StandardizedResponse<TaskListResponse>>('/api/v1/tasks/trash', {
    params: {
      page: params.page || 1,
      limit: params.limit || 20,
    },
  });
  return response.data;
}

/**
 * Restore a soft-deleted task from trash.
 *
 * @param taskId - UUID of the task to restore
 * @returns Promise resolving to the restored task
 * @throws Error if the request fails
 */
export async function restoreTask(taskId: string): Promise<StandardizedResponse<Task>> {
  const response = await api.post<StandardizedResponse<Task>>(`/api/v1/tasks/${taskId}/restore`);
  return response.data;
}

/**
 * Permanently delete a task from the database (irreversible).
 *
 * @param taskId - UUID of the task to permanently delete
 * @returns Promise resolving to success message
 * @throws Error if the request fails
 */
export async function permanentDeleteTask(
  taskId: string
): Promise<StandardizedResponse<{ task_id: string }>> {
  const response = await api.delete<StandardizedResponse<{ task_id: string }>>(
    `/api/v1/tasks/${taskId}/permanent`
  );
  return response.data;
}

/**
 * Reorder tasks by updating their manual_order field.
 *
 * @param taskIds - Ordered array of task UUIDs representing the new order
 * @returns Promise resolving to bulk operation response with updated tasks
 * @throws Error if the request fails
 */
export async function reorderTasks(
  taskIds: string[]
): Promise<StandardizedResponse<{ updated_count: number; tasks: Task[] }>> {
  const response = await api.patch<StandardizedResponse<{ updated_count: number; tasks: Task[] }>>(
    '/api/v1/tasks/reorder',
    { task_ids: taskIds }
  );
  return response.data;
}
