"use client";

/**
 * EditTaskDialog Component - Modal for editing task title, description, due date, and tags.
 * Client Component because it needs form state, validation, and submit handlers.
 */

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { format, parseISO } from "date-fns";
import { Task } from "@/lib/types/task";
import { useUpdateTask } from "@/hooks/useTasks";
import { useAssignTags } from "@/hooks/useTags";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";
import { DueDatePicker } from "./DueDatePicker";
import { TagPicker } from "./TagPicker";
import { SubtaskList } from "./SubtaskList";
import { RecurringDialog } from "./RecurringDialog";
import { SaveTemplateDialog } from "./SaveTemplateDialog";
import { useRecurrencePattern, useDeleteRecurrence } from "@/hooks/useRecurring";
import { Repeat, X, FileText } from "lucide-react";

// Form data type
interface EditTaskFormData {
  title: string;
  description?: string;
  due_date: string | null;
  notes?: string;
}

// Zod validation schema
const editTaskSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(100, "Title must be 100 characters or less")
    .trim(),
  description: z
    .string()
    .max(500, "Description must be 500 characters or less")
    .trim()
    .optional(),
  due_date: z.string().nullable(),
  notes: z
    .string()
    .max(500, "Notes must be 500 characters or less")
    .trim()
    .optional(),
});

interface EditTaskDialogProps {
  task: Task;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function EditTaskDialog({
  task,
  open,
  onOpenChange,
}: EditTaskDialogProps) {
  const { mutate: updateTask, isPending: isUpdating } = useUpdateTask();
  const { mutateAsync: assignTags, isPending: isAssigningTags } = useAssignTags();
  const isPending = isUpdating || isAssigningTags;
  const [dueDate, setDueDate] = useState<Date | null>(
    task.due_date ? parseISO(task.due_date) : null
  );
  const [selectedTagIds, setSelectedTagIds] = useState<string[]>(
    task.tags?.map((tag) => tag.id) || []
  );
  const [initialTagIds, setInitialTagIds] = useState<string[]>(
    task.tags?.map((tag) => tag.id) || []
  );
  const [recurringDialogOpen, setRecurringDialogOpen] = useState(false);
  const [saveTemplateDialogOpen, setSaveTemplateDialogOpen] = useState(false);

  const { data: recurrencePattern } = useRecurrencePattern(task.recurrence_pattern_id ? task.id : undefined);
  const { mutate: deleteRecurrence } = useDeleteRecurrence();

  const form = useForm<EditTaskFormData>({
    resolver: zodResolver(editTaskSchema),
    defaultValues: {
      title: task.title,
      description: task.description || "",
      due_date: task.due_date || null,
      notes: task.notes || "",
    },
  });

  // Reset form and due date when task changes
  useEffect(() => {
    form.reset({
      title: task.title,
      description: task.description || "",
      due_date: task.due_date || null,
      notes: task.notes || "",
    });
    setDueDate(task.due_date ? parseISO(task.due_date) : null);
    const tagIds = task.tags?.map((tag) => tag.id) || [];
    setSelectedTagIds(tagIds);
    setInitialTagIds(tagIds);
  }, [task, form]);

  const onSubmit = async (data: EditTaskFormData) => {
    // Check if tags changed
    const tagsChanged =
      JSON.stringify([...selectedTagIds].sort()) !==
      JSON.stringify([...initialTagIds].sort());

    // Check if anything actually changed
    const hasFormChanges =
      data.title !== task.title ||
      (data.description || "") !== (task.description || "") ||
      (data.due_date || null) !== (task.due_date || null) ||
      (data.notes || "") !== (task.notes || "");

    if (!hasFormChanges && !tagsChanged) {
      form.setError("root", {
        message: "No changes detected. Please modify at least one field.",
      });
      return;
    }

    // Submit task update if form data changed
    if (hasFormChanges) {
      updateTask(
        {
          taskId: task.id,
          data: {
            title: data.title !== task.title ? data.title : undefined,
            description:
              data.description !== task.description
                ? data.description
                : undefined,
            due_date:
              (data.due_date || null) !== (task.due_date || null)
                ? data.due_date
                : undefined,
            notes:
              (data.notes || "") !== (task.notes || "")
                ? data.notes
                : undefined,
          },
        },
        {
          onSuccess: async () => {
            // Update tags if changed
            if (tagsChanged) {
              try {
                await assignTags({
                  taskId: task.id,
                  tagIds: selectedTagIds,
                });
              } catch {
                // Silently handle tag assignment errors
              }
            }
            onOpenChange(false);
            form.reset();
            setDueDate(null);
            setSelectedTagIds([]);
          },
        }
      );
    } else if (tagsChanged) {
      // Only tags changed, update them directly
      try {
        await assignTags({
          taskId: task.id,
          tagIds: selectedTagIds,
        });
        onOpenChange(false);
        form.reset();
        setDueDate(null);
        setSelectedTagIds([]);
      } catch {
        form.setError("root", {
          message: "Failed to update tags. Please try again.",
        });
      }
    }
  };

  const handleCancel = () => {
    form.reset();
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>Edit Task</DialogTitle>
          <DialogDescription>
            Update the task title or description. Click save when you&apos;re done.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            {/* Title Field */}
            <FormField<EditTaskFormData>
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Title</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Enter task title"
                      {...field}
                      value={field.value ?? ""}
                      disabled={isPending}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Description Field */}
            <FormField<EditTaskFormData>
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description (Optional)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Enter task description"
                      className="min-h-[100px] resize-none"
                      {...field}
                      value={field.value ?? ""}
                      disabled={isPending}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Due Date Field */}
            <div className="space-y-2">
              <Label htmlFor="due_date">Due Date (Optional)</Label>
              <DueDatePicker
                value={dueDate}
                onChange={(date) => {
                  setDueDate(date);
                  form.setValue(
                    "due_date",
                    date ? format(date, "yyyy-MM-dd") : null
                  );
                }}
              />
            </div>

            {/* Tags Field */}
            <div className="space-y-2">
              <Label>Tags (Optional)</Label>
              <TagPicker
                selectedTagIds={selectedTagIds}
                onTagsChange={setSelectedTagIds}
                maxTags={10}
              />
            </div>

            {/* Subtasks Field */}
            <div className="space-y-2">
              <Label>Subtasks (Optional)</Label>
              <SubtaskList
                taskId={task.id}
                subtasks={task.subtasks || []}
              />
            </div>

            {/* Recurring Section */}
            <div className="space-y-2">
              <Label>Recurring (Optional)</Label>
              {recurrencePattern ? (
                <div className="flex items-center justify-between p-3 border rounded-md bg-muted/50">
                  <div className="flex items-center gap-2">
                    <Repeat className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">
                      Repeats {recurrencePattern.frequency}
                      {recurrencePattern.interval > 1 && ` (every ${recurrencePattern.interval})`}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => setRecurringDialogOpen(true)}
                    >
                      Edit
                    </Button>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteRecurrence(task.id)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ) : (
                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  onClick={() => setRecurringDialogOpen(true)}
                >
                  <Repeat className="mr-2 h-4 w-4" />
                  Make Recurring
                </Button>
              )}
            </div>

            {/* Notes Field */}
            <FormField<EditTaskFormData>
              control={form.control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notes (Optional)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Add detailed notes..."
                      className="min-h-[120px] resize-none"
                      {...field}
                      value={field.value ?? ""}
                      disabled={isPending}
                    />
                  </FormControl>
                  <div className="flex justify-between items-center">
                    <FormMessage />
                    <span className="text-xs text-muted-foreground">
                      {(field.value || "").length}/500 characters
                    </span>
                  </div>
                </FormItem>
              )}
            />

            {/* Root Error Message */}
            {form.formState.errors.root && (
              <p className="text-sm font-medium text-destructive">
                {form.formState.errors.root.message}
              </p>
            )}

            {/* Dialog Footer */}
            <DialogFooter className="flex-col sm:flex-row gap-2">
              <Button
                type="button"
                variant="secondary"
                onClick={() => setSaveTemplateDialogOpen(true)}
                disabled={isPending}
                className="sm:mr-auto"
              >
                <FileText className="mr-2 h-4 w-4" />
                Save as Template
              </Button>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleCancel}
                  disabled={isPending}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isPending}>
                  {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Save Changes
                </Button>
              </div>
            </DialogFooter>
          </form>
        </Form>

        {/* Recurring Dialog */}
        <RecurringDialog
          open={recurringDialogOpen}
          onOpenChange={setRecurringDialogOpen}
          taskId={task.id}
          mode={recurrencePattern ? "edit" : "create"}
        />

        {/* Save Template Dialog */}
        <SaveTemplateDialog
          open={saveTemplateDialogOpen}
          onOpenChange={setSaveTemplateDialogOpen}
          taskId={task.id}
          taskTitle={task.title}
        />
      </DialogContent>
    </Dialog>
  );
}
