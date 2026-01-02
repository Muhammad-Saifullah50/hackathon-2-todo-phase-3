/**
 * React Query hooks for task operations.
 * Uses direct API calls instead of server actions for better auth handling.
 */

import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { getTasks, getTrash } from '@/lib/api/tasks';
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
    staleTime: 0,
    gcTime: 5 * 60 * 1000,
    refetchOnWindowFocus: true,
    refetchOnMount: 'always',
  });
}

/**
 * Hook to create a new task with optimistic updates.
 */
export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateTaskRequest) => {
      const response = await api.post('/api/v1/tasks', data);
      return response.data.data;
    },

    onMutate: async (newTask: CreateTaskRequest) => {
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      const previousTasks = queryClient.getQueryData(tasksKeys.all);

      const tempId = `temp-${crypto.randomUUID()}`;

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

      return { previousTasks };
    },

    onError: (error, _variables, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(tasksKeys.all, context.previousTasks);
      }
      console.error('Failed to create task:', error);
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: tasksKeys.all });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },
  });
}

/**
 * Hook to update a task with optimistic updates.
 */
export function useUpdateTask() {
  const queryClient = useQueryClient();
  const { toast, dismiss } = useToast();

  return useMutation({
    mutationFn: async ({
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
    }) => {
      const response = await api.put(`/api/v1/tasks/${taskId}`, data);
      return response.data.data;
    },

    onMutate: async ({ taskId, data }) => {
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      const previousQueries = queryClient.getQueriesData({
        queryKey: tasksKeys.all,
      });

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
        title: "Failed to update task",
        description:
          error instanceof Error
            ? error.message
            : "An error occurred while updating the task.",
        duration: 5000,
      });

      console.error("Failed to update task:", error);
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: tasksKeys.all });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },

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
    mutationFn: async (taskId: string) => {
      const response = await api.patch(`/api/v1/tasks/${taskId}/toggle`);
      return response.data.data;
    },

    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      const previousQueries = queryClient.getQueriesData({ queryKey: tasksKeys.all });

      const now = new Date().toISOString();

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
    mutationFn: async ({ taskIds, targetStatus }: { taskIds: string[]; targetStatus: TaskStatus }) => {
      const response = await api.patch('/api/v1/tasks/bulk-toggle', {
        task_ids: taskIds,
        target_status: targetStatus,
      });
      return response.data.data;
    },

    onMutate: async ({ taskIds, targetStatus }) => {
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      const previousQueries = queryClient.getQueriesData({ queryKey: tasksKeys.all });

      const now = new Date().toISOString();
      const completedAt = targetStatus === 'completed' ? now : null;

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

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: tasksKeys.all });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },

    onSuccess: (data) => {
      const count = data?.updated_count || 0;
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
    mutationFn: async (taskId: string) => {
      const response = await api.delete(`/api/v1/tasks/${taskId}`);
      return response.data.data;
    },

    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      const previousQueries = queryClient.getQueriesData({ queryKey: tasksKeys.all });

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
    mutationFn: async (taskIds: string[]) => {
      // Validate task IDs before sending
      const validTaskIds = taskIds.filter(id => {
        // Check if string looks like a UUID or temp ID (standard UUID format: 8-4-4-4-12)
        return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id);
      });

      if (validTaskIds.length !== taskIds.length) {
        console.error('Invalid task IDs detected:', taskIds);
        throw new Error('Some task IDs are invalid');
      }

      const response = await api.post('/api/v1/tasks/bulk-delete', {
        task_ids: validTaskIds,
      });
      return response.data.data;
    },

    onMutate: async (taskIds) => {
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      const previousQueries = queryClient.getQueriesData({ queryKey: tasksKeys.all });

      const taskIdSet = new Set(taskIds);

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

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: tasksKeys.all });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },

    onSuccess: (data) => {
      const count = data?.updated_count || 0;
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
    mutationFn: async (taskId: string) => {
      const response = await api.post(`/api/v1/tasks/${taskId}/restore`);
      return response.data.data;
    },

    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      const previousQueries = queryClient.getQueriesData({ queryKey: tasksKeys.all });

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
    mutationFn: async (taskId: string) => {
      const response = await api.delete(`/api/v1/tasks/${taskId}/permanent`);
      return response.data.data;
    },

    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      const previousQueries = queryClient.getQueriesData({ queryKey: tasksKeys.all });

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
 */
export function useReorderTasks() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: async (taskIds: string[]) => {
      const response = await api.patch('/api/v1/tasks/reorder', {
        task_ids: taskIds,
      });
      return response.data.data;
    },

    onMutate: async (taskIds) => {
      await queryClient.cancelQueries({ queryKey: tasksKeys.all });

      const previousQueries = queryClient.getQueriesData({ queryKey: tasksKeys.all });

      const taskMap = new Map<string, Task>(
        (queryClient.getQueryData(tasksKeys.all) as any)?.data?.tasks?.map((task: Task) => [task.id, task]) || []
      );
      const reorderedTasks: Task[] = [];
      for (let i = 0; i < taskIds.length; i++) {
        const task = taskMap.get(taskIds[i]);
        if (task) {
          reorderedTasks.push({ ...task, manual_order: i });
        }
      }

      const reorderSet = new Set(taskIds);
      const remainingTasks = (queryClient.getQueryData(tasksKeys.all) as any)?.data?.tasks?.filter(
        (task: Task) => !reorderSet.has(task.id)
      ) || [];

      queryClient.setQueriesData({ queryKey: tasksKeys.all }, (old: any) => {
        if (!old || !old.data || !old.data.tasks) return old;

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

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: tasksKeys.all });
    },
  });
}
