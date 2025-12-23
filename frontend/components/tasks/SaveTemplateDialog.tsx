"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { useSaveTaskAsTemplate } from "@/hooks/useTemplates";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";

interface SaveTemplateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  taskId: string;
  taskTitle: string;
}

export function SaveTemplateDialog({
  open,
  onOpenChange,
  taskId,
  taskTitle,
}: SaveTemplateDialogProps) {
  const [templateName, setTemplateName] = useState(taskTitle);
  const [includeSubtasks, setIncludeSubtasks] = useState(true);
  const [includeTags, setIncludeTags] = useState(true);
  const saveTemplate = useSaveTaskAsTemplate();

  const handleSave = async () => {
    if (!templateName.trim()) return;

    try {
      await saveTemplate.mutateAsync({
        task_id: taskId,
        template_name: templateName.trim(),
        include_subtasks: includeSubtasks,
        include_tags: includeTags,
      });
      onOpenChange(false);
      setTemplateName("");
      setIncludeSubtasks(true);
      setIncludeTags(true);
    } catch (error) {
      console.error("Failed to save template:", error);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Save as Template</DialogTitle>
          <DialogDescription>
            Save this task structure as a reusable template
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="template-name">Template Name</Label>
            <Input
              id="template-name"
              placeholder="Enter template name"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && templateName.trim()) {
                  handleSave();
                }
              }}
            />
          </div>

          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="include-subtasks"
                checked={includeSubtasks}
                onCheckedChange={(checked) => setIncludeSubtasks(checked as boolean)}
              />
              <label
                htmlFor="include-subtasks"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Include subtasks
              </label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="include-tags"
                checked={includeTags}
                onCheckedChange={(checked) => setIncludeTags(checked as boolean)}
              />
              <label
                htmlFor="include-tags"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Include tags
              </label>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={!templateName.trim() || saveTemplate.isPending}
          >
            {saveTemplate.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              "Save Template"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
