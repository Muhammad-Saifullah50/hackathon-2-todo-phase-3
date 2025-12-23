"use client";

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

interface RecurringConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (action: "this" | "all") => void;
  type: "delete" | "edit";
  taskTitle: string;
}

export function RecurringConfirmDialog({
  open,
  onOpenChange,
  onConfirm,
  type,
  taskTitle,
}: RecurringConfirmDialogProps) {
  const isDelete = type === "delete";

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>
            {isDelete ? "Delete Recurring Task" : "Edit Recurring Task"}
          </AlertDialogTitle>
          <AlertDialogDescription className="space-y-3">
            <p>
              {isDelete
                ? `"${taskTitle}" is a recurring task.`
                : `You're editing a recurring task: "${taskTitle}"`}
            </p>
            <p className="font-medium text-foreground">
              {isDelete
                ? "What would you like to delete?"
                : "What would you like to update?"}
            </p>
          </AlertDialogDescription>
        </AlertDialogHeader>

        <AlertDialogFooter className="flex-col sm:flex-col gap-2">
          <AlertDialogAction
            onClick={() => {
              onConfirm("this");
              onOpenChange(false);
            }}
            className="w-full"
          >
            {isDelete
              ? "Delete only this instance"
              : "Update only this instance"}
          </AlertDialogAction>

          <AlertDialogAction
            onClick={() => {
              onConfirm("all");
              onOpenChange(false);
            }}
            className={`w-full ${isDelete ? "bg-destructive text-destructive-foreground hover:bg-destructive/90" : ""}`}
          >
            {isDelete
              ? "Stop all recurrences (delete pattern)"
              : "Update all future instances"}
          </AlertDialogAction>

          <AlertDialogCancel className="w-full mt-2">Cancel</AlertDialogCancel>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
