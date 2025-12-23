"use client";

import { useState } from "react";
import { FileText, Loader2, Pencil, Trash2, Plus, CheckSquare } from "lucide-react";
import { useTemplates, useDeleteTemplate, useUpdateTemplate } from "@/hooks/useTemplates";
import { useTags } from "@/hooks/useTags";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";

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

const priorityColors = {
  low: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  high: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

export function TemplateManagement() {
  const { data, isLoading } = useTemplates();
  const deleteTemplate = useDeleteTemplate();
  const updateTemplate = useUpdateTemplate();
  const { data: tagsData } = useTags();

  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null);
  const [deleteTemplateId, setDeleteTemplateId] = useState<string | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  // Edit form state
  const [editFormData, setEditFormData] = useState({
    name: "",
    title: "",
    description: "",
    priority: "medium" as "low" | "medium" | "high",
    subtasks_template: [] as SubtaskTemplateItem[],
    tag_ids: [] as string[],
  });

  const allTags = tagsData?.data?.tags || [];

  const handleEditClick = (template: Template) => {
    setEditingTemplate(template);
    setEditFormData({
      name: template.name,
      title: template.title,
      description: template.description || "",
      priority: template.priority,
      subtasks_template: template.subtasks_template || [],
      tag_ids: template.tags.map((t) => t.id),
    });
    setIsEditDialogOpen(true);
  };

  const handleDeleteClick = (templateId: string) => {
    setDeleteTemplateId(templateId);
    setIsDeleteDialogOpen(true);
  };

  const handleEditSubmit = async () => {
    if (!editingTemplate) return;

    try {
      await updateTemplate.mutateAsync({
        templateId: editingTemplate.id,
        data: {
          name: editFormData.name,
          title: editFormData.title,
          description: editFormData.description || undefined,
          priority: editFormData.priority,
          subtasks_template: editFormData.subtasks_template.length > 0
            ? editFormData.subtasks_template
            : undefined,
          tag_ids: editFormData.tag_ids.length > 0 ? editFormData.tag_ids : undefined,
        },
      });
      setIsEditDialogOpen(false);
      setEditingTemplate(null);
    } catch (error) {
      console.error("Failed to update template:", error);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTemplateId) return;

    try {
      await deleteTemplate.mutateAsync(deleteTemplateId);
      setIsDeleteDialogOpen(false);
      setDeleteTemplateId(null);
    } catch (error) {
      console.error("Failed to delete template:", error);
    }
  };

  const addSubtask = () => {
    setEditFormData((prev) => ({
      ...prev,
      subtasks_template: [...prev.subtasks_template, { description: "" }],
    }));
  };

  const updateSubtask = (index: number, description: string) => {
    setEditFormData((prev) => ({
      ...prev,
      subtasks_template: prev.subtasks_template.map((s, i) =>
        i === index ? { description } : s
      ),
    }));
  };

  const removeSubtask = (index: number) => {
    setEditFormData((prev) => ({
      ...prev,
      subtasks_template: prev.subtasks_template.filter((_, i) => i !== index),
    }));
  };

  const toggleTagSelection = (tagId: string) => {
    setEditFormData((prev) => ({
      ...prev,
      tag_ids: prev.tag_ids.includes(tagId)
        ? prev.tag_ids.filter((id) => id !== tagId)
        : [...prev.tag_ids, tagId],
    }));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const templates = data?.templates || [];

  if (templates.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <FileText className="h-12 w-12 text-muted-foreground/50 mb-4" />
        <h3 className="text-lg font-medium mb-2">No templates yet</h3>
        <p className="text-sm text-muted-foreground max-w-sm">
          Save a task as a template to create reusable task structures. Templates help you
          quickly create tasks with pre-filled information.
        </p>
      </div>
    );
  }

  return (
    <>
      <ScrollArea className="max-h-[600px]">
        <div className="space-y-4">
          {templates.map((template) => (
            <div
              key={template.id}
              className="rounded-lg border p-4 hover:bg-accent/50 transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <h3 className="font-medium">{template.name}</h3>
                  </div>
                  <p className="text-sm font-medium text-foreground">{template.title}</p>
                  {template.description && (
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {template.description}
                    </p>
                  )}
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge
                      variant="secondary"
                      className={priorityColors[template.priority]}
                    >
                      {template.priority}
                    </Badge>
                    {template.tags.map((tag) => (
                      <Badge
                        key={tag.id}
                        variant="outline"
                        style={{
                          backgroundColor: `${tag.color}20`,
                          color: tag.color,
                          borderColor: tag.color,
                        }}
                      >
                        {tag.name}
                      </Badge>
                    ))}
                    {template.subtasks_template && template.subtasks_template.length > 0 && (
                      <Badge variant="outline" className="flex items-center gap-1">
                        <CheckSquare className="h-3 w-3" />
                        {template.subtasks_template.length} subtask
                        {template.subtasks_template.length !== 1 ? "s" : ""}
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Created {new Date(template.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleEditClick(template)}
                  >
                    <Pencil className="h-4 w-4 mr-1" />
                    Edit
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-destructive hover:bg-destructive hover:text-destructive-foreground"
                    onClick={() => handleDeleteClick(template.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>

      {/* Edit Template Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Template</DialogTitle>
            <DialogDescription>
              Update your template details and settings
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="template-name">Template Name</Label>
              <Input
                id="template-name"
                value={editFormData.name}
                onChange={(e) =>
                  setEditFormData((prev) => ({ ...prev, name: e.target.value }))
                }
                placeholder="e.g., Weekly Review"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="template-title">Task Title</Label>
              <Input
                id="template-title"
                value={editFormData.title}
                onChange={(e) =>
                  setEditFormData((prev) => ({ ...prev, title: e.target.value }))
                }
                placeholder="e.g., Weekly team review"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="template-description">Description</Label>
              <Textarea
                id="template-description"
                value={editFormData.description}
                onChange={(e) =>
                  setEditFormData((prev) => ({ ...prev, description: e.target.value }))
                }
                placeholder="Optional description..."
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="template-priority">Priority</Label>
              <Select
                value={editFormData.priority}
                onValueChange={(value: "low" | "medium" | "high") =>
                  setEditFormData((prev) => ({ ...prev, priority: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Tags Selection */}
            {allTags.length > 0 && (
              <div className="space-y-2">
                <Label>Tags</Label>
                <div className="flex flex-wrap gap-2 p-3 border rounded-md">
                  {allTags.map((tag) => (
                    <div
                      key={tag.id}
                      className="flex items-center space-x-2"
                    >
                      <Checkbox
                        id={`tag-${tag.id}`}
                        checked={editFormData.tag_ids.includes(tag.id)}
                        onCheckedChange={() => toggleTagSelection(tag.id)}
                      />
                      <label
                        htmlFor={`tag-${tag.id}`}
                        className="flex items-center gap-1 cursor-pointer"
                      >
                        <Badge
                          variant="outline"
                          style={{
                            backgroundColor: `${tag.color}20`,
                            color: tag.color,
                            borderColor: tag.color,
                          }}
                        >
                          {tag.name}
                        </Badge>
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Subtasks Section */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Subtasks</Label>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={addSubtask}
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Add Subtask
                </Button>
              </div>
              <div className="space-y-2">
                {editFormData.subtasks_template.map((subtask, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <Input
                      value={subtask.description}
                      onChange={(e) => updateSubtask(index, e.target.value)}
                      placeholder={`Subtask ${index + 1}`}
                    />
                    <Button
                      type="button"
                      size="icon"
                      variant="ghost"
                      className="shrink-0 text-destructive hover:text-destructive"
                      onClick={() => removeSubtask(index)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
                {editFormData.subtasks_template.length === 0 && (
                  <p className="text-sm text-muted-foreground py-2">
                    No subtasks defined for this template
                  </p>
                )}
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsEditDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={handleEditSubmit}
              disabled={updateTemplate.isPending || !editFormData.name || !editFormData.title}
            >
              {updateTemplate.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save Changes"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Template</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this template? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              disabled={deleteTemplate.isPending}
            >
              {deleteTemplate.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                "Delete"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
