"use client";

import dynamic from "next/dynamic";
import { Skeleton } from "@/components/ui/skeleton";

const CompletionTrendChart = dynamic(
  () => import("@/components/dashboard/CompletionTrendChart").then(m => m.CompletionTrendChart),
  { ssr: false, loading: () => <Skeleton className="h-[300px] w-full rounded-xl" /> }
);

const PriorityBreakdownChart = dynamic(
  () => import("@/components/dashboard/PriorityBreakdownChart").then(m => m.PriorityBreakdownChart),
  { ssr: false, loading: () => <Skeleton className="h-[300px] w-full rounded-xl" /> }
);

export function DashboardCharts() {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <CompletionTrendChart />
      <PriorityBreakdownChart />
    </div>
  );
}
