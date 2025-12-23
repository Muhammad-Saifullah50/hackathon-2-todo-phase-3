import type { Metadata } from "next";
import { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Kanban Board",
  description: "Organize tasks by status with drag and drop functionality",
};

export default function KanbanLayout({ children }: { children: ReactNode }) {
  return children;
}
