/**
 * React Query hooks for search operations.
 * Provides debounced search and quick filter functionality.
 */

import { useQuery } from '@tanstack/react-query';
import { useState, useCallback, useMemo, useEffect } from 'react';
import {
  searchTasks,
  getAutocompleteSuggestions,
  getQuickFilters,
  type SearchParams,
} from '@/lib/api/search';

/**
 * Debounce delay for search input (ms).
 */
const SEARCH_DEBOUNCE_MS = 300;

/**
 * Query key factory for search operations.
 */
export const searchKeys = {
  all: ['search'] as const,
  search: (params: SearchParams) => [...searchKeys.all, 'results', params] as const,
  autocomplete: (query: string) => [...searchKeys.all, 'autocomplete', query] as const,
  quickFilters: () => [...searchKeys.all, 'quick-filters'] as const,
};

/**
 * Hook to manage search state with debouncing.
 *
 * @param initialQuery - Initial search query
 * @param debounceMs - Debounce delay in milliseconds
 * @returns Object with search state and handlers
 */
export function useSearchInput(initialQuery = '', debounceMs = SEARCH_DEBOUNCE_MS) {
  const [inputValue, setInputValue] = useState(initialQuery);
  const [debouncedValue, setDebouncedValue] = useState(initialQuery);

  // Debounce the input value
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(inputValue);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [inputValue, debounceMs]);

  // Clear search
  const clearSearch = useCallback(() => {
    setInputValue('');
    setDebouncedValue('');
  }, []);

  return {
    inputValue,
    debouncedValue,
    setInputValue,
    clearSearch,
    isDebouncing: inputValue !== debouncedValue,
  };
}

/**
 * Hook to search tasks with combined filters.
 *
 * @param params - Search parameters including query and filters
 * @returns React Query result with search results
 */
export function useSearchTasks(params: SearchParams) {
  const hasSearchCriteria = Boolean(
    params.q ||
      params.status ||
      params.priority ||
      (params.tags && params.tags.length > 0) ||
      params.due_date_from ||
      params.due_date_to ||
      params.has_due_date !== undefined ||
      params.has_notes !== undefined
  );

  return useQuery({
    queryKey: searchKeys.search(params),
    queryFn: () => searchTasks(params),
    enabled: hasSearchCriteria,
    staleTime: 30000,
    gcTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to get autocomplete suggestions.
 *
 * @param query - Search query prefix
 * @param limit - Maximum suggestions to return
 * @returns React Query result with suggestions
 */
export function useAutocomplete(query: string, limit = 5) {
  return useQuery({
    queryKey: searchKeys.autocomplete(query),
    queryFn: () => getAutocompleteSuggestions(query, limit),
    enabled: query.length >= 1,
    staleTime: 30000,
    gcTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to get quick filter options with counts.
 *
 * @returns React Query result with quick filters
 */
export function useQuickFilters() {
  return useQuery({
    queryKey: searchKeys.quickFilters(),
    queryFn: getQuickFilters,
    staleTime: 30000,
    gcTime: 5 * 60 * 1000,
  });
}

/**
 * Active filter state type.
 */
export interface ActiveFilters {
  query: string;
  status?: 'pending' | 'completed';
  priority?: 'low' | 'medium' | 'high';
  tags: string[];
  dueDateFilter?: 'today' | 'this_week' | 'overdue';
  hasDueDate?: boolean;
  hasNotes?: boolean;
}

/**
 * Hook to manage combined search and filter state.
 *
 * @returns Object with filter state and handlers
 */
export function useSearchFilters() {
  const [filters, setFilters] = useState<ActiveFilters>({
    query: '',
    tags: [],
  });

  // Apply quick filter
  const applyQuickFilter = useCallback((filterId: string) => {
    setFilters((prev) => {
      // Toggle filter if already active
      if (prev.dueDateFilter === filterId) {
        return {
          ...prev,
          dueDateFilter: undefined,
        };
      }

      // Handle priority filter specially
      if (filterId === 'high_priority') {
        return {
          ...prev,
          priority: prev.priority === 'high' ? undefined : 'high',
          dueDateFilter: undefined,
        };
      }

      // Apply date-based filter
      return {
        ...prev,
        dueDateFilter: filterId as 'today' | 'this_week' | 'overdue',
        priority: undefined, // Clear priority when applying date filter
      };
    });
  }, []);

  // Set search query
  const setQuery = useCallback((query: string) => {
    setFilters((prev) => ({ ...prev, query }));
  }, []);

  // Set status filter
  const setStatusFilter = useCallback((status?: 'pending' | 'completed') => {
    setFilters((prev) => ({ ...prev, status }));
  }, []);

  // Set priority filter
  const setPriorityFilter = useCallback((priority?: 'low' | 'medium' | 'high') => {
    setFilters((prev) => ({ ...prev, priority }));
  }, []);

  // Set tag filters
  const setTagFilters = useCallback((tags: string[]) => {
    setFilters((prev) => ({ ...prev, tags }));
  }, []);

  // Clear all filters
  const clearAllFilters = useCallback(() => {
    setFilters({
      query: '',
      tags: [],
    });
  }, []);

  // Check if any filter is active
  const hasActiveFilters = useMemo(() => {
    return Boolean(
      filters.query ||
        filters.status ||
        filters.priority ||
        filters.tags.length > 0 ||
        filters.dueDateFilter ||
        filters.hasDueDate !== undefined ||
        filters.hasNotes !== undefined
    );
  }, [filters]);

  // Count active filters
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.query) count++;
    if (filters.status) count++;
    if (filters.priority) count++;
    if (filters.tags.length > 0) count++;
    if (filters.dueDateFilter) count++;
    if (filters.hasDueDate !== undefined) count++;
    if (filters.hasNotes !== undefined) count++;
    return count;
  }, [filters]);

  return {
    filters,
    setQuery,
    setStatusFilter,
    setPriorityFilter,
    setTagFilters,
    applyQuickFilter,
    clearAllFilters,
    hasActiveFilters,
    activeFilterCount,
  };
}

/**
 * Convert ActiveFilters to SearchParams for API call.
 *
 * @param filters - Active filter state
 * @returns SearchParams for API call
 */
export function filtersToSearchParams(filters: ActiveFilters): SearchParams {
  const params: SearchParams = {
    q: filters.query || undefined,
    status: filters.status,
    priority: filters.priority,
    tags: filters.tags.length > 0 ? filters.tags : undefined,
    has_due_date: filters.hasDueDate,
    has_notes: filters.hasNotes,
  };

  // Convert dueDateFilter to date range
  if (filters.dueDateFilter) {
    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const todayEnd = new Date(todayStart);
    todayEnd.setDate(todayEnd.getDate() + 1);

    switch (filters.dueDateFilter) {
      case 'today':
        params.due_date_from = todayStart.toISOString();
        params.due_date_to = todayEnd.toISOString();
        break;
      case 'this_week':
        const weekEnd = new Date(todayStart);
        weekEnd.setDate(weekEnd.getDate() + 7);
        params.due_date_from = todayStart.toISOString();
        params.due_date_to = weekEnd.toISOString();
        break;
      case 'overdue':
        params.due_date_to = todayStart.toISOString();
        break;
    }
  }

  return params;
}
