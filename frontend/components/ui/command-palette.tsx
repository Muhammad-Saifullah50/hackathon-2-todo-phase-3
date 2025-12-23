"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Command } from "cmdk";
import {
  Search,
  Plus,
  ListTodo,
  LayoutDashboard,
  Calendar,
  Columns3,
  Filter,
  Settings,
  Tag,
  CheckSquare,
  Clock,
  AlertCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface CommandAction {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  keywords?: string[];
  group: string;
  action: () => void;
  shortcut?: string;
}

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onNewTask?: () => void;
  onApplyFilter?: (filter: string) => void;
}

export function CommandPalette({
  open,
  onOpenChange,
  onNewTask,
  onApplyFilter,
}: CommandPaletteProps) {
  const router = useRouter();
  const [search, setSearch] = React.useState("");

  const actions: CommandAction[] = React.useMemo(() => [
    {
      id: "new-task",
      label: "Create New Task",
      icon: Plus,
      keywords: ["add", "create", "new"],
      group: "Actions",
      action: () => {
        onNewTask?.();
        onOpenChange(false);
      },
      shortcut: "N",
    },
    {
      id: "search-tasks",
      label: "Search Tasks",
      icon: Search,
      keywords: ["find", "filter", "search"],
      group: "Actions",
      action: () => {
        router.push("/tasks");
        onOpenChange(false);
      },
      shortcut: "/",
    },
    {
      id: "view-list",
      label: "View Tasks List",
      icon: ListTodo,
      keywords: ["list", "tasks", "all"],
      group: "Navigation",
      action: () => {
        router.push("/tasks");
        onOpenChange(false);
      },
    },
    {
      id: "view-dashboard",
      label: "View Dashboard",
      icon: LayoutDashboard,
      keywords: ["dashboard", "stats", "analytics"],
      group: "Navigation",
      action: () => {
        router.push("/tasks/dashboard");
        onOpenChange(false);
      },
    },
    {
      id: "view-calendar",
      label: "View Calendar",
      icon: Calendar,
      keywords: ["calendar", "schedule", "dates"],
      group: "Navigation",
      action: () => {
        router.push("/tasks/calendar");
        onOpenChange(false);
      },
    },
    {
      id: "view-kanban",
      label: "View Kanban Board",
      icon: Columns3,
      keywords: ["kanban", "board", "columns"],
      group: "Navigation",
      action: () => {
        router.push("/tasks/kanban");
        onOpenChange(false);
      },
    },
    {
      id: "filter-today",
      label: "Filter: Today",
      icon: CheckSquare,
      keywords: ["today", "filter"],
      group: "Filters",
      action: () => {
        onApplyFilter?.("today");
        onOpenChange(false);
      },
    },
    {
      id: "filter-week",
      label: "Filter: This Week",
      icon: Clock,
      keywords: ["week", "filter"],
      group: "Filters",
      action: () => {
        onApplyFilter?.("week");
        onOpenChange(false);
      },
    },
    {
      id: "filter-overdue",
      label: "Filter: Overdue",
      icon: AlertCircle,
      keywords: ["overdue", "late", "filter"],
      group: "Filters",
      action: () => {
        onApplyFilter?.("overdue");
        onOpenChange(false);
      },
    },
    {
      id: "filter-high",
      label: "Filter: High Priority",
      icon: Filter,
      keywords: ["priority", "high", "important", "filter"],
      group: "Filters",
      action: () => {
        onApplyFilter?.("high");
        onOpenChange(false);
      },
    },
    {
      id: "manage-tags",
      label: "Manage Tags",
      icon: Tag,
      keywords: ["tags", "labels", "categories"],
      group: "Actions",
      action: () => {
        router.push("/tasks?action=manage-tags");
        onOpenChange(false);
      },
    },
    {
      id: "settings",
      label: "Settings",
      icon: Settings,
      keywords: ["settings", "preferences", "config"],
      group: "Navigation",
      action: () => {
        router.push("/settings");
        onOpenChange(false);
      },
    },
  ], [router, onNewTask, onApplyFilter, onOpenChange]);

  const filteredActions = React.useMemo(() => {
    if (!search) return actions;

    const lowerSearch = search.toLowerCase();
    return actions.filter(
      (action) =>
        action.label.toLowerCase().includes(lowerSearch) ||
        action.keywords?.some((keyword) => keyword.includes(lowerSearch))
    );
  }, [search, actions]);

  const groupedActions = React.useMemo(() => {
    const groups: Record<string, CommandAction[]> = {};
    filteredActions.forEach((action) => {
      if (!groups[action.group]) {
        groups[action.group] = [];
      }
      groups[action.group].push(action);
    });
    return groups;
  }, [filteredActions]);

  React.useEffect(() => {
    if (!open) {
      setSearch("");
    }
  }, [open]);

  return (
    <Command.Dialog
      open={open}
      onOpenChange={onOpenChange}
      label="Command Palette"
      className={cn(
        "fixed left-1/2 top-1/2 z-50 w-full max-w-2xl -translate-x-1/2 -translate-y-1/2",
        "rounded-lg border bg-popover shadow-lg",
        "animate-in fade-in-0 zoom-in-95"
      )}
    >
      <div className="flex items-center border-b px-3">
        <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
        <Command.Input
          value={search}
          onValueChange={setSearch}
          placeholder="Type a command or search..."
          className="flex h-11 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
        />
      </div>

      <Command.List className="max-h-[400px] overflow-y-auto overflow-x-hidden p-2">
        <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
          No results found.
        </Command.Empty>

        {Object.entries(groupedActions).map(([group, groupActions]) => (
          <Command.Group
            key={group}
            heading={group}
            className="[&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5 [&_[cmdk-group-heading]]:text-xs [&_[cmdk-group-heading]]:font-medium [&_[cmdk-group-heading]]:text-muted-foreground"
          >
            {groupActions.map((action) => {
              const Icon = action.icon;
              return (
                <Command.Item
                  key={action.id}
                  value={action.label}
                  onSelect={() => action.action()}
                  className={cn(
                    "relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none",
                    "aria-selected:bg-accent aria-selected:text-accent-foreground",
                    "data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
                  )}
                >
                  <Icon className="mr-2 h-4 w-4" />
                  <span className="flex-1">{action.label}</span>
                  {action.shortcut && (
                    <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
                      {action.shortcut}
                    </kbd>
                  )}
                </Command.Item>
              );
            })}
          </Command.Group>
        ))}
      </Command.List>
    </Command.Dialog>
  );
}
