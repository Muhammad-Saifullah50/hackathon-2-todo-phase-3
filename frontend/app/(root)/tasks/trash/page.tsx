import type { Metadata } from "next";
import { TrashView } from "@/components/tasks/TrashView";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Trash",
  description: "Restore or permanently delete your trashed tasks",
};

export default function TrashPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 pt-6 w-full h-[calc(100vh-4rem)] flex flex-col">
      <div className="flex items-center justify-between mb-6 shrink-0">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <Link href="/tasks">
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <ArrowLeft className="h-4 w-4" />
              </Button>
            </Link>
            <h1 className="text-3xl font-bold tracking-tight">Trash</h1>
          </div>
          <p className="text-muted-foreground">
            Deleted tasks are kept here. You can restore them or delete them permanently.
          </p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto min-h-0 pb-6 pr-1">
        <TrashView />
      </div>
    </div>
  );
}
