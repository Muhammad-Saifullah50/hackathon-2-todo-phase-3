"use client";

/**
 * Hook to sync task data when chatbot makes changes.
 *
 * Invalidates React Query caches on-demand rather than polling or
 * triple-cascading.  TanStack Query's built-in refetchOnWindowFocus
 * handles tab-return revalidation; we do not duplicate it here.
 */

import { useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';

import { tasksKeys } from './useTasks';

/**
 * Sync task data after chatbot interactions.
 * Invalidates relevant React Query caches and triggers a router refresh.
 * Uses explicit query-key invalidation matching the pattern from useTasks mutation hooks.
 */
export function useChatTaskSync() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const lastRevalidationRef = useRef<number>(0);

  const revalidateTasks = useCallback(async () => {
    const now = Date.now();
    if (now - lastRevalidationRef.current < 1000) return;
    lastRevalidationRef.current = now;

    queryClient.invalidateQueries({ queryKey: tasksKeys.lists() });
    queryClient.invalidateQueries({ queryKey: ['analytics'] });
    queryClient.invalidateQueries({ queryKey: ['tags'] });
    queryClient.invalidateQueries({ queryKey: [...tasksKeys.all, 'trash'] });
    router.refresh();
  }, [queryClient, router]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).__revalidateTasks = revalidateTasks;
    }
  }, [revalidateTasks]);

  return { revalidateTasks };
}

/**
 * Helper function to call from chatbot callbacks after task modifications.
 */
export function triggerTaskRevalidation() {
  if (typeof window !== 'undefined' && (window as any).__revalidateTasks) {
    (window as any).__revalidateTasks();
  }
}
