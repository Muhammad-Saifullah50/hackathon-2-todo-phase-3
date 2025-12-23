/**
 * Tasks Page - Main page for task management (SERVER COMPONENT).
 * Displays task list and provides task creation functionality.
 * Server Component by default - only imports Client Components.
 */

import type { Metadata } from "next";
import { CreateTaskDialog } from "@/components/tasks/CreateTaskDialog";
import { TaskList } from "@/components/tasks/TaskList";

export const metadata: Metadata = {
  title: "My Tasks",
  description: "Manage your tasks and stay organized with Todoly's powerful task management interface",
};

export default function TasksPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 pt-6 w-full">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">My Tasks</h1>
          <p className="text-muted-foreground mt-1">
            Manage your tasks and stay organized
          </p>
        </div>
        <div data-tour="create-task-button">
          <CreateTaskDialog />
        </div>
      </div>

      {/* Task List with filters, sorting, and pagination */}
      <TaskList />
    </div>
  );
}
