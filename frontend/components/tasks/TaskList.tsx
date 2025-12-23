"use client";

/**
 * TaskList Component - Main list/grid view with filters and pagination.
 * Client Component because it manages filter state and uses React Query.
 * Enhanced with Framer Motion animations for smooth list transitions.
 * Includes global search and quick filters for advanced task discovery.
 * Supports drag-and-drop reordering with @dnd-kit.
 */

import { useState, useCallback, useEffect, useMemo } from "react";
import { motion, AnimatePresence, LayoutGroup } from "framer-motion";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  TouchSensor,
  useSensor,
  useSensors,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { useTasks, useBulkToggle, useBulkDelete, useReorderTasks } from "@/hooks/useTasks";
import { useSearchInput } from "@/hooks/useSearch";
import { useIsMobile } from "@/hooks/useMobile";
import { TaskCard } from "./TaskCard";
import { SortableTaskCard } from "./SortableTaskCard";
import { SwipeableTaskCard } from "@/components/mobile/SwipeableTaskCard";
import { TaskFilters } from "./TaskFilters";
import { Pagination } from "./Pagination";
import { BulkActions } from "./BulkActions";
import { SearchBar } from "./SearchBar";
import { QuickFilters, FilterSummary } from "./QuickFilters";
import { TaskStatus } from "@/lib/types/task";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { LayoutGrid, LayoutList } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import Image from "next/image";
import { Checkbox } from "@/components/ui/checkbox";
import { TaskListSkeleton } from "./TaskListSkeleton";
import { staggerContainer, useReducedMotion } from "@/lib/animations";

export function TaskList() {
  // Filter and pagination state
  const [status, setStatus] = useState<TaskStatus | "all">("all");
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(1);
  const [layout, setLayout] = useState<"list" | "grid">("list");

  // Search state with debouncing
  const { inputValue, debouncedValue, setInputValue, clearSearch, isDebouncing } =
    useSearchInput("", 300);

  // Quick filter state
  const [activeQuickFilter, setActiveQuickFilter] = useState<string | undefined>();

  // Bulk selection state
  const [selectedTaskIds, setSelectedTaskIds] = useState<Set<string>>(new Set());
  const { mutate: bulkToggle } = useBulkToggle();
  const { mutate: bulkDelete } = useBulkDelete();

  // Keyboard navigation state - currently selected task for navigation
  const [selectedTaskIndex, setSelectedTaskIndex] = useState<number>(-1);

  // Check for reduced motion preference
  const prefersReducedMotion = useReducedMotion();

  // Mobile detection for swipeable cards
  const isMobile = useIsMobile();

  // Drag and drop state
  const [activeId, setActiveId] = useState<string | null>(null);
  const { mutate: reorderTasks } = useReorderTasks();

  // Configure drag sensors
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // Minimum distance before drag starts (desktop)
      },
    }),
    useSensor(TouchSensor, {
      activationConstraint: {
        delay: 300, // Long-press delay for mobile (300ms)
        tolerance: 5, // Allow small movement during delay
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Build query params including search
  const queryParams = {
    page,
    limit: 20,
    status: status === "all" ? null : status,
    sort_by: sortBy,
    sort_order: sortOrder,
    search: debouncedValue || undefined,
  };

  // Fetch tasks with React Query
  const { data, isLoading, isError, error } = useTasks(queryParams);

  const tasks = useMemo(() => data?.data?.tasks || [], [data?.data?.tasks]);
  const metadata = data?.data?.metadata;
  const pagination = data?.data?.pagination;

  // Handle quick filter change
  const handleQuickFilterChange = useCallback((filterId: string) => {
    setActiveQuickFilter((prev) => (prev === filterId ? undefined : filterId));
    setPage(1);
  }, []);

  // Clear all filters including search
  const handleClearAllFilters = useCallback(() => {
    clearSearch();
    setStatus("all");
    setActiveQuickFilter(undefined);
    setPage(1);
  }, [clearSearch]);

  // Bulk selection handlers
  const toggleTaskSelection = useCallback((taskId: string) => {
    setSelectedTaskIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(taskId)) {
        newSet.delete(taskId);
      } else {
        newSet.add(taskId);
      }
      return newSet;
    });
  }, []);

  const toggleSelectAll = useCallback(() => {
    if (selectedTaskIds.size === tasks.length) {
      setSelectedTaskIds(new Set());
    } else {
      setSelectedTaskIds(new Set(tasks.map((t) => t.id)));
    }
  }, [selectedTaskIds, tasks]);

  const handleBulkToggle = useCallback((targetStatus: TaskStatus) => {
    bulkToggle(
      { taskIds: Array.from(selectedTaskIds), targetStatus },
      {
        onSuccess: () => {
          setSelectedTaskIds(new Set());
        },
      }
    );
  }, [bulkToggle, selectedTaskIds]);

  const handleBulkDelete = useCallback(() => {
    bulkDelete(Array.from(selectedTaskIds), {
      onSuccess: () => {
        setSelectedTaskIds(new Set());
      },
    });
  }, [bulkDelete, selectedTaskIds]);

  const clearSelection = useCallback(() => {
    setSelectedTaskIds(new Set());
  }, []);

  const allSelected = tasks.length > 0 && selectedTaskIds.size === tasks.length;

  // Count active filters
  const activeFilterCount =
    (debouncedValue ? 1 : 0) +
    (status !== "all" ? 1 : 0) +
    (activeQuickFilter ? 1 : 0);

  // Determine if drag is disabled (when filters/sorting is active)
  const isDragDisabled = useMemo(() => {
    // Disable drag when filters or sorting (other than default) is applied
    return (
      activeFilterCount > 0 ||
      sortBy !== "created_at" ||
      sortOrder !== "desc"
    );
  }, [activeFilterCount, sortBy, sortOrder]);

  // Get task IDs for sortable context
  const taskIds = useMemo(() => tasks.map((t) => t.id), [tasks]);

  // Find the active task for drag overlay
  const activeTask = useMemo(
    () => tasks.find((t) => t.id === activeId),
    [tasks, activeId]
  );

  // Drag handlers
  const handleDragStart = useCallback((event: DragStartEvent) => {
    setActiveId(event.active.id as string);
  }, []);

  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      const { active, over } = event;
      setActiveId(null);

      if (over && active.id !== over.id) {
        // Find indices
        const oldIndex = tasks.findIndex((t) => t.id === active.id);
        const newIndex = tasks.findIndex((t) => t.id === over.id);

        if (oldIndex !== -1 && newIndex !== -1) {
          // Create new ordered array
          const reorderedTasks = [...tasks];
          const [movedTask] = reorderedTasks.splice(oldIndex, 1);
          reorderedTasks.splice(newIndex, 0, movedTask);

          // Send reorder request with new order
          reorderTasks(reorderedTasks.map((t) => t.id));
        }
      }
    },
    [tasks, reorderTasks]
  );

  // Keyboard navigation handlers
  useEffect(() => {
    const handleNavigateUp = () => {
      if (tasks.length === 0) return;
      setSelectedTaskIndex((prev) => {
        const newIndex = prev <= 0 ? tasks.length - 1 : prev - 1;
        // Scroll to selected task
        const element = document.querySelector(`[data-task-index="${newIndex}"]`);
        if (element) {
          element.scrollIntoView({ behavior: "smooth", block: "center" });
        }
        return newIndex;
      });
    };

    const handleNavigateDown = () => {
      if (tasks.length === 0) return;
      setSelectedTaskIndex((prev) => {
        const newIndex = prev >= tasks.length - 1 ? 0 : prev + 1;
        // Scroll to selected task
        const element = document.querySelector(`[data-task-index="${newIndex}"]`);
        if (element) {
          element.scrollIntoView({ behavior: "smooth", block: "center" });
        }
        return newIndex;
      });
    };

    const handleSelectTask = () => {
      if (selectedTaskIndex >= 0 && selectedTaskIndex < tasks.length) {
        const task = tasks[selectedTaskIndex];
        // Dispatch custom event to open edit dialog for selected task
        window.dispatchEvent(
          new CustomEvent("open-edit-task-dialog", { detail: { taskId: task.id } })
        );
      }
    };

    const handleDeleteSelected = () => {
      if (selectedTaskIndex >= 0 && selectedTaskIndex < tasks.length) {
        const task = tasks[selectedTaskIndex];
        toggleTaskSelection(task.id);
        // Auto-trigger bulk delete for single selection
        if (!selectedTaskIds.has(task.id)) {
          setTimeout(() => {
            handleBulkDelete();
          }, 100);
        }
      }
    };

    window.addEventListener("navigate-task-up", handleNavigateUp);
    window.addEventListener("navigate-task-down", handleNavigateDown);
    window.addEventListener("select-task", handleSelectTask);
    window.addEventListener("delete-selected-task", handleDeleteSelected);

    return () => {
      window.removeEventListener("navigate-task-up", handleNavigateUp);
      window.removeEventListener("navigate-task-down", handleNavigateDown);
      window.removeEventListener("select-task", handleSelectTask);
      window.removeEventListener("delete-selected-task", handleDeleteSelected);
    };
  }, [tasks, selectedTaskIndex, selectedTaskIds, toggleTaskSelection, handleBulkDelete]);

  // Determine if showing filtered/search results with no matches
  const hasSearchOrFilter = activeFilterCount > 0;

  // Loading state
  if (isLoading) {
    return <TaskListSkeleton count={5} variant={layout} />;
  }

  // Error state
  if (isError) {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          Failed to load tasks: {error instanceof Error ? error.message : "Unknown error"}
        </AlertDescription>
      </Alert>
    );
  }

  // Empty state
  if (tasks.length === 0) {
    return (
      <div className="space-y-6">
        {/* Search Bar */}
        <div className="space-y-4">
          <SearchBar
            value={inputValue}
            onChange={setInputValue}
            onClear={clearSearch}
            isSearching={isDebouncing}
            placeholder="Search tasks by title, description, or notes..."
          />

          {/* Quick Filters */}
          <div className="flex flex-wrap items-center gap-4">
            <QuickFilters
              activeFilter={activeQuickFilter}
              onFilterChange={handleQuickFilterChange}
            />

            <FilterSummary
              activeFilterCount={activeFilterCount}
              onClearAll={handleClearAllFilters}
            />
          </div>
        </div>

        <div className="flex items-center justify-between">
          <TaskFilters
            status={status}
            sortBy={sortBy}
            sortOrder={sortOrder}
            onStatusChange={(value) => {
              setStatus(value);
              setPage(1);
            }}
            onSortByChange={(value) => {
              setSortBy(value);
              setPage(1);
            }}
            onSortOrderChange={(value) => {
              setSortOrder(value);
              setPage(1);
            }}
          />

          {/* Layout Toggle */}
          <div className="flex gap-1">
            <Button
              variant={layout === "list" ? "default" : "outline"}
              size="icon"
              onClick={() => setLayout("list")}
            >
              <LayoutList className="h-4 w-4" />
            </Button>
            <Button
              variant={layout === "grid" ? "default" : "outline"}
              size="icon"
              onClick={() => setLayout("grid")}
            >
              <LayoutGrid className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Enhanced Empty State */}
        {hasSearchOrFilter ? (
          // No results from search/filter
          <EmptyState
            illustration={
              <Image
                src="/illustrations/no-results.svg"
                alt="No results found"
                width={100}
                height={100}
                className="opacity-60"
              />
            }
            heading="No tasks match your filters"
            description={
              debouncedValue
                ? `No results found for "${debouncedValue}"`
                : "Try adjusting your filters to find what you're looking for."
            }
            action={{
              label: "Clear all filters",
              onClick: handleClearAllFilters,
              variant: "outline",
            }}
          />
        ) : (
          // No tasks at all
          <EmptyState
            illustration={
              <Image
                src="/illustrations/no-tasks.svg"
                alt="No tasks yet"
                width={100}
                height={100}
                className="opacity-60"
              />
            }
            heading="No tasks yet"
            description="Create your first task to get started!"
          />
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Screen reader announcements */}
      <div className="sr-only" aria-live="polite" aria-atomic="true">
        {metadata && `${metadata.total_pending} pending tasks, ${metadata.total_completed} completed tasks`}
        {debouncedValue && `, searching for "${debouncedValue}"`}
      </div>

      {/* Search Bar */}
      <div className="space-y-4">
        <div data-tour="search-bar">
          <SearchBar
            value={inputValue}
            onChange={setInputValue}
            onClear={clearSearch}
            isSearching={isDebouncing}
            placeholder="Search tasks by title, description, or notes..."
          />
        </div>

        {/* Quick Filters */}
        <div className="flex flex-wrap items-center gap-4">
          <div data-tour="quick-filters">
            <QuickFilters
              activeFilter={activeQuickFilter}
              onFilterChange={handleQuickFilterChange}
            />
          </div>

          <FilterSummary
            activeFilterCount={activeFilterCount}
            onClearAll={handleClearAllFilters}
          />
        </div>
      </div>

      {/* Filters and Layout Toggle */}
      <div className="flex items-center justify-between gap-4">
        <div data-tour="task-filters">
          <TaskFilters
            status={status}
            sortBy={sortBy}
            sortOrder={sortOrder}
            onStatusChange={(value) => {
              setStatus(value);
              setPage(1);
            }}
            onSortByChange={(value) => {
              setSortBy(value);
              setPage(1);
            }}
            onSortOrderChange={(value) => {
              setSortOrder(value);
              setPage(1);
            }}
          />
        </div>

        {/* Layout Toggle */}
        <div className="flex gap-1" data-tour="view-toggle">
          <Button
            variant={layout === "list" ? "default" : "outline"}
            size="icon"
            onClick={() => setLayout("list")}
            aria-label="List view"
          >
            <LayoutList className="h-4 w-4" />
          </Button>
          <Button
            variant={layout === "grid" ? "default" : "outline"}
            size="icon"
            onClick={() => setLayout("grid")}
            aria-label="Grid view"
          >
            <LayoutGrid className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Task Count Badges and Select All */}
      <div className="flex items-center justify-between">
        {metadata && (
          <div className="flex gap-4 text-sm">
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">Pending:</span>
              <span className="font-medium">{metadata.total_pending}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">Completed:</span>
              <span className="font-medium">{metadata.total_completed}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">Total:</span>
              <span className="font-medium">{metadata.total_active}</span>
            </div>
          </div>
        )}

        {/* Select All Checkbox */}
        {tasks.length > 0 && (
          <div className="flex items-center gap-2">
            <Checkbox
              id="select-all"
              checked={allSelected}
              onCheckedChange={toggleSelectAll}
            />
            <label
              htmlFor="select-all"
              className="text-sm font-medium cursor-pointer"
            >
              Select All
            </label>
          </div>
        )}
      </div>

      {/* Task Grid/List with Drag and Drop */}
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <SortableContext items={taskIds} strategy={verticalListSortingStrategy}>
          <LayoutGroup>
            <motion.div
              variants={prefersReducedMotion ? undefined : staggerContainer}
              initial="hidden"
              animate="visible"
              className={
                layout === "grid"
                  ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                  : "space-y-3"
              }
            >
              <AnimatePresence mode="popLayout">
                {tasks.map((task, index) => {
                  const isKeyboardSelected = index === selectedTaskIndex;
                  return (
                    <motion.div
                      key={task.id}
                      data-task-index={index}
                      layout={!prefersReducedMotion}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, x: -100, transition: { duration: 0.3 } }}
                      transition={{ duration: 0.2 }}
                      className="flex items-start gap-2"
                      onClick={() => setSelectedTaskIndex(index)}
                    >
                      {/* Bulk Selection Checkbox - Hidden on mobile when using swipe gestures */}
                      {!isMobile && (
                        <Checkbox
                          checked={selectedTaskIds.has(task.id)}
                          onCheckedChange={() => toggleTaskSelection(task.id)}
                          className="mt-4"
                          aria-label={`Select ${task.title}`}
                        />
                      )}
                      <div className="flex-1">
                        {/* Use SwipeableTaskCard on mobile, SortableTaskCard on desktop */}
                        {isMobile ? (
                          <SwipeableTaskCard
                            task={task}
                            variant={layout}
                            searchQuery={debouncedValue}
                            disabled={isDragDisabled}
                          />
                        ) : (
                          <SortableTaskCard
                            task={task}
                            variant={layout}
                            searchQuery={debouncedValue}
                            isDragDisabled={isDragDisabled}
                            isSelected={isKeyboardSelected}
                            onSelect={() => setSelectedTaskIndex(index)}
                          />
                        )}
                      </div>
                    </motion.div>
                  );
                })}
              </AnimatePresence>
            </motion.div>
          </LayoutGroup>
        </SortableContext>

        {/* Drag Overlay - shows a semi-transparent card following the cursor */}
        <DragOverlay>
          {activeTask && (
            <div className="opacity-80 shadow-2xl">
              <TaskCard task={activeTask} variant={layout} />
            </div>
          )}
        </DragOverlay>
      </DndContext>

      {/* Pagination */}
      {pagination && pagination.total_pages > 1 && (
        <Pagination pagination={pagination} onPageChange={setPage} />
      )}

      {/* Bulk Actions Toolbar */}
      <BulkActions
        selectedCount={selectedTaskIds.size}
        onMarkAsCompleted={() => handleBulkToggle('completed')}
        onMarkAsPending={() => handleBulkToggle('pending')}
        onBulkDelete={handleBulkDelete}
        onClearSelection={clearSelection}
      />
    </div>
  );
}
