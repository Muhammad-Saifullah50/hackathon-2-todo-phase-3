"use client";

/**
 * TaskFilters Component - Filter and sort controls for tasks.
 * Client Component because it needs state and onChange handlers.
 */

import { TaskStatus } from "@/lib/types/task";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Filter, ArrowUpDown } from "lucide-react";

interface TaskFiltersProps {
  status: TaskStatus | "all";
  sortBy: string;
  sortOrder: "asc" | "desc";
  onStatusChange: (status: TaskStatus | "all") => void;
  onSortByChange: (sortBy: string) => void;
  onSortOrderChange: (sortOrder: "asc" | "desc") => void;
}

export function TaskFilters({
  status,
  sortBy,
  sortOrder,
  onStatusChange,
  onSortByChange,
  onSortOrderChange,
}: TaskFiltersProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-end">
      {/* Status Filter */}
      <div className="flex-1 w-full sm:w-auto space-y-2">
        <Label htmlFor="status-filter" className="flex items-center gap-2 text-sm">
          <Filter className="h-4 w-4" />
          Status
        </Label>
        <Select
          value={status}
          onValueChange={(value) =>
            onStatusChange(value as TaskStatus | "all")
          }
        >
          <SelectTrigger id="status-filter" className="w-full sm:w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Tasks</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Sort By */}
      <div className="flex-1 w-full sm:w-auto space-y-2">
        <Label htmlFor="sort-by" className="flex items-center gap-2 text-sm">
          <ArrowUpDown className="h-4 w-4" />
          Sort By
        </Label>
        <Select value={sortBy} onValueChange={onSortByChange}>
          <SelectTrigger id="sort-by" className="w-full sm:w-[180px]">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="created_at">Date Created</SelectItem>
            <SelectItem value="title">Title</SelectItem>
            <SelectItem value="status">Status</SelectItem>
            <SelectItem value="priority">Priority</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Sort Order */}
      <div className="flex-1 w-full sm:w-auto space-y-2">
        <Label htmlFor="sort-order" className="text-sm">
          Order
        </Label>
        <Select value={sortOrder} onValueChange={(value) => onSortOrderChange(value as "asc" | "desc")}>
          <SelectTrigger id="sort-order" className="w-full sm:w-[140px]">
            <SelectValue placeholder="Order" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="desc">Newest First</SelectItem>
            <SelectItem value="asc">Oldest First</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
