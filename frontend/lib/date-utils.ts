import {
  format,
  formatDistanceToNow,
  addDays,
  startOfWeek,
  endOfWeek,
  startOfMonth,
  endOfMonth,
  isPast,
  isToday,
  isTomorrow,
  differenceInDays,
  parseISO,
} from "date-fns";

/**
 * Due date status types for color-coding tasks
 */
export type DueDateStatus = "overdue" | "due_soon" | "upcoming" | "none";

/**
 * Determine the status of a task based on its due date.
 *
 * @param dueDate - ISO 8601 date string or null
 * @returns DueDateStatus enum value
 *
 * Logic:
 * - overdue: Past date (not including today)
 * - due_soon: Today or tomorrow
 * - upcoming: Within 7 days
 * - none: No due date or more than 7 days away
 */
export function getDueDateStatus(dueDate: string | null): DueDateStatus {
  if (!dueDate) return "none";

  const date = parseISO(dueDate);
  const now = new Date();

  // Check if overdue (past date, excluding today)
  if (isPast(date) && !isToday(date)) {
    return "overdue";
  }

  // Check if due soon (today or tomorrow)
  if (isToday(date) || isTomorrow(date)) {
    return "due_soon";
  }

  // Check if upcoming (within next 7 days)
  const daysUntilDue = differenceInDays(date, now);
  if (daysUntilDue >= 0 && daysUntilDue <= 7) {
    return "upcoming";
  }

  return "none";
}

/**
 * Get color classes for due date badge based on status.
 *
 * @param status - DueDateStatus enum value
 * @returns Tailwind CSS class string
 */
export function getDueDateColor(status: DueDateStatus): string {
  switch (status) {
    case "overdue":
      return "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400";
    case "due_soon":
      return "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400";
    case "upcoming":
      return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400";
    default:
      return "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400";
  }
}

/**
 * Format due date for display with relative time.
 *
 * @param dueDate - ISO 8601 date string or null
 * @returns Formatted string like "Due tomorrow" or "3 days overdue"
 */
export function formatDueDate(dueDate: string | null): string {
  if (!dueDate) return "No due date";

  const date = parseISO(dueDate);
  const status = getDueDateStatus(dueDate);

  if (status === "overdue") {
    const daysOverdue = Math.abs(differenceInDays(new Date(), date));
    if (daysOverdue === 1) return "1 day overdue";
    return `${daysOverdue} days overdue`;
  }

  if (isToday(date)) return "Due today";
  if (isTomorrow(date)) return "Due tomorrow";

  // For upcoming dates, show relative time
  return `Due ${formatDistanceToNow(date, { addSuffix: true })}`;
}

/**
 * Format due date for absolute display.
 *
 * @param dueDate - ISO 8601 date string or null
 * @param formatString - date-fns format string (default: "MMM d, yyyy")
 * @returns Formatted date string
 */
export function formatDueDateAbsolute(
  dueDate: string | null,
  formatString: string = "MMM d, yyyy"
): string {
  if (!dueDate) return "No due date";
  return format(parseISO(dueDate), formatString);
}

/**
 * Get quick filter date ranges for common views.
 */
export const getQuickFilters = () => {
  const now = new Date();

  return {
    today: {
      label: "Today",
      from: format(now, "yyyy-MM-dd'T'00:00:00"),
      to: format(now, "yyyy-MM-dd'T'23:59:59"),
    },
    tomorrow: {
      label: "Tomorrow",
      from: format(addDays(now, 1), "yyyy-MM-dd'T'00:00:00"),
      to: format(addDays(now, 1), "yyyy-MM-dd'T'23:59:59"),
    },
    thisWeek: {
      label: "This Week",
      from: format(startOfWeek(now), "yyyy-MM-dd'T'00:00:00"),
      to: format(endOfWeek(now), "yyyy-MM-dd'T'23:59:59"),
    },
    thisMonth: {
      label: "This Month",
      from: format(startOfMonth(now), "yyyy-MM-dd'T'00:00:00"),
      to: format(endOfMonth(now), "yyyy-MM-dd'T'23:59:59"),
    },
    overdue: {
      label: "Overdue",
      from: "1970-01-01T00:00:00",
      to: format(addDays(now, -1), "yyyy-MM-dd'T'23:59:59"),
    },
  };
};

/**
 * Check if a date matches a quick filter.
 *
 * @param dueDate - ISO 8601 date string or null
 * @param filterKey - Key from getQuickFilters()
 * @returns boolean indicating if date matches filter
 */
export function matchesQuickFilter(
  dueDate: string | null,
  filterKey: keyof ReturnType<typeof getQuickFilters>
): boolean {
  if (!dueDate) return false;

  const date = parseISO(dueDate);
  const filters = getQuickFilters();
  const filter = filters[filterKey];

  const fromDate = parseISO(filter.from);
  const toDate = parseISO(filter.to);

  return date >= fromDate && date <= toDate;
}

/**
 * Sort tasks by due date with null handling.
 *
 * @param tasks - Array of tasks with due_date property
 * @param order - "asc" or "desc"
 * @returns Sorted array (original array is not modified)
 */
export function sortTasksByDueDate<T extends { due_date: string | null }>(
  tasks: T[],
  order: "asc" | "desc" = "asc"
): T[] {
  return [...tasks].sort((a, b) => {
    // Tasks without due dates go to the end
    if (!a.due_date && !b.due_date) return 0;
    if (!a.due_date) return 1;
    if (!b.due_date) return -1;

    const dateA = parseISO(a.due_date);
    const dateB = parseISO(b.due_date);

    return order === "asc"
      ? dateA.getTime() - dateB.getTime()
      : dateB.getTime() - dateA.getTime();
  });
}

/**
 * Group tasks by due date status.
 *
 * @param tasks - Array of tasks with due_date property
 * @returns Object with tasks grouped by status
 */
export function groupTasksByDueDate<T extends { due_date: string | null }>(
  tasks: T[]
): Record<DueDateStatus, T[]> {
  return tasks.reduce(
    (groups, task) => {
      const status = getDueDateStatus(task.due_date);
      groups[status].push(task);
      return groups;
    },
    {
      overdue: [],
      due_soon: [],
      upcoming: [],
      none: [],
    } as Record<DueDateStatus, T[]>
  );
}
