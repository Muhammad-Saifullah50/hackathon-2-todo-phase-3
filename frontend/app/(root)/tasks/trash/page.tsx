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
    <div className="max-w-7xl mx-auto py-6 px-4 w-full">
      <div className="flex items-center justify-between mb-6">
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

      {/* Trash View with restore and permanent delete options */}
      <TrashView />
    </div>
  );
}
