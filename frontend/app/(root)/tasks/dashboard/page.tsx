import type { Metadata } from "next";
import { StatsCards } from "@/components/dashboard/StatsCards";
import { CompletionTrendChart } from "@/components/dashboard/CompletionTrendChart";
import { PriorityBreakdownChart } from "@/components/dashboard/PriorityBreakdownChart";
import { CreateTaskDialog } from "@/components/tasks/CreateTaskDialog";

export const metadata: Metadata = {
  title: "Dashboard",
  description: "Overview of your tasks and productivity metrics",
};

export default function DashboardPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 pt-6 w-full h-[calc(100vh-4rem)] flex flex-col">
      <div className="flex items-center justify-between mb-6 shrink-0">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Overview of your tasks and productivity metrics
          </p>
        </div>
        <CreateTaskDialog />
      </div>

      <div className="flex-1 overflow-y-auto space-y-6 pb-6 pr-1">
        <StatsCards />

        <div className="grid gap-6 md:grid-cols-2">
          <CompletionTrendChart />
          <PriorityBreakdownChart />
        </div>
      </div>
    </div>
  );
}
