"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAnalyticsStats } from "@/hooks/useAnalytics";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, CheckCircle2, Clock, ListTodo } from "lucide-react";
import { useRouter } from "next/navigation";

export function StatsCards() {
  const { data, isLoading, error } = useAnalyticsStats();
  const router = useRouter();

  if (error) {
    return (
      <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4">
        <p className="text-sm text-destructive">
          Failed to load statistics. Please try again.
        </p>
      </div>
    );
  }

  if (isLoading || !data) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-4 rounded-full" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16" />
              <Skeleton className="mt-2 h-3 w-32" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const stats = data.data;

  const statCards = [
    {
      title: "Pending Tasks",
      value: stats.pending_count,
      description: "Active tasks to complete",
      icon: Clock,
      color: "text-blue-600",
      bgColor: "bg-blue-100 dark:bg-blue-900/20",
      onClick: () => router.push("/tasks?status=pending"),
    },
    {
      title: "Completed Today",
      value: stats.completed_today_count,
      description: "Tasks finished today",
      icon: CheckCircle2,
      color: "text-green-600",
      bgColor: "bg-green-100 dark:bg-green-900/20",
      onClick: () => router.push("/tasks?completed=today"),
    },
    {
      title: "Overdue",
      value: stats.overdue_count,
      description: "Tasks past due date",
      icon: AlertCircle,
      color: "text-red-600",
      bgColor: "bg-red-100 dark:bg-red-900/20",
      onClick: () => router.push("/tasks?status=pending&overdue=true"),
    },
    {
      title: "Total Tasks",
      value: stats.total_count,
      description: "All active tasks",
      icon: ListTodo,
      color: "text-purple-600",
      bgColor: "bg-purple-100 dark:bg-purple-900/20",
      onClick: () => router.push("/tasks"),
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {statCards.map((stat) => {
        const Icon = stat.icon;
        return (
          <Card
            key={stat.title}
            className="cursor-pointer transition-all hover:scale-105 hover:shadow-lg"
            onClick={stat.onClick}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <div className={`rounded-full p-2 ${stat.bgColor}`}>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.description}</p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
