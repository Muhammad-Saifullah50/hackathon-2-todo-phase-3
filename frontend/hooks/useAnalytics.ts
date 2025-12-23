import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { authClient } from "@/lib/auth-client";

interface AnalyticsStatsData {
  pending_count: number;
  completed_today_count: number;
  overdue_count: number;
  total_count: number;
}

interface AnalyticsStatsResponse {
  success: boolean;
  message: string;
  data: AnalyticsStatsData;
}

interface CompletionTrendDataPoint {
  date: string;
  completed: number;
  created: number;
}

interface CompletionTrendData {
  data: CompletionTrendDataPoint[];
  days: number;
}

interface CompletionTrendResponse {
  success: boolean;
  message: string;
  data: CompletionTrendData;
}

interface PriorityBreakdownItem {
  priority: string;
  count: number;
  percentage: number;
}

interface PriorityBreakdownData {
  data: PriorityBreakdownItem[];
  total: number;
}

interface PriorityBreakdownResponse {
  success: boolean;
  message: string;
  data: PriorityBreakdownData;
}

/**
 * Hook to fetch analytics statistics (pending, completed today, overdue, total)
 */
export function useAnalyticsStats() {
  const { data: session } = authClient.useSession();

  return useQuery<AnalyticsStatsResponse>({
    queryKey: ["analytics", "stats"],
    queryFn: async () => {
      const response = await apiClient.get("/api/v1/tasks/analytics/stats");
      return response.data;
    },
    staleTime: 2000, // Cache for 2 seconds - short stale time for real-time dashboard updates
    refetchOnWindowFocus: true,
    enabled: !!session, // Only fetch when authenticated
  });
}

/**
 * Hook to fetch completion trend data for the last N days
 * @param days Number of days to fetch (default: 7, max: 30)
 */
export function useCompletionTrend(days: number = 7) {
  const { data: session } = authClient.useSession();

  return useQuery<CompletionTrendResponse>({
    queryKey: ["analytics", "completion-trend", days],
    queryFn: async () => {
      const response = await apiClient.get(
        `/api/v1/tasks/analytics/completion-trend?days=${days}`
      );
      return response.data;
    },
    staleTime: 2000, // Cache for 2 seconds - short stale time for real-time dashboard updates
    refetchOnWindowFocus: true,
    enabled: !!session, // Only fetch when authenticated
  });
}

/**
 * Hook to fetch priority breakdown (low, medium, high)
 */
export function usePriorityBreakdown() {
  const { data: session } = authClient.useSession();

  return useQuery<PriorityBreakdownResponse>({
    queryKey: ["analytics", "priority-breakdown"],
    queryFn: async () => {
      const response = await apiClient.get("/api/v1/tasks/analytics/priority-breakdown");
      return response.data;
    },
    staleTime: 2000, // Cache for 2 seconds - short stale time for real-time dashboard updates
    refetchOnWindowFocus: true,
    enabled: !!session, // Only fetch when authenticated
  });
}
