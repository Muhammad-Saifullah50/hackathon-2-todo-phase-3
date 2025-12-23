"use client";

import { useEffect } from "react";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Task management error:", error);
  }, [error]);

  return (
    <div className="container max-w-7xl mx-auto py-6 px-4">
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
        <div className="rounded-full bg-destructive/10 p-6 mb-6">
          <AlertTriangle className="h-12 w-12 text-destructive" />
        </div>
        <h1 className="text-2xl font-bold mb-2">Something went wrong</h1>
        <p className="text-muted-foreground mb-6 max-w-md">
          An error occurred while loading your tasks. Please try refreshing the page or
          contact support if the problem persists.
        </p>
        <details className="mb-6 text-sm text-muted-foreground max-w-2xl">
          <summary className="cursor-pointer font-medium mb-2">
            Error details
          </summary>
          <pre className="text-left bg-muted p-4 rounded-lg overflow-auto">
            {error.message}
          </pre>
        </details>
        <Button onClick={reset}>Try Again</Button>
      </div>
    </div>
  );
}