"use client";

import { format } from "date-fns";
import { X, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { TaskCard } from "@/components/tasks/TaskCard";
import { CreateTaskDialog } from "@/components/tasks/CreateTaskDialog";
import { useState } from "react";
import type { Task } from "@/lib/types/task";

interface DayTasksPanelProps {
  date: Date;
  tasks: Task[];
  onClose: () => void;
}

export function DayTasksPanel({ date, tasks, onClose }: DayTasksPanelProps) {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  const formattedDate = format(date, "EEEE, MMMM d, yyyy");

  const handleCreateTask = () => {
    setIsCreateDialogOpen(true);
  };

  return (
    <div className="w-96 border-l pl-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold">{formattedDate}</h3>
          <p className="text-sm text-muted-foreground">
            {tasks.length} {tasks.length === 1 ? "task" : "tasks"}
          </p>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Create Task Button */}
      <Button
        onClick={handleCreateTask}
        className="w-full mb-4"
        variant="outline"
      >
        <Plus className="h-4 w-4 mr-2" />
        Create Task
      </Button>

      {/* Task List */}
      <div className="space-y-3 max-h-[calc(100vh-250px)] overflow-y-auto">
        {tasks.length === 0 ? (
          <Card className="p-6 text-center">
            <p className="text-muted-foreground">No tasks for this day</p>
          </Card>
        ) : (
          tasks.map((task) => <TaskCard key={task.id} task={task} />)
        )}
      </div>

      {/* Create Task Dialog with pre-filled due date */}
      <CreateTaskDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        hideTrigger={true}
        defaultValues={{
          due_date: date.toISOString(),
        }}
      />
    </div>
  );
}
