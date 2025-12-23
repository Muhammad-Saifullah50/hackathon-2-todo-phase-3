import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryOptions,
  UseMutationOptions,
} from "@tanstack/react-query";
import { Subtask, SubtaskListResponse } from "@/lib/types/task";

// API client for subtasks
const apiClient = {
  getSubtasks: async (taskId: string): Promise<SubtaskListResponse> => {
    const response = await fetch(`/api/v1/tasks/${taskId}/subtasks`);
    if (!response.ok) {
      throw new Error("Failed to fetch subtasks");
    }
    const result = await response.json();
    return result.data;
  },

  createSubtask: async (taskId: string, description: string): Promise<Subtask> => {
    const response = await fetch(`/api/v1/tasks/${taskId}/subtasks`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        description,
        order_index: null, // Let backend auto-assign
      }),
    });
    if (!response.ok) {
      throw new Error("Failed to create subtask");
    }
    const result = await response.json();
    return result.data;
  },

  updateSubtask: async (
    subtaskId: string,
    data: Partial<Subtask>
  ): Promise<Subtask> => {
    const response = await fetch(`/api/v1/subtasks/${subtaskId}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error("Failed to update subtask");
    }
    const result = await response.json();
    return result.data;
  },

  toggleSubtask: async (subtaskId: string, isCompleted: boolean): Promise<Subtask> => {
    const response = await fetch(`/api/v1/subtasks/${subtaskId}/toggle`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ is_completed: isCompleted }),
    });
    if (!response.ok) {
      throw new Error("Failed to toggle subtask");
    }
    const result = await response.json();
    return result.data;
  },

  deleteSubtask: async (subtaskId: string): Promise<void> => {
    const response = await fetch(`/api/v1/subtasks/${subtaskId}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      throw new Error("Failed to delete subtask");
    }
  },

  reorderSubtasks: async (taskId: string, subtaskIds: string[]): Promise<SubtaskListResponse> => {
    const response = await fetch(`/api/v1/tasks/${taskId}/subtasks/reorder`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ subtask_ids: subtaskIds }),
    });
    if (!response.ok) {
      throw new Error("Failed to reorder subtasks");
    }
    const result = await response.json();
    return result.data;
  },
};

// Define hook types
type UseSubtasksQueryOptions = UseQueryOptions<
  SubtaskListResponse,
  Error,
  SubtaskListResponse,
  [string, string]
>;

type UseCreateSubtaskMutationOptions = UseMutationOptions<
  Subtask,
  Error,
  { taskId: string; description: string }
>;

type UseUpdateSubtaskMutationOptions = UseMutationOptions<
  Subtask,
  Error,
  { subtaskId: string; data: Partial<Subtask> }
>;

type UseToggleSubtaskMutationOptions = UseMutationOptions<
  Subtask,
  Error,
  { subtaskId: string; isCompleted: boolean }
>;

type UseDeleteSubtaskMutationOptions = UseMutationOptions<
  void,
  Error,
  string
>;

type UseReorderSubtasksMutationOptions = UseMutationOptions<
  SubtaskListResponse,
  Error,
  { taskId: string; subtaskIds: string[] }
>;

/**
 * Hook to fetch subtasks for a specific task
 */
export const useSubtasks = (taskId: string, options?: UseSubtasksQueryOptions) => {
  return useQuery({
    queryKey: ["subtasks", taskId],
    queryFn: () => apiClient.getSubtasks(taskId),
    enabled: !!taskId,
    ...options,
  });
};

/**
 * Hook to create a new subtask
 */
export const useCreateSubtask = (options?: UseCreateSubtaskMutationOptions) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ taskId, description }) => 
      apiClient.createSubtask(taskId, description),
    onSuccess: (newSubtask, variables) => {
      // Update the subtasks query cache
      queryClient.setQueryData<SubtaskListResponse>(
        ["subtasks", variables.taskId],
        (old: SubtaskListResponse | undefined) => {
          if (!old) return {
            subtasks: [newSubtask],
            total_count: 1,
            completed_count: 0,
            pending_count: 1,
            completion_percentage: 0
          };
          
          const updatedSubtasks = [...old.subtasks, newSubtask].sort(
            (a, b) => a.order_index - b.order_index
          );
          
          return {
            ...old,
            subtasks: updatedSubtasks,
            total_count: old.total_count + 1,
            completion_percentage: 
              (old.completed_count / (old.total_count + 1)) * 100,
          };
        }
      );
      
      // Invalidate and refetch to ensure data consistency
      queryClient.invalidateQueries({ queryKey: ["subtasks", variables.taskId] });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
    ...options,
  });
};

/**
 * Hook to update a subtask
 */
export const useUpdateSubtask = (options?: UseUpdateSubtaskMutationOptions) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ subtaskId, data }) => 
      apiClient.updateSubtask(subtaskId, data),
    onSuccess: (updatedSubtask, variables) => {
      // Update the subtasks query cache
      queryClient.setQueryData<SubtaskListResponse>(
        ["subtasks", updatedSubtask.task_id],
        (old) => {
          if (!old) return old;
          
          const updatedSubtasks = old.subtasks.map((subtask) =>
            subtask.id === updatedSubtask.id ? updatedSubtask : subtask
          );
          
          // Recalculate stats
          const completedCount = updatedSubtasks.filter(s => s.is_completed).length;
          const completionPercentage = updatedSubtasks.length 
            ? (completedCount / updatedSubtasks.length) * 100 
            : 0;
          
          return {
            ...old,
            subtasks: updatedSubtasks,
            completed_count: completedCount,
            completion_percentage: completionPercentage,
          };
        }
      );
      
      // Invalidate and refetch to ensure data consistency
      queryClient.invalidateQueries({ 
        queryKey: ["subtasks", updatedSubtask.task_id] 
      });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
    ...options,
  });
};

/**
 * Hook to toggle a subtask's completion status
 */
export const useToggleSubtask = (options?: UseToggleSubtaskMutationOptions) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ subtaskId, isCompleted }) => 
      apiClient.toggleSubtask(subtaskId, isCompleted),
    onSuccess: (updatedSubtask, variables) => {
      // Update the subtasks query cache
      queryClient.setQueryData<SubtaskListResponse>(
        ["subtasks", updatedSubtask.task_id],
        (old) => {
          if (!old) return old;
          
          const updatedSubtasks = old.subtasks.map((subtask) =>
            subtask.id === updatedSubtask.id ? updatedSubtask : subtask
          );
          
          // Recalculate stats
          const completedCount = updatedSubtasks.filter(s => s.is_completed).length;
          const completionPercentage = updatedSubtasks.length 
            ? (completedCount / updatedSubtasks.length) * 100 
            : 0;
          
          return {
            ...old,
            subtasks: updatedSubtasks,
            completed_count: completedCount,
            completion_percentage: completionPercentage,
          };
        }
      );
      
      // Invalidate and refetch to ensure data consistency
      queryClient.invalidateQueries({ 
        queryKey: ["subtasks", updatedSubtask.task_id] 
      });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
    ...options,
  });
};

/**
 * Hook to delete a subtask
 */
export const useDeleteSubtask = (options?: UseDeleteSubtaskMutationOptions) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (subtaskId: string) => apiClient.deleteSubtask(subtaskId),
    onSuccess: (_, subtaskId) => {
      // Find the subtask to get its task_id
      const subtasksQueries = queryClient.getQueriesData<SubtaskListResponse>({
        queryKey: ["subtasks"],
      });
      
      for (const [queryKey, data] of subtasksQueries) {
        if (!data) continue;
        
        const subtaskToDelete = data.subtasks.find(s => s.id === subtaskId);
        if (subtaskToDelete) {
          // Update this subtasks query
          const updatedSubtasks = data.subtasks.filter(s => s.id !== subtaskId);
          
          // Recalculate stats
          const completedCount = updatedSubtasks.filter(s => s.is_completed).length;
          const completionPercentage = updatedSubtasks.length 
            ? (completedCount / updatedSubtasks.length) * 100 
            : 0;
          
          queryClient.setQueryData<SubtaskListResponse>(queryKey, {
            ...data,
            subtasks: updatedSubtasks,
            total_count: data.total_count - 1,
            completed_count: completedCount,
            completion_percentage: completionPercentage,
          });
          
          // Invalidate and refetch to ensure data consistency
          queryClient.invalidateQueries({ 
            queryKey: ["subtasks", subtaskToDelete.task_id] 
          });
          queryClient.invalidateQueries({ queryKey: ["tasks"] });
          break;
        }
      }
    },
    ...options,
  });
};

/**
 * Hook to reorder subtasks
 */
export const useReorderSubtasks = (options?: UseReorderSubtasksMutationOptions) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ taskId, subtaskIds }) => 
      apiClient.reorderSubtasks(taskId, subtaskIds),
    onSuccess: (result, variables) => {
      // Update the subtasks query cache
      queryClient.setQueryData<SubtaskListResponse>(
        ["subtasks", variables.taskId],
        result
      );
      
      // Invalidate and refetch to ensure data consistency
      queryClient.invalidateQueries({
        queryKey: ["subtasks", variables.taskId]
      });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
    ...options,
  });
};