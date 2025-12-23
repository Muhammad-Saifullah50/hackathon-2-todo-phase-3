/**
 * TaskListSkeleton Component - Loading skeleton for task list.
 * Shows placeholder content while tasks are loading.
 */

import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";

interface TaskListSkeletonProps {
  count?: number;
  variant?: "list" | "grid";
}

export function TaskListSkeleton({ count = 5, variant = "list" }: TaskListSkeletonProps) {
  return (
    <div className="space-y-6">
      {/* Filters skeleton */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex gap-2">
          <Skeleton className="h-10 w-32" />
          <Skeleton className="h-10 w-32" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="flex gap-1">
          <Skeleton className="h-10 w-10" />
          <Skeleton className="h-10 w-10" />
        </div>
      </div>

      {/* Metadata badges skeleton */}
      <div className="flex gap-4">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-6 w-32" />
      </div>

      {/* Task cards skeleton */}
      <div
        className={
          variant === "grid"
            ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
            : "space-y-3"
        }
      >
        {Array.from({ length: count }).map((_, i) => (
          <TaskCardSkeleton key={i} />
        ))}
      </div>

      {/* Pagination skeleton */}
      <div className="flex items-center justify-between">
        <Skeleton className="h-10 w-32" />
        <div className="flex gap-2">
          <Skeleton className="h-10 w-10" />
          <Skeleton className="h-10 w-10" />
          <Skeleton className="h-10 w-10" />
        </div>
        <Skeleton className="h-10 w-32" />
      </div>
    </div>
  );
}

function TaskCardSkeleton() {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          {/* Checkbox skeleton */}
          <Skeleton className="h-5 w-5 rounded-sm mt-0.5" />

          <div className="flex-1 space-y-2">
            {/* Title and badges */}
            <div className="flex items-start justify-between gap-2">
              <Skeleton className="h-5 w-3/4" />
              <div className="flex gap-1">
                <Skeleton className="h-6 w-16 rounded-full" />
                <Skeleton className="h-6 w-6 rounded-sm" />
                <Skeleton className="h-6 w-6 rounded-sm" />
              </div>
            </div>

            {/* Description */}
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-2/3" />

            {/* Timestamps */}
            <div className="flex gap-3 pt-1">
              <Skeleton className="h-3 w-24" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
