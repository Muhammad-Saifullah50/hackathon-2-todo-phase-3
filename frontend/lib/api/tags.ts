/**
 * API client functions for tag operations.
 */

import api from "@/lib/api";
import type { StandardizedResponse } from "@/lib/types/task";
import type {
  CreateTagRequest,
  Tag,
  TagAssignRequest,
  TagAssignResponse,
  TagListResponse,
  UpdateTagRequest,
} from "@/lib/types/tag";

/**
 * Get all tags for the authenticated user.
 */
export async function getTags(): Promise<StandardizedResponse<TagListResponse>> {
  const response = await api.get<StandardizedResponse<TagListResponse>>("/api/v1/tags/");
  return response.data;
}

/**
 * Create a new tag.
 */
export async function createTag(
  data: CreateTagRequest
): Promise<StandardizedResponse<Tag>> {
  const response = await api.post<StandardizedResponse<Tag>>("/api/v1/tags/", data);
  return response.data;
}

/**
 * Update an existing tag.
 */
export async function updateTag(
  tagId: string,
  data: UpdateTagRequest
): Promise<StandardizedResponse<Tag>> {
  const response = await api.patch<StandardizedResponse<Tag>>(`/api/v1/tags/${tagId}`, data);
  return response.data;
}

/**
 * Delete a tag.
 */
export async function deleteTag(
  tagId: string
): Promise<StandardizedResponse<{ tag_id: string }>> {
  const response = await api.delete<StandardizedResponse<{ tag_id: string }>>(
    `/api/v1/tags/${tagId}`
  );
  return response.data;
}

/**
 * Get tags for a specific task.
 */
export async function getTaskTags(
  taskId: string
): Promise<StandardizedResponse<TagAssignResponse>> {
  const response = await api.get<StandardizedResponse<TagAssignResponse>>(
    `/api/v1/tags/tasks/${taskId}/tags`
  );
  return response.data;
}

/**
 * Assign tags to a task.
 */
export async function assignTagsToTask(
  taskId: string,
  data: TagAssignRequest
): Promise<StandardizedResponse<TagAssignResponse>> {
  const response = await api.post<StandardizedResponse<TagAssignResponse>>(
    `/api/v1/tags/tasks/${taskId}/tags`,
    data
  );
  return response.data;
}

/**
 * Remove tags from a task.
 */
export async function removeTagsFromTask(
  taskId: string,
  data: TagAssignRequest
): Promise<StandardizedResponse<TagAssignResponse>> {
  const response = await api.delete<StandardizedResponse<TagAssignResponse>>(
    `/api/v1/tags/tasks/${taskId}/tags`,
    { data }
  );
  return response.data;
}
