/**
 * API client for search-related operations.
 * Provides typed functions for task search, autocomplete, and quick filters.
 */

import api from '../api';
import type { StandardizedResponse } from '../types/task';

/**
 * Search parameters for task search.
 */
export interface SearchParams {
  q?: string;
  status?: 'pending' | 'completed';
  priority?: 'low' | 'medium' | 'high';
  tags?: string[];
  due_date_from?: string;
  due_date_to?: string;
  has_due_date?: boolean;
  has_notes?: boolean;
  page?: number;
  limit?: number;
}

/**
 * Autocomplete suggestion from the API.
 */
export interface AutocompleteSuggestion {
  id: string;
  title: string;
  status: string;
}

/**
 * Quick filter option with count.
 */
export interface QuickFilterOption {
  id: string;
  label: string;
  count: number;
  filter_params: Record<string, string>;
}

/**
 * Search response from the API.
 */
export interface SearchResponse {
  tasks: Array<{
    id: string;
    title: string;
    description: string | null;
    status: string;
    priority: string;
    due_date: string | null;
    created_at: string;
    updated_at: string;
    [key: string]: unknown;
  }>;
  query: string | null;
  total_results: number;
  metadata: {
    total_pending: number;
    total_completed: number;
    total_active: number;
    total_deleted: number;
  };
  pagination: {
    page: number;
    limit: number;
    total_items: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

/**
 * Autocomplete response from the API.
 */
export interface AutocompleteResponse {
  suggestions: AutocompleteSuggestion[];
}

/**
 * Quick filters response from the API.
 */
export interface QuickFiltersResponse {
  filters: QuickFilterOption[];
}

/**
 * Search tasks with combined filters.
 *
 * @param params - Search parameters including query and filters
 * @returns Promise resolving to search results with pagination
 */
export async function searchTasks(
  params: SearchParams = {}
): Promise<StandardizedResponse<SearchResponse>> {
  const response = await api.get<StandardizedResponse<SearchResponse>>('/api/v1/tasks/search', {
    params: {
      q: params.q || '',
      status: params.status || undefined,
      priority: params.priority || undefined,
      tags: params.tags && params.tags.length > 0 ? params.tags.join(',') : undefined,
      due_date_from: params.due_date_from || undefined,
      due_date_to: params.due_date_to || undefined,
      has_due_date: params.has_due_date !== undefined ? params.has_due_date : undefined,
      has_notes: params.has_notes !== undefined ? params.has_notes : undefined,
      page: params.page || 1,
      limit: params.limit || 20,
    },
  });
  return response.data;
}

/**
 * Get autocomplete suggestions for task search.
 *
 * @param query - Search query prefix
 * @param limit - Maximum suggestions to return (default 5)
 * @returns Promise resolving to autocomplete suggestions
 */
export async function getAutocompleteSuggestions(
  query: string,
  limit: number = 5
): Promise<StandardizedResponse<AutocompleteResponse>> {
  const response = await api.get<StandardizedResponse<AutocompleteResponse>>(
    '/api/v1/tasks/autocomplete',
    {
      params: { q: query, limit },
    }
  );
  return response.data;
}

/**
 * Get quick filter options with counts.
 *
 * @returns Promise resolving to quick filters with task counts
 */
export async function getQuickFilters(): Promise<StandardizedResponse<QuickFiltersResponse>> {
  const response = await api.get<StandardizedResponse<QuickFiltersResponse>>(
    '/api/v1/tasks/quick-filters'
  );
  return response.data;
}
