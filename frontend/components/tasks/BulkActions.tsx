"use client";

/**
 * BulkActions Component - Toolbar for bulk operations on selected tasks.
 * Client Component because it needs onClick handlers.
 */

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Circle, X, Trash2 } from "lucide-react";
import { DeleteConfirmDialog } from "./DeleteConfirmDialog";

interface BulkActionsProps {
  selectedCount: number;
  onMarkAsCompleted: () => void;
  onMarkAsPending: () => void;
  onBulkDelete: () => void;
  onClearSelection: () => void;
}

export function BulkActions({
  selectedCount,
  onMarkAsCompleted,
  onMarkAsPending,
  onBulkDelete,
  onClearSelection,
}: BulkActionsProps) {
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  if (selectedCount === 0) {
    return null;
  }

  const handleBulkDelete = () => {
    onBulkDelete();
    setIsDeleteDialogOpen(false);
  };

  return (
    <>
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 animate-in slide-in-from-bottom-5">
        <div className="bg-background border rounded-lg shadow-lg p-4 flex items-center gap-4">
          <span className="text-sm font-medium">
            {selectedCount} task{selectedCount === 1 ? '' : 's'} selected
          </span>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={onMarkAsCompleted}
              className="gap-2"
            >
              <CheckCircle2 className="h-4 w-4" />
              Mark as Completed
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={onMarkAsPending}
              className="gap-2"
            >
              <Circle className="h-4 w-4" />
              Mark as Pending
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsDeleteDialogOpen(true)}
              className="gap-2 text-destructive hover:text-destructive"
            >
              <Trash2 className="h-4 w-4" />
              Delete
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={onClearSelection}
              className="gap-2"
            >
              <X className="h-4 w-4" />
              Clear
            </Button>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmDialog
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
        onConfirm={handleBulkDelete}
        bulkCount={selectedCount}
        isPermanent={false}
      />
    </>
  );
}
