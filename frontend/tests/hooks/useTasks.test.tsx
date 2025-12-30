/**
 * Tests for useTasks hook
 *
 * Tests query and mutation operations for tasks including:
 * - Fetching tasks with filters
 * - Creating, updating, and deleting tasks
 * - Optimistic updates and rollback
 * - Bulk operations
 */

import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode } from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useTasks, useCreateTask, useUpdateTask, useDeleteTask, useToggleTask } from '@/hooks/useTasks';
import * as taskApi from '@/lib/api/tasks';
import { Task } from '@/lib/types/task';

// Mock the API module
vi.mock('@/lib/api/tasks');

// Mock toast
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));

describe('useTasks Hook', () => {
  let queryClient: QueryClient;
  let wrapper: ({ children }: { children: ReactNode }) => React.ReactElement;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );

    vi.clearAllMocks();
  });

  describe('useTasks - Query Hook', () => {
    it('should fetch tasks successfully', async () => {
      const mockTasks = {
        success: true,
        message: 'Tasks fetched successfully',
        data: {
          tasks: [
            { id: '1', title: 'Task 1', status: 'pending', priority: 'medium', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null },
            { id: '2', title: 'Task 2', status: 'completed', priority: 'high', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null },
          ] as Task[],
          metadata: { total_pending: 1, total_completed: 1, total_active: 2, total_deleted: 0 },
          pagination: { page: 1, limit: 20, total_items: 2, total_pages: 1, has_next: false, has_prev: false }
        }
      };

      vi.mocked(taskApi.getTasks).mockResolvedValue(mockTasks as any);

      const { result } = renderHook(() => useTasks({}), { wrapper });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockTasks.data);
      expect(taskApi.getTasks).toHaveBeenCalledWith({});
    });

    it('should handle fetch error', async () => {
      vi.mocked(taskApi.getTasks).mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useTasks({}), { wrapper });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBeTruthy();
    });

    it('should apply status filter', async () => {
      const mockTasks = {
        success: true,
        message: 'Tasks fetched successfully',
        data: {
          tasks: [{ id: '1', title: 'Task 1', status: 'pending', priority: 'medium', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null }] as Task[],
          metadata: { total_pending: 1, total_completed: 0, total_active: 1, total_deleted: 0 },
          pagination: { page: 1, limit: 20, total_items: 1, total_pages: 1, has_next: false, has_prev: false }
        }
      };

      vi.mocked(taskApi.getTasks).mockResolvedValue(mockTasks as any);

      const { result } = renderHook(() => useTasks({ status: 'pending' }), { wrapper });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(taskApi.getTasks).toHaveBeenCalledWith({ status: 'pending' });
    });

    it('should apply priority filter', async () => {
      const mockTasks = {
        success: true,
        message: 'Tasks fetched successfully',
        data: {
          tasks: [{ id: '1', title: 'Urgent Task', status: 'pending', priority: 'high', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null }] as Task[],
          metadata: { total_pending: 1, total_completed: 0, total_active: 1, total_deleted: 0 },
          pagination: { page: 1, limit: 20, total_items: 1, total_pages: 1, has_next: false, has_prev: false }
        }
      };

      vi.mocked(taskApi.getTasks).mockResolvedValue(mockTasks as any);

      const { result } = renderHook(() => useTasks({ priority: 'high' }), { wrapper });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(taskApi.getTasks).toHaveBeenCalledWith({ priority: 'high' });
    });

    it('should handle pagination', async () => {
      const mockTasks = {
        success: true,
        message: 'Tasks fetched successfully',
        data: {
          tasks: [] as Task[],
          metadata: { total_pending: 25, total_completed: 25, total_active: 50, total_deleted: 0 },
          pagination: { page: 2, limit: 20, total_items: 50, total_pages: 3, has_next: true, has_prev: true }
        }
      };

      vi.mocked(taskApi.getTasks).mockResolvedValue(mockTasks as any);

      const { result } = renderHook(() => useTasks({ page: 2, limit: 20 }), { wrapper });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(taskApi.getTasks).toHaveBeenCalledWith({ page: 2, limit: 20 });
    });

    it('should apply search query', async () => {
      const mockTasks = {
        success: true,
        message: 'Tasks fetched successfully',
        data: {
          tasks: [{ id: '1', title: 'Buy groceries', status: 'pending', priority: 'medium', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null }] as Task[],
          metadata: { total_pending: 1, total_completed: 0, total_active: 1, total_deleted: 0 },
          pagination: { page: 1, limit: 20, total_items: 1, total_pages: 1, has_next: false, has_prev: false }
        }
      };

      vi.mocked(taskApi.getTasks).mockResolvedValue(mockTasks as any);

      const { result } = renderHook(() => useTasks({ search: 'groceries' }), { wrapper });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(taskApi.getTasks).toHaveBeenCalledWith({ search: 'groceries' });
    });
  });

  describe('useCreateTask - Mutation Hook', () => {
    it('should create task successfully', async () => {
      const newTask = {
        success: true,
        message: 'Task created successfully',
        data: { id: '3', title: 'New Task', status: 'pending', priority: 'medium', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null }
      };
      vi.mocked(taskApi.createTask).mockResolvedValue(newTask as any);

      const { result } = renderHook(() => useCreateTask(), { wrapper });

      const taskData = { title: 'New Task', priority: 'medium' as const };
      result.current.mutate(taskData);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(taskApi.createTask).toHaveBeenCalledWith(taskData);
      expect(result.current.data).toEqual(newTask.data);
    });

    it('should handle create error', async () => {
      vi.mocked(taskApi.createTask).mockRejectedValue(new Error('Validation error'));

      const { result } = renderHook(() => useCreateTask(), { wrapper });

      const taskData = { title: '', priority: 'medium' as const };
      result.current.mutate(taskData);

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBeTruthy();
    });

    it('should invalidate queries on success', async () => {
      const newTask = {
        success: true,
        message: 'Task created successfully',
        data: { id: '3', title: 'New Task', status: 'pending', priority: 'medium', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null }
      };
      vi.mocked(taskApi.createTask).mockResolvedValue(newTask as any);

      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const { result } = renderHook(() => useCreateTask(), { wrapper });

      result.current.mutate({ title: 'New Task', priority: 'medium' as const });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['tasks'] });
    });
  });

  describe('useUpdateTask - Mutation Hook', () => {
    it('should update task successfully', async () => {
      const updatedTask = {
        success: true,
        message: 'Task updated successfully',
        data: { id: '1', title: 'Updated Task', status: 'pending', priority: 'high', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null }
      };
      vi.mocked(taskApi.updateTask).mockResolvedValue(updatedTask as any);

      const { result } = renderHook(() => useUpdateTask(), { wrapper });

      result.current.mutate({ taskId: '1', data: { title: 'Updated Task' } });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(taskApi.updateTask).toHaveBeenCalledWith('1', { title: 'Updated Task' });
    });

    it('should perform optimistic update', async () => {
      const updatedTask = {
        success: true,
        message: 'Task updated successfully',
        data: { id: '1', title: 'Updated Task', status: 'pending', priority: 'high', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null }
      };
      vi.mocked(taskApi.updateTask).mockResolvedValue(updatedTask as any);

      // Set initial query data
      queryClient.setQueryData(['tasks'], {
        tasks: [{ id: '1', title: 'Original Task', status: 'pending', priority: 'medium', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null }],
        metadata: { total_pending: 1, total_completed: 0, total_active: 1, total_deleted: 0 },
        pagination: { page: 1, limit: 20, total_items: 1, total_pages: 1, has_next: false, has_prev: false }
      });

      const { result } = renderHook(() => useUpdateTask(), { wrapper });

      result.current.mutate({ taskId: '1', data: { title: 'Updated Task' } });

      // Query data should be immediately updated
      const queryData = queryClient.getQueryData(['tasks']) as any;
      expect(queryData.tasks[0].title).toBe('Updated Task');

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });
    });

    it('should rollback on error', async () => {
      vi.mocked(taskApi.updateTask).mockRejectedValue(new Error('Update failed'));

      // Set initial query data
      const initialData = {
        tasks: [{ id: '1', title: 'Original Task', status: 'pending', priority: 'medium', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null }],
        metadata: { total_pending: 1, total_completed: 0, total_active: 1, total_deleted: 0 },
        pagination: { page: 1, limit: 20, total_items: 1, total_pages: 1, has_next: false, has_prev: false }
      };
      queryClient.setQueryData(['tasks'], initialData);

      const { result } = renderHook(() => useUpdateTask(), { wrapper });

      result.current.mutate({ taskId: '1', data: { title: 'Updated Task' } });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      // Query data should be rolled back
      const queryData = queryClient.getQueryData(['tasks']) as any;
      expect(queryData.tasks[0].title).toBe('Original Task');
    });
  });

  describe('useToggleTask - Mutation Hook', () => {
    it('should toggle task from pending to completed', async () => {
      const toggledTask = {
        success: true,
        message: 'Task toggled successfully',
        data: { id: '1', title: 'Task', status: 'completed', priority: 'medium', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null }
      };
      vi.mocked(taskApi.toggleTask).mockResolvedValue(toggledTask as any);

      const { result } = renderHook(() => useToggleTask(), { wrapper });

      result.current.mutate('1');

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(taskApi.toggleTask).toHaveBeenCalledWith('1');
    });

    it('should update task counts optimistically', async () => {
      const toggledTask = {
        success: true,
        message: 'Task toggled successfully',
        data: { id: '1', title: 'Task', status: 'completed', priority: 'medium', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null }
      };
      vi.mocked(taskApi.toggleTask).mockResolvedValue(toggledTask as any);

      // Set initial query data with counts
      queryClient.setQueryData(['tasks'], {
        tasks: [{ id: '1', title: 'Task', status: 'pending', priority: 'medium', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null }],
        metadata: {
          total_pending: 1,
          total_completed: 0,
          total_active: 1,
          total_deleted: 0
        },
        pagination: { page: 1, limit: 20, total_items: 1, total_pages: 1, has_next: false, has_prev: false }
      });

      const { result } = renderHook(() => useToggleTask(), { wrapper });

      result.current.mutate('1');

      // Counts should be immediately updated
      const queryData = queryClient.getQueryData(['tasks']) as any;
      expect(queryData.metadata.total_pending).toBe(0);
      expect(queryData.metadata.total_completed).toBe(1);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });
    });
  });

  describe('useDeleteTask - Mutation Hook', () => {
    it('should delete task successfully', async () => {
      const deletedTaskResult = {
        success: true,
        message: 'Task deleted successfully',
        data: { id: '1', title: 'Task 1', status: 'pending', priority: 'medium', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null }
      };
      vi.mocked(taskApi.deleteTask).mockResolvedValue(deletedTaskResult as any);

      const { result } = renderHook(() => useDeleteTask(), { wrapper });

      result.current.mutate('1');

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(taskApi.deleteTask).toHaveBeenCalledWith('1');
    });

    it('should remove task optimistically', async () => {
      const deletedTaskResult = {
        success: true,
        message: 'Task deleted successfully',
        data: { id: '1', title: 'Task 1', status: 'pending', priority: 'medium', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null }
      };
      vi.mocked(taskApi.deleteTask).mockResolvedValue(deletedTaskResult as any);

      // Set initial query data
      queryClient.setQueryData(['tasks'], {
        tasks: [
          { id: '1', title: 'Task 1', status: 'pending', priority: 'medium', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null },
          { id: '2', title: 'Task 2', status: 'pending', priority: 'low', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null },
        ],
        metadata: { total_pending: 2, total_completed: 0, total_active: 2, total_deleted: 0 },
        pagination: { page: 1, limit: 20, total_items: 2, total_pages: 1, has_next: false, has_prev: false }
      });

      const { result } = renderHook(() => useDeleteTask(), { wrapper });

      result.current.mutate('1');

      // Task should be immediately removed
      const queryData = queryClient.getQueryData(['tasks']) as any;
      expect(queryData.tasks.length).toBe(1);
      expect(queryData.tasks[0].id).toBe('2');

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });
    });

    it('should rollback deletion on error', async () => {
      vi.mocked(taskApi.deleteTask).mockRejectedValue(new Error('Delete failed'));

      // Set initial query data
      const initialData = {
        tasks: [{ id: '1', title: 'Task 1', status: 'pending', priority: 'medium', user_id: 'user1', created_at: '', updated_at: '', completed_at: null, deleted_at: null, description: null, notes: null, manual_order: null }],
        metadata: { total_pending: 1, total_completed: 0, total_active: 1, total_deleted: 0 },
        pagination: { page: 1, limit: 20, total_items: 1, total_pages: 1, has_next: false, has_prev: false }
      };
      queryClient.setQueryData(['tasks'], initialData);

      const { result } = renderHook(() => useDeleteTask(), { wrapper });

      result.current.mutate('1');

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      // Task should be restored
      const queryData = queryClient.getQueryData(['tasks']) as any;
      expect(queryData.tasks.length).toBe(1);
      expect(queryData.tasks[0].id).toBe('1');
    });
  });
});
