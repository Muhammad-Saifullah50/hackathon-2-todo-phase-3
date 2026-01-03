"use client";

/**
 * Hook to sync task data when chatbot makes changes.
 *
 * This hook handles cache revalidation for task data:
 * 1. Uses router.refresh() to trigger server component re-renders
 * 2. Invalidates React Query cache to refresh client-side data
 * 3. Optionally refetches on window focus (for when user returns to tab)
 *
 * Note: Polling has been removed in favor of on-demand revalidation.
 * Server Actions automatically revalidate cache after mutations.
 */

import { useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';

export interface UseChatTaskSyncOptions {
  /**
   * Enable refetch on window focus (when user returns to tab)
   * @default true
   */
  refetchOnWindowFocus?: boolean;

  /**
   * Enable refetch on tab visibility change
   * @default true
   */
  refetchOnVisibilityChange?: boolean;
}

/**
 * Sync task data after chatbot interactions.
 * Invalidates both Next.js server cache and React Query client cache.
 *
 * @example
 * ```tsx
 * // In your chat page/component
 * function ChatPage() {
 *   useChatTaskSync();
 *   return <ChatInterface />;
 * }
 * ```
 */
export function useChatTaskSync(options: UseChatTaskSyncOptions = {}) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const lastRevalidationRef = useRef<number>(0);

  const {
    refetchOnWindowFocus = true,
    refetchOnVisibilityChange = true,
  } = options;

  /**
   * Function to trigger revalidation of all task data.
   * This invalidates both Next.js server cache and React Query client cache.
   */
  const revalidateTasks = useCallback(async () => {
    const now = Date.now();
    // Reduced debounce: don't revalidate if we just did it (within 200ms)
    if (now - lastRevalidationRef.current < 200) {
      console.log('[ChatTaskSync] Skipping revalidation (debounced)');
      return;
    }
    lastRevalidationRef.current = now;

    console.log('🔄 [ChatTaskSync] INSTANT REVALIDATION TRIGGERED');

    // 1. FORCE immediate refetch of tasks (this updates UI instantly)
    console.log('⚡ [ChatTaskSync] Force refetching ALL task queries...');
    await Promise.all([
      queryClient.refetchQueries({ queryKey: ['tasks'] }),
      queryClient.refetchQueries({ queryKey: ['task'] }),
      queryClient.refetchQueries({ queryKey: ['analytics'] }),
      queryClient.refetchQueries({ queryKey: ['tags'] }),
    ]);

    // 2. Invalidate ALL caches to mark as stale
    console.log('🗑️ [ChatTaskSync] Invalidating all caches...');
    queryClient.invalidateQueries({ queryKey: ['tasks'] });
    queryClient.invalidateQueries({ queryKey: ['task'] });
    queryClient.invalidateQueries({ queryKey: ['analytics'] });
    queryClient.invalidateQueries({ queryKey: ['tags'] });
    queryClient.invalidateQueries({ queryKey: ['trash'] });

    // 3. Trigger Next.js router refresh for server components
    console.log('🔃 [ChatTaskSync] Refreshing Next.js router...');
    router.refresh();

    // 4. Trigger Next.js server-side revalidation via API (async, non-blocking)
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'}/api/revalidate/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'chatbot_task_change' }),
    }).catch(error => {
      console.error('[ChatTaskSync] Failed to trigger server revalidation:', error);
    });

    console.log('✅ [ChatTaskSync] Revalidation complete - UI should update NOW');
  }, [queryClient, router]);

  // Expose revalidateTasks globally for chatbot to call
  useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).__revalidateTasks = revalidateTasks;
      console.log('[ChatTaskSync] Exposed __revalidateTasks globally');
    }
  }, [revalidateTasks]);

  // Set up window focus listener
  useEffect(() => {
    if (!refetchOnWindowFocus) return;

    const handleFocus = () => {
      console.log('[ChatTaskSync] Window gained focus, refetching...');
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.refetchQueries({ queryKey: ['tasks'] });
      router.refresh();
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [refetchOnWindowFocus, queryClient, router]);

  // Set up visibility change listener
  useEffect(() => {
    if (!refetchOnVisibilityChange) return;

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        console.log('[ChatTaskSync] Tab became visible, refetching...');
        queryClient.invalidateQueries({ queryKey: ['tasks'] });
        queryClient.refetchQueries({ queryKey: ['tasks'] });
        router.refresh();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [refetchOnVisibilityChange, queryClient, router]);

  return { revalidateTasks };
}

/**
 * Helper function to call from chatbot callbacks after task modifications.
 * Triggers immediate revalidation of all task data.
 */
export function triggerTaskRevalidation() {
  if (typeof window !== 'undefined' && (window as any).__revalidateTasks) {
    console.log('[ChatTaskSync] triggerTaskRevalidation called');
    (window as any).__revalidateTasks();
  }
}
