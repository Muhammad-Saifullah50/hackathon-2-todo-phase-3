"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Plus, FileText } from "lucide-react";
import { format } from "date-fns";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useToast } from "@/hooks/use-toast";
import { useCreateTask } from "@/hooks/useTasks";
import { useAssignTags } from "@/hooks/useTags";
import { createTaskSchema, type CreateTaskFormData } from "@/lib/schemas/task";
import { DueDatePicker } from "./DueDatePicker";
import { TagPicker } from "./TagPicker";
import { TemplateDialog } from "./TemplateDialog";

interface CreateTaskDialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  defaultValues?: {
    due_date?: string;
    priority?: "low" | "medium" | "high";
  };
  hideTrigger?: boolean;
}

export function CreateTaskDialog({
  open: controlledOpen,
  onOpenChange,
  defaultValues,
  hideTrigger = false,
  
}: CreateTaskDialogProps = {}) {
  const [internalOpen, setInternalOpen] = useState(false);
  const [dueDate, setDueDate] = useState<Date | null>(
    defaultValues?.due_date ? new Date(defaultValues.due_date) : null
  );
  const [selectedTagIds, setSelectedTagIds] = useState<string[]>([]);
  const [templateDialogOpen, setTemplateDialogOpen] = useState(false);
  const { toast } = useToast();
  const { mutate: createTask, isPending } = useCreateTask();
  const { mutateAsync: assignTags } = useAssignTags();

  // Use controlled open state if provided, otherwise use internal state
  const open = controlledOpen !== undefined ? controlledOpen : internalOpen;
  const setOpen = onOpenChange || setInternalOpen;

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    watch,
    setValue,
  } = useForm<CreateTaskFormData>({
    resolver: zodResolver(createTaskSchema),
    mode: "onChange", // Real-time validation
    defaultValues: {
      title: "",
      description: "",
      priority: defaultValues?.priority || "medium",
      due_date: defaultValues?.due_date ?? null,
    },
  });

  // Update due date and form when defaultValues change
  useEffect(() => {
    if (defaultValues?.due_date) {
      const date = new Date(defaultValues.due_date);
      setDueDate(date);
      setValue("due_date", defaultValues.due_date);
    }
    if (defaultValues?.priority) {
      setValue("priority", defaultValues.priority);
    }
  }, [defaultValues, setValue]);

  // Watch form values to detect changes
  const title = watch("title");
  const description = watch("description");
  const hasChanges = Boolean(title?.trim() || description?.trim() || dueDate || selectedTagIds.length > 0);

  // Listen for custom event from keyboard shortcuts provider
  useEffect(() => {
    const handleOpenDialog = () => {
      setOpen(true);
    };

    window.addEventListener("open-create-task-dialog", handleOpenDialog);
    return () => window.removeEventListener("open-create-task-dialog", handleOpenDialog);
  }, [setOpen]);

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen && hasChanges) {
      if (!window.confirm("Discard unsaved changes?")) {
        return;
      }
      reset();
      setDueDate(null);
      setSelectedTagIds([]);
    }
    setOpen(newOpen);
  };

  const onSubmit = (data: CreateTaskFormData) => {
    createTask(
      {
        title: data.title,
        description: data.description,
        priority: data.priority,
        due_date: data.due_date,
      },
      {
        onSuccess: async (response: { data?: { id: string } }) => {
          // Assign tags if any were selected
          if (selectedTagIds.length > 0 && response?.data?.id) {
            try {
              await assignTags({
                taskId: response.data.id,
                tagIds: selectedTagIds,
              });
            } catch {
              // Tags assignment failed but task was created
              toast({
                title: "Partial success",
                description: "Task created but some tags could not be assigned",
                variant: "default",
              });
            }
          }

          toast({
            title: "Success",
            description: "Task created successfully",
          });
          setOpen(false);
          reset();
          setDueDate(null);
          setSelectedTagIds([]);
        },
        onError: (error: Error) => {
          const apiError = error as Error & { response?: { data?: { error?: { message?: string } } } };
          toast({
            title: "Error",
            description:
              apiError?.response?.data?.error?.message ||
              "Failed to create task. Please try again.",
            variant: "destructive",
          });
        },
      }
    );
  };

  const titleLength = title?.length || 0;
  const descriptionLength = description?.length || 0;
  const titleWords = title ? title.trim().split(/\s+/).length : 0;

  return (
    <>
      {!hideTrigger && (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button onClick={() => setOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add Task
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>Create new task (N)</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      )}

      <Dialog open={open} onOpenChange={handleOpenChange}>
        <DialogContent className="sm:max-w-[500px] max-sm:h-full max-sm:w-full max-sm:max-w-full">
          <DialogHeader>
            <DialogTitle>Create New Task</DialogTitle>
            <DialogDescription>
              Fill in the details to create a new task
            </DialogDescription>
          </DialogHeader>

          <div className="mb-4">
            <Button
              type="button"
              variant="outline"
              className="w-full"
              onClick={() => setTemplateDialogOpen(true)}
            >
              <FileText className="mr-2 h-4 w-4" />
              Use Template
            </Button>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Title field */}
            <div>
              <Label htmlFor="title">
                Title <span className="text-destructive">*</span>
              </Label>
              <Input
                id="title"
                {...register("title")}
                placeholder="Enter task title..."
                maxLength={100}
                aria-invalid={errors.title ? "true" : "false"}
                aria-describedby={errors.title ? "title-error" : undefined}
              />
              <div className="flex justify-between items-center mt-1">
                <div>
                  {errors.title && (
                    <p id="title-error" className="text-sm text-destructive">
                      {errors.title.message}
                    </p>
                  )}
                </div>
                <p
                  className={`text-xs ${
                    titleLength > 90 || titleWords > 45
                      ? "text-orange-500"
                      : "text-muted-foreground"
                  }`}
                >
                  {titleLength}/100 chars · {titleWords}/50 words
                </p>
              </div>
            </div>

            {/* Description field */}
            <div>
              <Label htmlFor="description">Description (optional)</Label>
              <Textarea
                id="description"
                {...register("description")}
                placeholder="Add details (optional)..."
                maxLength={500}
                rows={4}
                aria-invalid={errors.description ? "true" : "false"}
                aria-describedby={
                  errors.description ? "description-error" : undefined
                }
              />
              <div className="flex justify-between items-center mt-1">
                <div>
                  {errors.description && (
                    <p
                      id="description-error"
                      className="text-sm text-destructive"
                    >
                      {errors.description.message}
                    </p>
                  )}
                </div>
                <p
                  className={`text-xs ${
                    descriptionLength > 450
                      ? "text-orange-500"
                      : "text-muted-foreground"
                  }`}
                >
                  {descriptionLength}/500 chars
                </p>
              </div>
            </div>

            {/* Priority field */}
            <div>
              <Label htmlFor="priority">Priority</Label>
              <Select
                onValueChange={(value) =>
                  setValue("priority", value as "low" | "medium" | "high")
                }
                defaultValue="medium"
              >
                <SelectTrigger id="priority">
                  <SelectValue placeholder="Select priority (default: Medium)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Due Date field */}
            <div>
              <Label htmlFor="due_date">Due Date (optional)</Label>
              <DueDatePicker
                value={dueDate}
                onChange={(date) => {
                  setDueDate(date);
                  setValue("due_date", date ? format(date, "yyyy-MM-dd") : null);
                }}
              />
            </div>

            {/* Tags field */}
            <div>
              <Label>Tags (optional)</Label>
              <TagPicker
                selectedTagIds={selectedTagIds}
                onTagsChange={setSelectedTagIds}
                maxTags={10}
              />
            </div>

            {/* Form actions */}
            <div className="flex justify-end gap-2 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => handleOpenChange(false)}
                disabled={isPending}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isPending || isSubmitting || Object.keys(errors).length > 0}
              >
                {isPending ? "Creating..." : "Create Task"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      <TemplateDialog
        open={templateDialogOpen}
        onOpenChange={setTemplateDialogOpen}
        onTemplateApplied={() => {
          setOpen(false);
        }}
      />
    </>
  );
}
