/**
 * React Query hooks for task operations.
 * Provides optimistic updates for better UX.
 */

import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import {
  getTasks,
  getTrash,
} from '@/lib/api/tasks';
import {
  createTaskAction,
  updateTaskAction,
  toggleTaskAction,
  bulkToggleTasksAction,
  deleteTaskAction,
  bulkDeleteTasksAction,
  reorderTasksAction,
  restoreTaskAction,
  permanentDeleteTaskAction,
} from '@/app/actions/tasks';
import type { CreateTaskRequest, Task, TaskQueryParams, TaskStatus } from '@/lib/types/task';
import { useToast } from './use-toast';

/**
 * Query key factory for tasks.
 * Includes query parameters to enable proper caching per filter/sort/page combination.
 */
export const tasksKeys = {
  all: ['tasks'] as const,
  lists: () => [...tasksKeys.all, 'list'] as const,
  list: (params: TaskQueryParams) => [...tasksKeys.lists(), params] as const,
};

/**
 * Hook to fetch tasks with filtering, sorting, and pagination.
 *
 * @param params - Query parameters for filtering, sorting, and pagination
 * @returns React Query result with tasks data, metadata, and pagination
 */
export function useTasks(params: TaskQueryParams = {}) {
  return useQuery({
    queryKey: tasksKeys.list(params),
    queryFn: () => getTasks(params),
    staleTime: 0, // Always consider data stale so invalidateQueries triggers refetch
    gcTime: 5 * 60 * 1000, // Keep unused data in cache for 5 minutes
    refetchOnWindowFocus: true, // Refetch when user returns to window
    refetchOnMount: 'always', // ALWAYS refetch on component mount - never use stale data
  });
}

/**
 * Hook to create a new task with optimistic updates.
 * Provides instant UI feedback even before server responds.
 */
export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createTaskAction,

    // Optimistic update: show task immediately
    onMutate: async (newTask: CreateTaskRequest) => {
      // Cancel any outgoing refetches for all task lists
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      // Snapshot the previous value
      const previousTasks = queryClient.getQueryData(tasksKeys.all);

      // Generate temporary ID for optimistic task
      const tempId = `temp-${crypto.randomUUID()}`;

      // Optimistically update the cache for all task lists
      queryClient.setQueryData(tasksKeys.all, (old: any) => {
        if (!old || !old.data) return old;

        const optimisticTask: Task = {
          id: tempId,
          title: newTask.title,
          description: newTask.description || null,
          priority: newTask.priority || 'medium',
          status: 'pending',
          user_id: 'temp-user',
          due_date: newTask.due_date || null,
          notes: newTask.notes || null,
          manual_order: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          completed_at: null,
          deleted_at: null,
        };

        return {
          ...old,
          data: {
            ...old.data,
            tasks: [optimisticTask, ...(old.data.tasks || [])],
          },
        };
      });

      // Return context for rollback
      return { previousTasks };
    },

    // Rollback on error
    onError: (error, _variables, context) => {
      // Restore previous state
      if (context?.previousTasks) {
        queryClient.setQueryData(tasksKeys.all, context.previousTasks);
      }

      // Log error for debugging
      console.error('Failed to create task:', error);
    },

    // After server action completes, Next.js revalidation handles cache refresh
    // We just invalidate React Query cache as a fallback
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: tasksKeys.all });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },
  });
}

/**
 * Hook to update a task with optimistic updates and rollback on error.
 */
export function useUpdateTask() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({
      taskId,
      data,
    }: {
      taskId: string;
      data: {
        title?: string;
        description?: string | null;
        priority?: 'low' | 'medium' | 'high';
        status?: 'pending' | 'completed';
        due_date?: string | null;
        notes?: string | null;
        manual_order?: number | null;
      };
    }) => updateTaskAction(taskId, data),

    // Optimistic update: show changes immediately
    onMutate: async ({ taskId, data }) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      // Snapshot the previous value for all task queries
      const previousQueries = queryClient.getQueriesData({
        queryKey: tasksKeys.all,
      });

      // Optimistically update all task list caches
      queryClient.setQueriesData({ queryKey: tasksKeys.all }, (old: any) => {
        if (!old || !old.data || !old.data.tasks) return old;

        return {
          ...old,
          data: {
            ...old.data,
            tasks: old.data.tasks.map((task: Task) =>
              task.id === taskId
                ? {
                    ...task,
                    title: data.title !== undefined ? data.title : task.title,
                    description:
                      data.description !== undefined
                        ? data.description
                        : task.description,
                    priority: data.priority !== undefined ? data.priority : task.priority,
                    status: data.status !== undefined ? data.status : task.status,
                    due_date: data.due_date !== undefined ? data.due_date : task.due_date,
                    notes: data.notes !== undefined ? data.notes : task.notes,
                    manual_order:
                      data.manual_order !== undefined ? data.manual_order : task.manual_order,
                    updated_at: new Date().toISOString(),
                  }
                : task
            ),
          },
        };
      });

      // Return context for rollback
      return { previousQueries };
    },

    // Rollback on error
    onError: (error, _variables, context) => {
      // Restore all previous states
      if (context?.previousQueries) {
        context.previousQueries.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }

      // Show error toast
      toast({
        variant: "destructive",
        title: "Failed to update task",
        description:
          error instanceof Error
            ? error.message
            : "An error occurred while updating the task.",
      });

      // Log error for debugging
      console.error("Failed to update task:", error);
    },

    // After server action completes, Next.js revalidation handles cache refresh
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: tasksKeys.all });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },

    // Show success toast on success
    onSuccess: () => {
      toast({
        title: "Task updated",
        description: "Your task has been updated successfully.",
      });
    },
  });
}

/**
 * Hook to toggle a task's status with optimistic updates.
 */
export function useToggleTask() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (taskId: string) => toggleTaskAction(taskId),

    // Optimistic update: flip status immediately
    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      const previousQueries = queryClient.getQueriesData({ queryKey: tasksKeys.all });

      // Optimistically toggle status in all caches
      queryClient.setQueriesData({ queryKey: tasksKeys.all }, (old: any) => {
        if (!old || !old.data || !old.data.tasks) return old;

        const now = new Date().toISOString();

        return {
          ...old,
          data: {
            ...old.data,
            tasks: old.data.tasks.map((task: Task) =>
              task.id === taskId
                ? {
                    ...task,
                    status: task.status === 'pending' ? 'completed' : 'pending',
                    completed_at: task.status === 'pending' ? now : null,
                    updated_at: now,
                  }
                : task
            ),
            // Update metadata counts
            metadata: old.data.metadata
              ? {
                  ...old.data.metadata,
                  total_pending:
                    old.data.tasks.find((t: Task) => t.id === taskId)?.status === 'pending'
                      ? old.data.metadata.total_pending - 1
                      : old.data.metadata.total_pending + 1,
                  total_completed:
                    old.data.tasks.find((t: Task) => t.id === taskId)?.status === 'pending'
                      ? old.data.metadata.total_completed + 1
                      : old.data.metadata.total_completed - 1,
                }
              : old.data.metadata,
          },
        };
      });

      return { previousQueries };
    },

    onError: (error, _variables, context) => {
      if (context?.previousQueries) {
        context.previousQueries.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }

      toast({
        variant: "destructive",
        title: "Failed to toggle task",
        description: error instanceof Error ? error.message : "An error occurred.",
      });
    },

    // After server action completes, Next.js revalidation handles cache refresh
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: tasksKeys.all });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },
  });
}

/**
 * Hook to bulk toggle multiple tasks with optimistic updates.
 */
export function useBulkToggle() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ taskIds, targetStatus }: { taskIds: string[]; targetStatus: TaskStatus }) =>
      bulkToggleTasksAction(taskIds, targetStatus),

    onMutate: async ({ taskIds, targetStatus }) => {
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      const previousQueries = queryClient.getQueriesData({ queryKey: tasksKeys.all });

      const now = new Date().toISOString();
      const completedAt = targetStatus === 'completed' ? now : null;

      // Optimistically update all selected tasks
      queryClient.setQueriesData({ queryKey: tasksKeys.all }, (old: any) => {
        if (!old || !old.data || !old.data.tasks) return old;

        const taskIdSet = new Set(taskIds);

        return {
          ...old,
          data: {
            ...old.data,
            tasks: old.data.tasks.map((task: Task) =>
              taskIdSet.has(task.id)
                ? {
                    ...task,
                    status: targetStatus,
                    completed_at: completedAt,
                    updated_at: now,
                  }
                : task
            ),
          },
        };
      });

      return { previousQueries };
    },

    onError: (error, _variables, context) => {
      if (context?.previousQueries) {
        context.previousQueries.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }

      toast({
        variant: "destructive",
        title: "Failed to toggle tasks",
        description: error instanceof Error ? error.message : "An error occurred.",
      });
    },

    // After server action completes, Next.js revalidation handles cache refresh
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: tasksKeys.all });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },

    onSuccess: (data) => {
      const count = data.data?.updated_count || 0;
      toast({
        title: "Tasks updated",
        description: `Successfully updated ${count} task${count === 1 ? '' : 's'}.`,
      });
    },
  });
}

/**
 * Hook to soft delete a task with optimistic updates.
 */
export function useDeleteTask() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (taskId: string) => deleteTaskAction(taskId),

    // Optimistic update: remove task immediately
    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      const previousQueries = queryClient.getQueriesData({ queryKey: tasksKeys.all });

      // Optimistically remove task from all caches
      queryClient.setQueriesData({ queryKey: tasksKeys.all }, (old: any) => {
        if (!old || !old.data || !old.data.tasks) return old;

        return {
          ...old,
          data: {
            ...old.data,
            tasks: old.data.tasks.filter((task: Task) => task.id !== taskId),
            // Update metadata counts
            metadata: old.data.metadata
              ? {
                  ...old.data.metadata,
                  total_active: old.data.metadata.total_active - 1,
                  total_deleted: old.data.metadata.total_deleted + 1,
                }
              : old.data.metadata,
          },
        };
      });

      return { previousQueries };
    },

    onError: (error, _variables, context) => {
      if (context?.previousQueries) {
        context.previousQueries.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }

      toast({
        variant: "destructive",
        title: "Failed to delete task",
        description: error instanceof Error ? error.message : "An error occurred.",
      });
    },

    // After server action completes, Next.js revalidation handles cache refresh
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: tasksKeys.all });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },

    onSuccess: () => {
      toast({
        title: "Task moved to trash",
        description: "You can restore it from the trash view.",
      });
    },
  });
}

/**
 * Hook to bulk delete multiple tasks with optimistic updates.
 */
export function useBulkDelete() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (taskIds: string[]) => bulkDeleteTasksAction(taskIds),

    onMutate: async (taskIds) => {
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      const previousQueries = queryClient.getQueriesData({ queryKey: tasksKeys.all });

      const taskIdSet = new Set(taskIds);

      // Optimistically remove all selected tasks
      queryClient.setQueriesData({ queryKey: tasksKeys.all }, (old: any) => {
        if (!old || !old.data || !old.data.tasks) return old;

        return {
          ...old,
          data: {
            ...old.data,
            tasks: old.data.tasks.filter((task: Task) => !taskIdSet.has(task.id)),
          },
        };
      });

      return { previousQueries };
    },

    onError: (error, _variables, context) => {
      if (context?.previousQueries) {
        context.previousQueries.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }

      toast({
        variant: "destructive",
        title: "Failed to delete tasks",
        description: error instanceof Error ? error.message : "An error occurred.",
      });
    },

    // After server action completes, Next.js revalidation handles cache refresh
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: tasksKeys.all });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },

    onSuccess: (data) => {
      const count = data.data?.updated_count || 0;
      toast({
        title: "Tasks moved to trash",
        description: `Successfully moved ${count} task${count === 1 ? '' : 's'} to trash.`,
      });
    },
  });
}

/**
 * Hook to fetch trash (soft-deleted tasks) with pagination.
 */
export function useTrash(params: TaskQueryParams = {}) {
  return useQuery({
    queryKey: [...tasksKeys.all, 'trash', params],
    queryFn: () => getTrash(params),
    staleTime: 30000,
    gcTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to restore a task from trash with optimistic updates.
 */
export function useRestoreTask() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (taskId: string) => restoreTaskAction(taskId),

    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      const previousQueries = queryClient.getQueriesData({ queryKey: tasksKeys.all });

      // Optimistically remove from trash view
      queryClient.setQueriesData({ queryKey: [...tasksKeys.all, 'trash'] }, (old: any) => {
        if (!old || !old.data || !old.data.tasks) return old;

        return {
          ...old,
          data: {
            ...old.data,
            tasks: old.data.tasks.filter((task: Task) => task.id !== taskId),
          },
        };
      });

      return { previousQueries };
    },

    onError: (error, _variables, context) => {
      if (context?.previousQueries) {
        context.previousQueries.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }

      toast({
        variant: "destructive",
        title: "Failed to restore task",
        description: error instanceof Error ? error.message : "An error occurred.",
      });
    },

    // After server action completes, Next.js revalidation handles cache refresh
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: tasksKeys.all });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },

    onSuccess: () => {
      toast({
        title: "Task restored",
        description: "The task has been restored successfully.",
      });
    },
  });
}

/**
 * Hook to permanently delete a task from the database.
 */
export function usePermanentDelete() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (taskId: string) => permanentDeleteTaskAction(taskId),

    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      const previousQueries = queryClient.getQueriesData({ queryKey: tasksKeys.all });

      // Optimistically remove from trash view
      queryClient.setQueriesData({ queryKey: [...tasksKeys.all, 'trash'] }, (old: any) => {
        if (!old || !old.data || !old.data.tasks) return old;

        return {
          ...old,
          data: {
            ...old.data,
            tasks: old.data.tasks.filter((task: Task) => task.id !== taskId),
          },
        };
      });

      return { previousQueries };
    },

    onError: (error, _variables, context) => {
      if (context?.previousQueries) {
        context.previousQueries.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }

      toast({
        variant: "destructive",
        title: "Failed to permanently delete task",
        description: error instanceof Error ? error.message : "An error occurred.",
      });
    },

    // After server action completes, Next.js revalidation handles cache refresh
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: tasksKeys.all });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },

    onSuccess: () => {
      toast({
        title: "Task permanently deleted",
        description: "This action cannot be undone.",
      });
    },
  });
}

/**
 * Hook to reorder tasks with optimistic updates.
 * Updates the manual_order field for the provided task IDs.
 */
export function useReorderTasks() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (taskIds: string[]) => reorderTasksAction(taskIds),

    // Optimistic update: reorder tasks immediately
    onMutate: async (taskIds) => {
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      const previousQueries = queryClient.getQueriesData({ queryKey: tasksKeys.all });

      // Optimistically reorder tasks in all caches
      queryClient.setQueriesData({ queryKey: tasksKeys.all }, (old: any) => {
        if (!old || !old.data || !old.data.tasks) return old;

        const taskMap = new Map<string, Task>(
          old.data.tasks.map((task: Task) => [task.id, task])
        );
        const reorderedTasks: Task[] = [];
        for (let i = 0; i < taskIds.length; i++) {
          const task = taskMap.get(taskIds[i]);
          if (task) {
            reorderedTasks.push({ ...task, manual_order: i });
          }
        }

        // Add any tasks that weren't in the reorder list at the end
        const reorderSet = new Set(taskIds);
        const remainingTasks = old.data.tasks.filter(
          (task: Task) => !reorderSet.has(task.id)
        );

        return {
          ...old,
          data: {
            ...old.data,
            tasks: [...reorderedTasks, ...remainingTasks],
          },
        };
      });

      return { previousQueries };
    },

    onError: (error, _variables, context) => {
      if (context?.previousQueries) {
        context.previousQueries.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }

      toast({
        variant: "destructive",
        title: "Failed to reorder tasks",
        description: error instanceof Error ? error.message : "An error occurred.",
      });
    },

    // After server action completes, Next.js revalidation handles cache refresh
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: tasksKeys.all });
    },
  });
}
