"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { usePriorityBreakdown } from "@/hooks/useAnalytics";
import { Skeleton } from "@/components/ui/skeleton";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import Image from "next/image";

const COLORS = {
  low: "hsl(var(--chart-1))",
  medium: "hsl(var(--chart-2))",
  high: "hsl(var(--chart-3))",
};

const PRIORITY_LABELS = {
  low: "Low",
  medium: "Medium",
  high: "High",
};

export function PriorityBreakdownChart() {
  const { data, isLoading, error } = usePriorityBreakdown();

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Priority Breakdown</CardTitle>
          <CardDescription>Distribution by priority level</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-[300px] items-center justify-center">
            <p className="text-sm text-destructive">Failed to load chart data</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isLoading || !data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Priority Breakdown</CardTitle>
          <CardDescription>Distribution by priority level</CardDescription>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[300px] w-full" />
        </CardContent>
      </Card>
    );
  }

  const breakdown = data.data;
  const chartData = breakdown.data.map((item) => ({
    name: PRIORITY_LABELS[item.priority as keyof typeof PRIORITY_LABELS] || item.priority,
    value: item.count,
    percentage: item.percentage,
    priority: item.priority,
  }));

  // Show empty state if no tasks
  if (breakdown.total === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Priority Breakdown</CardTitle>
          <CardDescription>Distribution by priority level</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-[300px] flex-col items-center justify-center space-y-4">
            <Image
              src="/illustrations/no-data.svg"
              alt="No data available"
              width={80}
              height={80}
              className="opacity-50"
            />
            <div className="text-center">
              <p className="text-sm font-medium">No tasks yet</p>
              <p className="text-xs text-muted-foreground">
                Create tasks with different priorities to see the breakdown
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Priority Breakdown</CardTitle>
        <CardDescription>
          Distribution by priority level ({breakdown.total} total)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={(props) => {
                const { name, payload } = props as { name: string; payload: { percentage: number } };
                const percentage = payload?.percentage ?? 0;
                return `${name}: ${percentage.toFixed(1)}%`;
              }}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[entry.priority as keyof typeof COLORS] || "#888"}
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--background))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
              formatter={(value, name, props) => {
                const percentage = (props as { payload: { percentage: number } }).payload?.percentage ?? 0;
                return [`${value} tasks (${percentage.toFixed(1)}%)`, name];
              }}
            />
            <Legend
              wrapperStyle={{
                paddingTop: "20px",
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
