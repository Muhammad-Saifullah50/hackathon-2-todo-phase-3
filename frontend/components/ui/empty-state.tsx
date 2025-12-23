/**
 * EmptyState Component - Reusable component for displaying empty states
 * with illustrations, heading, description, and optional action button.
 */

import { ReactNode } from "react";
import { Button } from "./button";
import { cn } from "@/lib/utils";

interface EmptyStateProps {
  illustration: ReactNode;
  heading: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
    variant?: "default" | "outline" | "secondary" | "ghost" | "link" | "destructive";
  };
  className?: string;
}

export function EmptyState({
  illustration,
  heading,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "rounded-lg border border-dashed p-12 text-center",
        className
      )}
    >
      <div className="flex flex-col items-center gap-4">
        {/* Illustration */}
        <div className="rounded-full bg-muted p-4">
          {illustration}
        </div>

        {/* Text Content */}
        <div className="space-y-2">
          <h3 className="text-lg font-semibold">{heading}</h3>
          <p className="text-sm text-muted-foreground max-w-md">
            {description}
          </p>
        </div>

        {/* Action Button */}
        {action && (
          <Button
            variant={action.variant || "outline"}
            onClick={action.onClick}
          >
            {action.label}
          </Button>
        )}
      </div>
    </div>
  );
}
