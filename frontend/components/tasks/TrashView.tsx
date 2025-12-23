"use client";

/**
 * TrashView Component - Displays deleted tasks with restore/permanent delete options.
 * Client Component because it manages state and uses React Query.
 */

import { useState } from "react";
import { useTrash } from "@/hooks/useTasks";
import { TaskCard } from "./TaskCard";
import { Pagination } from "./Pagination";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import Image from "next/image";
import { Checkbox } from "@/components/ui/checkbox";
import { DeleteConfirmDialog } from "./DeleteConfirmDialog";

export function TrashView() {
  // Pagination state
  const [page, setPage] = useState(1);

  // Bulk selection state
  const [selectedTaskIds, setSelectedTaskIds] = useState<Set<string>>(new Set());
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  // Fetch trash with React Query
  const { data, isLoading, isError, error } = useTrash({
    page,
    limit: 20,
  });

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  // Error state
  if (isError) {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          Failed to load trash: {error instanceof Error ? error.message : "Unknown error"}
        </AlertDescription>
      </Alert>
    );
  }

  const tasks = data?.data?.tasks || [];
  const pagination = data?.data?.pagination;

  // Bulk selection handlers
  const toggleTaskSelection = (taskId: string) => {
    setSelectedTaskIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(taskId)) {
        newSet.delete(taskId);
      } else {
        newSet.add(taskId);
      }
      return newSet;
    });
  };

  const toggleSelectAll = () => {
    if (selectedTaskIds.size === tasks.length) {
      setSelectedTaskIds(new Set());
    } else {
      setSelectedTaskIds(new Set(tasks.map((t) => t.id)));
    }
  };

  const clearSelection = () => {
    setSelectedTaskIds(new Set());
  };

  const allSelected = tasks.length > 0 && selectedTaskIds.size === tasks.length;

  // Empty state
  if (tasks.length === 0) {
    return (
      <EmptyState
        illustration={
          <Image
            src="/illustrations/empty-trash.svg"
            alt="Trash is empty"
            width={100}
            height={100}
            className="opacity-60"
          />
        }
        heading="Trash is empty"
        description="Deleted tasks will appear here. You can restore them or delete them permanently."
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Task Count and Select All */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          {tasks.length} task{tasks.length === 1 ? '' : 's'} in trash
        </div>

        {/* Select All Checkbox */}
        {tasks.length > 0 && (
          <div className="flex items-center gap-2">
            <Checkbox
              id="select-all-trash"
              checked={allSelected}
              onCheckedChange={toggleSelectAll}
            />
            <label
              htmlFor="select-all-trash"
              className="text-sm font-medium cursor-pointer"
            >
              Select All
            </label>
          </div>
        )}
      </div>

      {/* Info Alert */}
      <Alert>
        <AlertDescription>
          Tasks in trash can be restored or permanently deleted. Permanent deletion cannot be undone.
        </AlertDescription>
      </Alert>

      {/* Task List */}
      <div className="space-y-3">
        {tasks.map((task) => (
          <div key={task.id} className="flex items-start gap-2">
            {/* Bulk Selection Checkbox */}
            <Checkbox
              checked={selectedTaskIds.has(task.id)}
              onCheckedChange={() => toggleTaskSelection(task.id)}
              className="mt-4"
              aria-label={`Select ${task.title}`}
            />
            <div className="flex-1">
              <TaskCard task={task} variant="list" isTrashView={true} />
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {pagination && pagination.total_pages > 1 && (
        <Pagination pagination={pagination} onPageChange={setPage} />
      )}

      {/* Bulk Actions Toolbar */}
      {selectedTaskIds.size > 0 && (
        <>
          <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 animate-in slide-in-from-bottom-5">
            <div className="bg-background border rounded-lg shadow-lg p-4 flex items-center gap-4">
              <span className="text-sm font-medium">
                {selectedTaskIds.size} task{selectedTaskIds.size === 1 ? '' : 's'} selected
              </span>

              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsDeleteDialogOpen(true)}
                  className="gap-2 text-destructive hover:text-destructive"
                >
                  <Trash2 className="h-4 w-4" />
                  Delete Permanently
                </Button>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearSelection}
                  className="gap-2"
                >
                  Clear
                </Button>
              </div>
            </div>
          </div>

          {/* Permanent Delete Confirmation Dialog */}
          <DeleteConfirmDialog
            open={isDeleteDialogOpen}
            onOpenChange={setIsDeleteDialogOpen}
            onConfirm={() => {
              // TODO: Implement bulk permanent delete
              setIsDeleteDialogOpen(false);
              clearSelection();
            }}
            bulkCount={selectedTaskIds.size}
            isPermanent={true}
          />
        </>
      )}
    </div>
  );
}
