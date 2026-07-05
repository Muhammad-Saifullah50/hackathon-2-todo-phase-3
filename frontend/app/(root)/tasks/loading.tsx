import { TaskListSkeleton } from "@/components/tasks/TaskListSkeleton";

export default function TasksLoading() {
  return (
    <div className="max-w-7xl mx-auto px-4 pt-6 w-full h-[calc(100vh-4rem)] flex flex-col">
      <div className="flex items-center justify-between mb-4 shrink-0">
        <div>
          <div className="h-9 w-36 bg-muted rounded animate-pulse" />
          <div className="h-4 w-64 bg-muted rounded mt-2 animate-pulse" />
        </div>
        <div className="h-10 w-32 bg-muted rounded animate-pulse" />
      </div>
      <div className="flex-1 overflow-y-auto">
        <TaskListSkeleton count={5} variant="list" />
      </div>
    </div>
  );
}
