"use client";

import { useState, useMemo } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CalendarDayCell } from "./CalendarDayCell";
import { DayTasksPanel } from "./DayTasksPanel";
import { useTasks, useUpdateTask } from "@/hooks/useTasks";
import { useToast } from "@/hooks/use-toast";
import {
  startOfMonth,
  endOfMonth,
  eachDayOfInterval,
  format,
  addMonths,
  subMonths,
  isSameMonth,
  startOfWeek,
  endOfWeek,
  isSameDay,
  isToday,
  parseISO,
  differenceInMonths,
} from "date-fns";

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export function CalendarView() {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const { toast } = useToast();

  // Fetch tasks for the current month
  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);

  const { data: tasksData } = useTasks({
    has_due_date: true,
  });

  const { mutate: updateTask } = useUpdateTask();

  const tasks = useMemo(() => tasksData?.data?.tasks || [], [tasksData?.data?.tasks]);

  // Calculate calendar days (including leading/trailing days from adjacent months)
  const calendarDays = useMemo(() => {
    const start = startOfWeek(monthStart);
    const end = endOfWeek(monthEnd);
    return eachDayOfInterval({ start, end });
  }, [monthStart, monthEnd]);

  // Group tasks by date
  const tasksByDate = useMemo(() => {
    const grouped: Record<string, typeof tasks> = {};

    tasks.forEach((task) => {
      if (task.due_date) {
        const dateKey = format(parseISO(task.due_date), "yyyy-MM-dd");
        if (!grouped[dateKey]) {
          grouped[dateKey] = [];
        }
        grouped[dateKey].push(task);
      }
    });

    return grouped;
  }, [tasks]);

  const handlePreviousMonth = () => {
    const newMonth = subMonths(currentMonth, 1);
    // Constraint: ±12 months from current month
    if (Math.abs(differenceInMonths(newMonth, new Date())) <= 12) {
      setCurrentMonth(newMonth);
      setSelectedDate(null);
    }
  };

  const handleNextMonth = () => {
    const newMonth = addMonths(currentMonth, 1);
    // Constraint: ±12 months from current month
    if (Math.abs(differenceInMonths(newMonth, new Date())) <= 12) {
      setCurrentMonth(newMonth);
      setSelectedDate(null);
    }
  };

  const handleDateClick = (date: Date) => {
    setSelectedDate(date);
  };

  const handleClosePanel = () => {
    setSelectedDate(null);
  };

  const handleTaskDrop = (taskId: string, newDate: Date) => {
    const task = tasks.find((t) => t.id === taskId);
    if (!task) return;

    // Format the new due date as ISO string
    const newDueDate = newDate.toISOString();

    updateTask(
      {
        taskId: taskId,
        data: {
          due_date: newDueDate,
        },
      },
      {
        onSuccess: () => {
          toast({
            title: "Task rescheduled",
            description: `"${task.title}" moved to ${format(newDate, "MMM d, yyyy")}`,
          });
        },
        onError: () => {
          toast({
            title: "Error",
            description: "Failed to reschedule task. Please try again.",
            variant: "destructive",
          });
        },
      }
    );
  };

  const canGoPrevious = Math.abs(differenceInMonths(subMonths(currentMonth, 1), new Date())) <= 12;
  const canGoNext = Math.abs(differenceInMonths(addMonths(currentMonth, 1), new Date())) <= 12;

  return (
    <div className="flex gap-6">
      {/* Calendar Grid */}
      <div className="flex-1">
        {/* Header with navigation */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-semibold">
            {format(currentMonth, "MMMM yyyy")}
          </h2>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePreviousMonth}
              disabled={!canGoPrevious}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setCurrentMonth(new Date());
                setSelectedDate(null);
              }}
            >
              Today
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleNextMonth}
              disabled={!canGoNext}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Weekday headers */}
        <div className="grid grid-cols-7 gap-2 mb-2">
          {WEEKDAYS.map((day) => (
            <div
              key={day}
              className="text-center text-sm font-medium text-muted-foreground py-2"
            >
              {day}
            </div>
          ))}
        </div>

        {/* Calendar grid */}
        <div className="grid grid-cols-7 gap-2">
          {calendarDays.map((day) => {
            const dateKey = format(day, "yyyy-MM-dd");
            const dayTasks = tasksByDate[dateKey] || [];
            const isCurrentMonth = isSameMonth(day, currentMonth);
            const isSelected = selectedDate && isSameDay(day, selectedDate);
            const isTodayDate = isToday(day);

            return (
              <CalendarDayCell
                key={dateKey}
                date={day}
                tasks={dayTasks}
                isCurrentMonth={isCurrentMonth}
                isSelected={!!isSelected}
                isToday={isTodayDate}
                onClick={() => handleDateClick(day)}
                onTaskDrop={handleTaskDrop}
              />
            );
          })}
        </div>
      </div>

      {/* Day Tasks Panel */}
      {selectedDate && (
        <DayTasksPanel
          date={selectedDate}
          tasks={tasksByDate[format(selectedDate, "yyyy-MM-dd")] || []}
          onClose={handleClosePanel}
        />
      )}
    </div>
  );
}
