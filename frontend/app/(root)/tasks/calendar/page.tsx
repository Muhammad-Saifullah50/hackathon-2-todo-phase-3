import type { Metadata } from "next";
import { CalendarView } from "@/components/calendar/CalendarView";

export const metadata: Metadata = {
  title: "Calendar",
  description: "View and manage your tasks by due date in calendar view",
};

export default function CalendarPage() {
  return (
    <div className="max-w-7xl mx-auto py-6 w-full">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Calendar</h1>
        <p className="text-muted-foreground mt-2">
          View and manage your tasks by due date
        </p>
      </div>
      <CalendarView />
    </div>
  );
}
