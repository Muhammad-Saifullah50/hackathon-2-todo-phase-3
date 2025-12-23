"use client";

import { useState } from "react";
import { FileText, Loader2 } from "lucide-react";
import { useTemplates, useApplyTemplate } from "@/hooks/useTemplates";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";

interface TemplateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onTemplateApplied?: () => void;
}

export function TemplateDialog({ open, onOpenChange, onTemplateApplied }: TemplateDialogProps) {
  const { data, isLoading } = useTemplates();
  const applyTemplate = useApplyTemplate();
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);

  const handleApplyTemplate = async (templateId: string) => {
    setSelectedTemplateId(templateId);
    try {
      await applyTemplate.mutateAsync({ templateId });
      onOpenChange(false);
      onTemplateApplied?.();
    } catch (error) {
      console.error("Failed to apply template:", error);
    } finally {
      setSelectedTemplateId(null);
    }
  };

  const priorityColors = {
    low: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
    medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
    high: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Use Template</DialogTitle>
          <DialogDescription>
            Select a template to create a new task with pre-filled information
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="max-h-[400px] pr-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : data?.templates && data.templates.length > 0 ? (
            <div className="space-y-3">
              {data.templates.map((template) => (
                <div
                  key={template.id}
                  className="rounded-lg border p-4 hover:bg-accent transition-colors"
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
                          <Badge variant="outline">
                            {template.subtasks_template.length} subtask
                            {template.subtasks_template.length !== 1 ? "s" : ""}
                          </Badge>
                        )}
                      </div>
                    </div>
                    <Button
                      size="sm"
                      onClick={() => handleApplyTemplate(template.id)}
                      disabled={selectedTemplateId === template.id}
                    >
                      {selectedTemplateId === template.id ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Applying...
                        </>
                      ) : (
                        "Use Template"
                      )}
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <FileText className="h-12 w-12 text-muted-foreground/50 mb-4" />
              <p className="text-sm text-muted-foreground mb-2">No templates yet</p>
              <p className="text-xs text-muted-foreground">
                Save a task as a template to use it here
              </p>
            </div>
          )}
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
