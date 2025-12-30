"use server";

/**
 * Server Actions for task mutations with automatic cache revalidation.
 * These actions are called from Client Components and trigger Next.js cache invalidation.
 */

import { revalidatePath, revalidateTag } from 'next/cache';
import type { CreateTaskRequest, TaskStatus } from '@/lib/types/task';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9000';

// Type-safe wrappers for Next.js revalidation functions
const _revalidatePath = revalidatePath as (path: string, type?: 'page' | 'layout') => void;
const _revalidateTag = revalidateTag as (tag: string, maxAge?: number) => void;

/**
 * Get authentication token from cookies
 * In production, you should use next-auth or similar
 */
async function getAuthToken(): Promise<string | null> {
  const { cookies } = await import('next/headers');
  const cookieStore = await cookies();
  // Adjust this based on your auth implementation
  const token = cookieStore.get('better-auth.session_token')?.value;
  return token || null;
}

/**
 * Revalidate all task-related pages
 */
function revalidateAllTaskPages() {
  _revalidatePath('/tasks');
  _revalidatePath('/tasks/dashboard');
  _revalidatePath('/tasks/kanban');
  _revalidatePath('/tasks/calendar');
  _revalidateTag('tasks');
  _revalidateTag('analytics');
}

/**
 * Create a new task and revalidate the tasks cache
 */
export async function createTaskAction(data: CreateTaskRequest) {
  const token = await getAuthToken();

  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/tasks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to create task' }));
    throw new Error(error.detail || 'Failed to create task');
  }

  const result = await response.json();

  // Revalidate all task-related pages
  revalidateAllTaskPages();

  return result;
}

/**
 * Update an existing task and revalidate the cache
 */
export async function updateTaskAction(
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
) {
  const token = await getAuthToken();

  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/tasks/${taskId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to update task' }));
    throw new Error(error.detail || 'Failed to update task');
  }

  const result = await response.json();

  // Revalidate all task-related pages
  revalidateAllTaskPages();

  return result;
}

/**
 * Toggle task status (pending <-> completed)
 */
export async function toggleTaskAction(taskId: string) {
  const token = await getAuthToken();

  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/tasks/${taskId}/toggle`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to toggle task' }));
    throw new Error(error.detail || 'Failed to toggle task');
  }

  const result = await response.json();

  // Revalidate all task-related pages
  revalidateAllTaskPages();

  return result;
}

/**
 * Bulk toggle multiple tasks
 */
export async function bulkToggleTasksAction(taskIds: string[], targetStatus: TaskStatus) {
  const token = await getAuthToken();

  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/tasks/bulk/toggle`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      task_ids: taskIds,
      target_status: targetStatus,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to bulk toggle tasks' }));
    throw new Error(error.detail || 'Failed to bulk toggle tasks');
  }

  const result = await response.json();

  // Revalidate all task-related pages
  revalidateAllTaskPages();

  return result;
}

/**
 * Delete a task (soft delete)
 */
export async function deleteTaskAction(taskId: string) {
  const token = await getAuthToken();

  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/tasks/${taskId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to delete task' }));
    throw new Error(error.detail || 'Failed to delete task');
  }

  const result = await response.json();

  // Revalidate all task-related pages
  revalidateAllTaskPages();

  return result;
}

/**
 * Bulk delete multiple tasks
 */
export async function bulkDeleteTasksAction(taskIds: string[]) {
  const token = await getAuthToken();

  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/tasks/bulk/delete`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ task_ids: taskIds }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to bulk delete tasks' }));
    throw new Error(error.detail || 'Failed to bulk delete tasks');
  }

  const result = await response.json();

  // Revalidate all task-related pages
  revalidateAllTaskPages();

  return result;
}

/**
 * Reorder tasks
 */
export async function reorderTasksAction(taskIds: string[]) {
  const token = await getAuthToken();

  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/tasks/reorder`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ task_ids: taskIds }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to reorder tasks' }));
    throw new Error(error.detail || 'Failed to reorder tasks');
  }

  const result = await response.json();

  // Revalidate tasks page
  _revalidatePath('/tasks');
  _revalidateTag('tasks');

  return result;
}

/**
 * Restore a task from trash
 */
export async function restoreTaskAction(taskId: string) {
  const token = await getAuthToken();

  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/tasks/${taskId}/restore`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to restore task' }));
    throw new Error(error.detail || 'Failed to restore task');
  }

  const result = await response.json();

  // Revalidate all task-related pages
  revalidateAllTaskPages();

  return result;
}

/**
 * Permanently delete a task
 */
export async function permanentDeleteTaskAction(taskId: string) {
  const token = await getAuthToken();

  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/tasks/${taskId}/permanent`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to permanently delete task' }));
    throw new Error(error.detail || 'Failed to permanently delete task');
  }

  const result = await response.json();

  // Revalidate trash page
  _revalidatePath('/tasks/trash');
  _revalidateTag('tasks');

  return result;
}

/**
 * Generic revalidation action for chatbot mutations
 * Call this after the chatbot makes changes to tasks
 */
export async function revalidateTasksAction() {
  revalidateAllTaskPages();
}
