"use client";

import { useState } from "react";
import { Edit2, Plus, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { useTags, useCreateTag, useUpdateTag, useDeleteTag } from "@/hooks/useTags";
import type { TagWithCount } from "@/lib/types/tag";
import { TAG_COLORS } from "@/lib/types/tag";
import { TagBadge } from "./TagBadge";

interface TagManagementProps {
  trigger?: React.ReactNode;
  className?: string;
}

/**
 * A dialog for managing tags: view, create, edit, and delete tags.
 */
export function TagManagement({ trigger, className }: TagManagementProps) {
  const [open, setOpen] = useState(false);
  const [editingTag, setEditingTag] = useState<TagWithCount | null>(null);
  const [deleteTag, setDeleteTag] = useState<TagWithCount | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

  // Form state
  const [name, setName] = useState("");
  const [color, setColor] = useState<string>(TAG_COLORS[0]);

  const { data: tagsData, isLoading } = useTags();
  const createTag = useCreateTag();
  const updateTag = useUpdateTag();
  const deleteTagMutation = useDeleteTag();

  const tags = tagsData?.data?.tags || [];

  const resetForm = () => {
    setName("");
    setColor(TAG_COLORS[0]);
    setEditingTag(null);
    setShowCreateForm(false);
  };

  const handleStartEdit = (tag: TagWithCount) => {
    setEditingTag(tag);
    setName(tag.name);
    setColor(tag.color);
    setShowCreateForm(false);
  };

  const handleStartCreate = () => {
    resetForm();
    setShowCreateForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    try {
      if (editingTag) {
        await updateTag.mutateAsync({
          tagId: editingTag.id,
          data: { name: name.trim(), color },
        });
      } else {
        await createTag.mutateAsync({
          name: name.trim(),
          color,
        });
      }
      resetForm();
    } catch {
      // Error handled by mutation
    }
  };

  const handleDelete = async () => {
    if (!deleteTag) return;

    try {
      await deleteTagMutation.mutateAsync(deleteTag.id);
      setDeleteTag(null);
    } catch {
      // Error handled by mutation
    }
  };

  const isFormDirty = editingTag
    ? name.trim() !== editingTag.name || color !== editingTag.color
    : name.trim().length > 0;

  const isPending = createTag.isPending || updateTag.isPending;

  return (
    <>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          {trigger || (
            <Button variant="outline" size="sm" className={className}>
              Manage Tags
            </Button>
          )}
        </DialogTrigger>
        <DialogContent className="sm:max-w-[480px]">
          <DialogHeader>
            <DialogTitle>Manage Tags</DialogTitle>
            <DialogDescription>
              Create, edit, and organize your tags to categorize tasks.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Tag List */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label className="text-sm font-medium">Your Tags</Label>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleStartCreate}
                  disabled={showCreateForm || !!editingTag}
                >
                  <Plus className="h-4 w-4 mr-1" />
                  New Tag
                </Button>
              </div>

              {isLoading ? (
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-10 w-full" />
                  ))}
                </div>
              ) : tags.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No tags yet. Create your first tag to get started.
                </p>
              ) : (
                <div className="max-h-[200px] overflow-y-auto space-y-1">
                  {tags.map((tag) => (
                    <div
                      key={tag.id}
                      className={cn(
                        "flex items-center justify-between p-2 rounded-md hover:bg-muted/50 transition-colors",
                        editingTag?.id === tag.id && "bg-muted"
                      )}
                    >
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <TagBadge tag={tag} size="md" showCount />
                      </div>
                      <div className="flex items-center gap-1 shrink-0">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => handleStartEdit(tag)}
                          disabled={!!editingTag || showCreateForm}
                          aria-label={`Edit ${tag.name}`}
                        >
                          <Edit2 className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-destructive hover:text-destructive"
                          onClick={() => setDeleteTag(tag)}
                          disabled={!!editingTag || showCreateForm}
                          aria-label={`Delete ${tag.name}`}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Create/Edit Form */}
            {(showCreateForm || editingTag) && (
              <form onSubmit={handleSubmit} className="space-y-4 border-t pt-4">
                <div className="flex items-center justify-between">
                  <Label className="text-sm font-medium">
                    {editingTag ? "Edit Tag" : "New Tag"}
                  </Label>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={resetForm}
                  >
                    Cancel
                  </Button>
                </div>

                <div className="space-y-3">
                  <div className="space-y-1.5">
                    <Label htmlFor="tag-name">Name</Label>
                    <Input
                      id="tag-name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Enter tag name"
                      maxLength={50}
                      autoFocus
                    />
                  </div>

                  <div className="space-y-1.5">
                    <Label>Color</Label>
                    <div className="grid grid-cols-8 gap-1.5">
                      {TAG_COLORS.map((c) => (
                        <button
                          key={c}
                          type="button"
                          onClick={() => setColor(c)}
                          className={cn(
                            "h-7 w-7 rounded-full border-2 transition-transform hover:scale-110",
                            color === c
                              ? "border-foreground scale-110"
                              : "border-transparent"
                          )}
                          style={{ backgroundColor: c }}
                          aria-label={`Select color ${c}`}
                          aria-pressed={color === c}
                        />
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">
                      Preview:
                    </span>
                    <TagBadge
                      tag={{
                        id: "preview",
                        name: name || "Tag name",
                        color,
                        created_at: "",
                        updated_at: "",
                      }}
                      size="md"
                    />
                  </div>
                </div>

                <Button
                  type="submit"
                  className="w-full"
                  disabled={!name.trim() || !isFormDirty || isPending}
                >
                  {isPending
                    ? editingTag
                      ? "Saving..."
                      : "Creating..."
                    : editingTag
                      ? "Save Changes"
                      : "Create Tag"}
                </Button>
              </form>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <AlertDialog open={!!deleteTag} onOpenChange={() => setDeleteTag(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Tag?</AlertDialogTitle>
            <AlertDialogDescription>
              {deleteTag && (
                <>
                  This will permanently delete the tag &quot;
                  <strong>{deleteTag.name}</strong>&quot; and remove it from all
                  {deleteTag.task_count > 0
                    ? ` ${deleteTag.task_count} task${deleteTag.task_count > 1 ? "s" : ""}`
                    : " tasks"}
                  . This action cannot be undone.
                </>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              disabled={deleteTagMutation.isPending}
            >
              {deleteTagMutation.isPending ? "Deleting..." : "Delete Tag"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
