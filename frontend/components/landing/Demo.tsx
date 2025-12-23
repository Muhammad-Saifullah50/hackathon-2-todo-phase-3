"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  List,
  LayoutGrid,
  KanbanSquare,
  Calendar as CalendarIcon,
  CheckCircle2,
  Circle,
  Calendar,
} from "lucide-react";
import { fadeIn, slideIn } from "@/lib/animations";
import { Button } from "@/components/ui/button";

type ViewType = "list" | "grid" | "kanban" | "calendar";

const views = [
  { id: "list" as ViewType, label: "List View", icon: List },
  { id: "grid" as ViewType, label: "Grid View", icon: LayoutGrid },
  { id: "kanban" as ViewType, label: "Kanban Board", icon: KanbanSquare },
  { id: "calendar" as ViewType, label: "Calendar", icon: CalendarIcon },
];

const mockTasks = [
  {
    id: 1,
    title: "Design new landing page",
    status: "completed",
    priority: "high",
    dueDate: "2025-12-20",
    tags: ["Design", "Marketing"],
  },
  {
    id: 2,
    title: "Review Q4 budget proposal",
    status: "pending",
    priority: "high",
    dueDate: "2025-12-22",
    tags: ["Finance"],
  },
  {
    id: 3,
    title: "Update team documentation",
    status: "pending",
    priority: "medium",
    dueDate: "2025-12-25",
    tags: ["Documentation"],
  },
  {
    id: 4,
    title: "Plan marketing campaign",
    status: "pending",
    priority: "low",
    dueDate: "2025-12-28",
    tags: ["Marketing"],
  },
];

/**
 * Demo section with tabbed navigation showing different view modes.
 * Features animated previews of List, Grid, Kanban, and Calendar views.
 */
export default function Demo() {
  const [activeView, setActiveView] = useState<ViewType>("list");

  return (
    <section id="demo" className="py-24 bg-gray-50 dark:bg-gray-800">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center max-w-3xl mx-auto mb-12"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={fadeIn}
        >
          <h2 className="text-4xl sm:text-5xl font-bold tracking-tight mb-4">
            Work your way
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            Switch between different views to match your workflow. All your tasks, visualized
            beautifully.
          </p>
        </motion.div>

        {/* View Tabs */}
        <motion.div
          className="flex flex-wrap justify-center gap-2 mb-8"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={slideIn}
        >
          {views.map((view) => {
            const Icon = view.icon;
            return (
              <Button
                key={view.id}
                variant={activeView === view.id ? "default" : "outline"}
                size="lg"
                onClick={() => setActiveView(view.id)}
                className="gap-2"
              >
                <Icon className="h-5 w-5" />
                {view.label}
              </Button>
            );
          })}
        </motion.div>

        {/* View Preview */}
        <div className="max-w-5xl mx-auto">
          <AnimatePresence mode="wait">
            {activeView === "list" && <ListView key="list" />}
            {activeView === "grid" && <GridView key="grid" />}
            {activeView === "kanban" && <KanbanView key="kanban" />}
            {activeView === "calendar" && <CalendarView key="calendar" />}
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
}

function ListView() {
  return (
    <motion.div
      className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-6 border border-gray-200 dark:border-gray-700"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      <div className="space-y-3">
        {mockTasks.map((task, index) => (
          <motion.div
            key={task.id}
            className="flex items-center gap-4 p-4 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 transition-colors"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            {task.status === "completed" ? (
              <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0" />
            ) : (
              <Circle className="h-5 w-5 text-gray-400 flex-shrink-0" />
            )}
            <div className="flex-1 min-w-0">
              <h3
                className={`font-medium text-sm ${
                  task.status === "completed"
                    ? "line-through text-gray-500"
                    : "text-gray-900 dark:text-gray-100"
                }`}
              >
                {task.title}
              </h3>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  {task.dueDate}
                </span>
              </div>
            </div>
            <div className="flex gap-1">
              {task.tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400"
                >
                  {tag}
                </span>
              ))}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

function GridView() {
  return (
    <motion.div
      className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-6 border border-gray-200 dark:border-gray-700"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {mockTasks.map((task, index) => (
          <motion.div
            key={task.id}
            className="p-4 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 transition-all hover:shadow-lg"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
          >
            <div className="flex items-start gap-3 mb-3">
              {task.status === "completed" ? (
                <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
              ) : (
                <Circle className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
              )}
              <h3
                className={`font-medium text-sm flex-1 ${
                  task.status === "completed"
                    ? "line-through text-gray-500"
                    : "text-gray-900 dark:text-gray-100"
                }`}
              >
                {task.title}
              </h3>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {task.dueDate}
              </span>
              <div className="flex gap-1">
                {task.tags.slice(0, 1).map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

function KanbanView() {
  const columns = [
    { id: "pending", title: "To Do", tasks: mockTasks.filter((t) => t.status === "pending") },
    {
      id: "completed",
      title: "Done",
      tasks: mockTasks.filter((t) => t.status === "completed"),
    },
  ];

  return (
    <motion.div
      className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-6 border border-gray-200 dark:border-gray-700"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {columns.map((column, colIndex) => (
          <div key={column.id}>
            <h3 className="font-semibold text-sm text-gray-700 dark:text-gray-300 mb-3 flex items-center justify-between">
              {column.title}
              <span className="text-xs text-gray-500 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                {column.tasks.length}
              </span>
            </h3>
            <div className="space-y-3">
              {column.tasks.map((task, index) => (
                <motion.div
                  key={task.id}
                  className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 transition-all cursor-move hover:shadow-md"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: colIndex * 0.2 + index * 0.1 }}
                >
                  <h4 className="font-medium text-sm text-gray-900 dark:text-gray-100 mb-2">
                    {task.title}
                  </h4>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {task.dueDate}
                    </span>
                    <span
                      className={`text-xs px-2 py-0.5 rounded ${
                        task.priority === "high"
                          ? "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400"
                          : task.priority === "medium"
                          ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400"
                          : "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300"
                      }`}
                    >
                      {task.priority}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}

function CalendarView() {
  return (
    <motion.div
      className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-6 border border-gray-200 dark:border-gray-700"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      {/* Calendar Header */}
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
          December 2025
        </h3>
        <div className="grid grid-cols-7 gap-2 text-center text-xs font-medium text-gray-500 dark:text-gray-400">
          {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
            <div key={day}>{day}</div>
          ))}
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-2">
        {Array.from({ length: 35 }, (_, i) => {
          const day = i - 3;
          const hasTask = [20, 22, 25, 28].includes(day);
          const isToday = day === 21;

          return (
            <motion.div
              key={i}
              className={`aspect-square p-2 rounded-lg text-center ${
                day < 1 || day > 31
                  ? "text-gray-300 dark:text-gray-700"
                  : isToday
                  ? "bg-blue-500 text-white font-semibold"
                  : hasTask
                  ? "bg-purple-100 dark:bg-purple-900/30 text-purple-900 dark:text-purple-100 font-medium"
                  : "bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              } ${hasTask || isToday ? "cursor-pointer hover:scale-105" : ""} transition-all`}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.01 }}
            >
              {day > 0 && day <= 31 && (
                <>
                  <div className="text-sm">{day}</div>
                  {hasTask && !isToday && (
                    <div className="mt-1 w-1 h-1 rounded-full bg-purple-500 mx-auto" />
                  )}
                </>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-6 flex items-center gap-4 text-xs text-gray-600 dark:text-gray-400">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-blue-500" />
          <span>Today</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-purple-100 dark:bg-purple-900/30 border border-purple-300 dark:border-purple-700" />
          <span>Has Tasks</span>
        </div>
      </div>
    </motion.div>
  );
}
