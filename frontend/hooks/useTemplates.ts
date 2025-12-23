import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";

interface SubtaskTemplateItem {
  description: string;
}

interface Template {
  id: string;
  user_id: string;
  name: string;
  title: string;
  description: string | null;
  priority: "low" | "medium" | "high";
  subtasks_template: SubtaskTemplateItem[] | null;
  tags: Array<{ id: string; name: string; color: string }>;
  created_at: string;
  updated_at: string;
}

interface TemplateListResponse {
  templates: Template[];
  total: number;
  page: number;
  page_size: number;
}

interface CreateTemplateData {
  name: string;
  title: string;
  description?: string;
  priority: "low" | "medium" | "high";
  subtasks_template?: SubtaskTemplateItem[];
  tag_ids?: string[];
}

interface UpdateTemplateData {
  name?: string;
  title?: string;
  description?: string;
  priority?: "low" | "medium" | "high";
  subtasks_template?: SubtaskTemplateItem[];
  tag_ids?: string[];
}

interface SaveTaskAsTemplateData {
  task_id: string;
  template_name: string;
  include_subtasks?: boolean;
  include_tags?: boolean;
}

export function useTemplates(page = 1, pageSize = 50) {
  return useQuery<TemplateListResponse>({
    queryKey: ["templates", page, pageSize],
    queryFn: async () => {
      const response = await api.get(`/api/v1/templates?page=${page}&page_size=${pageSize}`);
      return response.data;
    },
  });
}

export function useTemplate(templateId: string) {
  return useQuery<Template>({
    queryKey: ["templates", templateId],
    queryFn: async () => {
      const response = await api.get(`/api/v1/templates/${templateId}`);
      return response.data;
    },
    enabled: !!templateId,
  });
}

export function useCreateTemplate() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: async (data: CreateTemplateData) => {
      const response = await api.post(`/api/v1/templates`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["templates"] });
      toast({
        title: "Template created",
        description: "Your template has been created successfully.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message || "Failed to create template",
        variant: "destructive",
      });
    },
  });
}

export function useUpdateTemplate() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: async ({ templateId, data }: { templateId: string; data: UpdateTemplateData }) => {
      const response = await api.patch(`/api/v1/templates/${templateId}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["templates"] });
      toast({
        title: "Template updated",
        description: "Your template has been updated successfully.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message || "Failed to update template",
        variant: "destructive",
      });
    },
  });
}

export function useDeleteTemplate() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: async (templateId: string) => {
      const response = await api.delete(`/api/v1/templates/${templateId}`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["templates"] });
      toast({
        title: "Template deleted",
        description: "Your template has been deleted successfully.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message || "Failed to delete template",
        variant: "destructive",
      });
    },
  });
}

export function useApplyTemplate() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: async ({ templateId, dueDate }: { templateId: string; dueDate?: string }) => {
      const response = await api.post(`/api/v1/templates/${templateId}/apply`, {
        due_date: dueDate,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast({
        title: "Task created from template",
        description: "A new task has been created from your template.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message || "Failed to create task from template",
        variant: "destructive",
      });
    },
  });
}

export function useSaveTaskAsTemplate() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: async (data: SaveTaskAsTemplateData) => {
      const params = new URLSearchParams({
        template_name: data.template_name,
        include_subtasks: String(data.include_subtasks ?? true),
        include_tags: String(data.include_tags ?? true),
      });
      const response = await api.post(
        `/api/v1/templates/tasks/${data.task_id}/save-as-template?${params}`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["templates"] });
      toast({
        title: "Template saved",
        description: "Your task has been saved as a template.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message || "Failed to save task as template",
        variant: "destructive",
      });
    },
  });
}
