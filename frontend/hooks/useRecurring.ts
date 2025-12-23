"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export interface RecurrencePattern {
  id: string;
  task_id: string;
  frequency: "daily" | "weekly" | "monthly";
  interval: number;
  days_of_week?: number[] | null;
  day_of_month?: number | null;
  end_date?: string | null;
  next_occurrence_date: string;
  created_at: string;
  updated_at: string;
}

export interface RecurrencePatternCreate {
  frequency: "daily" | "weekly" | "monthly";
  interval: number;
  days_of_week?: number[] | null;
  day_of_month?: number | null;
  end_date?: string | null;
}

export interface RecurrencePatternUpdate {
  frequency?: "daily" | "weekly" | "monthly";
  interval?: number;
  days_of_week?: number[] | null;
  day_of_month?: number | null;
  end_date?: string | null;
}

export interface RecurrencePreview {
  dates: string[];
  count: number;
}

/**
 * Hook to fetch recurrence pattern for a task
 */
export function useRecurrencePattern(taskId: string | undefined) {
  return useQuery<RecurrencePattern>({
    queryKey: ["recurrence", taskId],
    queryFn: async () => {
      const response = await api.get(`/api/v1/tasks/${taskId}/recurrence`);
      return response.data;
    },
    enabled: !!taskId,
    retry: false, // Don't retry if pattern doesn't exist
  });
}

/**
 * Hook to preview upcoming occurrences
 */
export function useRecurrencePreview(taskId: string | undefined, count: number = 5) {
  return useQuery<RecurrencePreview>({
    queryKey: ["recurrence-preview", taskId, count],
    queryFn: async () => {
      const response = await api.get(
        `/api/v1/tasks/${taskId}/recurrence/preview?count=${count}`
      );
      return response.data;
    },
    enabled: !!taskId,
  });
}

/**
 * Hook to create recurrence pattern
 */
export function useCreateRecurrence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      taskId,
      data,
    }: {
      taskId: string;
      data: RecurrencePatternCreate;
    }) => {
      const response = await api.post(`/api/v1/tasks/${taskId}/recurrence`, data);
      return response.data;
    },
    onSuccess: (_, { taskId }) => {
      queryClient.invalidateQueries({ queryKey: ["recurrence", taskId] });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}

/**
 * Hook to update recurrence pattern
 */
export function useUpdateRecurrence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      taskId,
      data,
    }: {
      taskId: string;
      data: RecurrencePatternUpdate;
    }) => {
      const response = await api.patch(`/api/v1/tasks/${taskId}/recurrence`, data);
      return response.data;
    },
    onSuccess: (_, { taskId }) => {
      queryClient.invalidateQueries({ queryKey: ["recurrence", taskId] });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}

/**
 * Hook to delete recurrence pattern (stop recurrence)
 */
export function useDeleteRecurrence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (taskId: string) => {
      await api.delete(`/api/v1/tasks/${taskId}/recurrence`);
    },
    onSuccess: (_, taskId) => {
      queryClient.invalidateQueries({ queryKey: ["recurrence", taskId] });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}
