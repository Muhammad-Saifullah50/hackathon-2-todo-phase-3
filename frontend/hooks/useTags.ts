/**
 * React Query hooks for tag operations.
 * Provides optimistic updates for better UX.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  assignTagsToTask,
  createTag,
  deleteTag,
  getTaskTags,
  getTags,
  removeTagsFromTask,
  updateTag,
} from "@/lib/api/tags";
import type {
  CreateTagRequest,
  TagWithCount,
  UpdateTagRequest,
} from "@/lib/types/tag";
import { useToast } from "./use-toast";

/**
 * Query key factory for tags.
 */
export const tagsKeys = {
  all: ["tags"] as const,
  lists: () => [...tagsKeys.all, "list"] as const,
  list: () => [...tagsKeys.lists()] as const,
  taskTags: (taskId: string) => [...tagsKeys.all, "task", taskId] as const,
};

/**
 * Hook to fetch all tags for the authenticated user.
 */
export function useTags() {
  return useQuery({
    queryKey: tagsKeys.list(),
    queryFn: getTags,
    staleTime: 60000, // Consider data fresh for 1 minute
    gcTime: 10 * 60 * 1000, // Keep unused data in cache for 10 minutes
  });
}

/**
 * Hook to create a new tag with optimistic updates.
 */
export function useCreateTag() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: createTag,

    onMutate: async (newTag: CreateTagRequest) => {
      await queryClient.cancelQueries({ queryKey: tagsKeys.all });

      const previousTags = queryClient.getQueryData(tagsKeys.list());

      // Generate temporary ID for optimistic tag
      const tempId = `temp-${crypto.randomUUID()}`;

      queryClient.setQueryData(tagsKeys.list(), (old: any) => {
        if (!old || !old.data) return old;

        const optimisticTag: TagWithCount = {
          id: tempId,
          name: newTag.name,
          color: newTag.color,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          task_count: 0,
        };

        return {
          ...old,
          data: {
            ...old.data,
            tags: [...(old.data.tags || []), optimisticTag].sort((a, b) =>
              a.name.localeCompare(b.name)
            ),
          },
        };
      });

      return { previousTags };
    },

    onError: (error, _variables, context) => {
      if (context?.previousTags) {
        queryClient.setQueryData(tagsKeys.list(), context.previousTags);
      }

      toast({
        variant: "destructive",
        title: "Failed to create tag",
        description:
          error instanceof Error ? error.message : "An error occurred.",
      });
    },

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tagsKeys.all });

      toast({
        title: "Tag created",
        description: "Your new tag has been created successfully.",
      });
    },
  });
}

/**
 * Hook to update a tag with optimistic updates.
 */
export function useUpdateTag() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ tagId, data }: { tagId: string; data: UpdateTagRequest }) =>
      updateTag(tagId, data),

    onMutate: async ({ tagId, data }) => {
      await queryClient.cancelQueries({ queryKey: tagsKeys.all });

      const previousTags = queryClient.getQueryData(tagsKeys.list());

      queryClient.setQueryData(tagsKeys.list(), (old: any) => {
        if (!old || !old.data || !old.data.tags) return old;

        return {
          ...old,
          data: {
            ...old.data,
            tags: old.data.tags
              .map((tag: TagWithCount) =>
                tag.id === tagId
                  ? {
                      ...tag,
                      name: data.name !== undefined ? data.name : tag.name,
                      color: data.color !== undefined ? data.color : tag.color,
                      updated_at: new Date().toISOString(),
                    }
                  : tag
              )
              .sort((a: TagWithCount, b: TagWithCount) =>
                a.name.localeCompare(b.name)
              ),
          },
        };
      });

      return { previousTags };
    },

    onError: (error, _variables, context) => {
      if (context?.previousTags) {
        queryClient.setQueryData(tagsKeys.list(), context.previousTags);
      }

      toast({
        variant: "destructive",
        title: "Failed to update tag",
        description:
          error instanceof Error ? error.message : "An error occurred.",
      });
    },

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tagsKeys.all });

      toast({
        title: "Tag updated",
        description: "Your tag has been updated successfully.",
      });
    },
  });
}

/**
 * Hook to delete a tag with optimistic updates.
 */
export function useDeleteTag() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (tagId: string) => deleteTag(tagId),

    onMutate: async (tagId) => {
      await queryClient.cancelQueries({ queryKey: tagsKeys.all });

      const previousTags = queryClient.getQueryData(tagsKeys.list());

      queryClient.setQueryData(tagsKeys.list(), (old: any) => {
        if (!old || !old.data || !old.data.tags) return old;

        return {
          ...old,
          data: {
            ...old.data,
            tags: old.data.tags.filter(
              (tag: TagWithCount) => tag.id !== tagId
            ),
          },
        };
      });

      return { previousTags };
    },

    onError: (error, _variables, context) => {
      if (context?.previousTags) {
        queryClient.setQueryData(tagsKeys.list(), context.previousTags);
      }

      toast({
        variant: "destructive",
        title: "Failed to delete tag",
        description:
          error instanceof Error ? error.message : "An error occurred.",
      });
    },

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tagsKeys.all });

      toast({
        title: "Tag deleted",
        description: "The tag and all its associations have been removed.",
      });
    },
  });
}

/**
 * Hook to fetch tags for a specific task.
 */
export function useTaskTags(taskId: string) {
  return useQuery({
    queryKey: tagsKeys.taskTags(taskId),
    queryFn: () => getTaskTags(taskId),
    enabled: !!taskId,
    staleTime: 30000,
    gcTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to assign tags to a task with optimistic updates.
 */
export function useAssignTags() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ taskId, tagIds }: { taskId: string; tagIds: string[] }) =>
      assignTagsToTask(taskId, { tag_ids: tagIds }),

    onMutate: async ({ taskId }) => {
      await queryClient.cancelQueries({
        queryKey: tagsKeys.taskTags(taskId),
      });

      const previousTags = queryClient.getQueryData(tagsKeys.taskTags(taskId));

      return { previousTags, taskId };
    },

    onError: (error, _variables, context) => {
      if (context?.previousTags && context?.taskId) {
        queryClient.setQueryData(
          tagsKeys.taskTags(context.taskId),
          context.previousTags
        );
      }

      toast({
        variant: "destructive",
        title: "Failed to assign tags",
        description:
          error instanceof Error ? error.message : "An error occurred.",
      });
    },

    onSuccess: (data, { taskId }) => {
      // Update the task tags cache with the response data
      queryClient.setQueryData(tagsKeys.taskTags(taskId), data);

      // Invalidate tag list to update counts
      queryClient.invalidateQueries({ queryKey: tagsKeys.list() });

      // Invalidate tasks to refresh tag associations
      queryClient.invalidateQueries({ queryKey: ["tasks"] });

      toast({
        title: "Tags updated",
        description: "Task tags have been updated successfully.",
      });
    },
  });
}

/**
 * Hook to remove tags from a task with optimistic updates.
 */
export function useRemoveTags() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ taskId, tagIds }: { taskId: string; tagIds: string[] }) =>
      removeTagsFromTask(taskId, { tag_ids: tagIds }),

    onMutate: async ({ taskId, tagIds }) => {
      await queryClient.cancelQueries({
        queryKey: tagsKeys.taskTags(taskId),
      });

      const previousTags = queryClient.getQueryData(tagsKeys.taskTags(taskId));

      // Optimistically remove tags from the task
      queryClient.setQueryData(tagsKeys.taskTags(taskId), (old: any) => {
        if (!old || !old.data || !old.data.tags) return old;

        const tagIdSet = new Set(tagIds);

        return {
          ...old,
          data: {
            ...old.data,
            tags: old.data.tags.filter(
              (tag: TagWithCount) => !tagIdSet.has(tag.id)
            ),
          },
        };
      });

      return { previousTags, taskId };
    },

    onError: (error, _variables, context) => {
      if (context?.previousTags && context?.taskId) {
        queryClient.setQueryData(
          tagsKeys.taskTags(context.taskId),
          context.previousTags
        );
      }

      toast({
        variant: "destructive",
        title: "Failed to remove tags",
        description:
          error instanceof Error ? error.message : "An error occurred.",
      });
    },

    onSuccess: (data, { taskId }) => {
      // Update the task tags cache with the response data
      queryClient.setQueryData(tagsKeys.taskTags(taskId), data);

      // Invalidate tag list to update counts
      queryClient.invalidateQueries({ queryKey: tagsKeys.list() });

      // Invalidate tasks to refresh tag associations
      queryClient.invalidateQueries({ queryKey: ["tasks"] });

      toast({
        title: "Tags removed",
        description: "Tags have been removed from the task.",
      });
    },
  });
}
