"use client";

/**
 * DeleteConfirmDialog Component - Confirmation dialog for task deletion.
 * Supports both soft delete (move to trash) and permanent delete modes.
 */

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

interface DeleteConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  isPermanent?: boolean;
  taskTitle?: string;
  bulkCount?: number;
}

export function DeleteConfirmDialog({
  open,
  onOpenChange,
  onConfirm,
  isPermanent = false,
  taskTitle,
  bulkCount,
}: DeleteConfirmDialogProps) {
  const isBulk = bulkCount !== undefined && bulkCount > 0;

  const getTitle = () => {
    if (isPermanent) {
      return isBulk
        ? `Permanently Delete ${bulkCount} Tasks?`
        : "Permanently Delete Task?";
    }
    return isBulk ? `Delete ${bulkCount} Tasks?` : "Delete Task?";
  };

  const getDescription = () => {
    if (isPermanent) {
      return isBulk
        ? `This will permanently delete ${bulkCount} tasks from the database. This action cannot be undone and the tasks will be lost forever.`
        : `This will permanently delete "${taskTitle}" from the database. This action cannot be undone and the task will be lost forever.`;
    }
    return isBulk
      ? `This will move ${bulkCount} tasks to trash. You can restore them later from the trash view.`
      : `This will move "${taskTitle}" to trash. You can restore it later from the trash view.`;
  };

  const getActionText = () => {
    return isPermanent ? "Delete Permanently" : "Move to Trash";
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{getTitle()}</AlertDialogTitle>
          <AlertDialogDescription className="space-y-2">
            <p>{getDescription()}</p>
            {isPermanent && (
              <p className="font-semibold text-destructive">
                ⚠️ Warning: This action is irreversible!
              </p>
            )}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirm}
            className={
              isPermanent
                ? "bg-destructive hover:bg-destructive/90"
                : undefined
            }
          >
            {getActionText()}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
