"use client";

import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { useSidebarStore } from "@/lib/sidebar-store";

export function CollapseToggle() {
  const { isCollapsed, toggle: toggleCollapsed } = useSidebarStore();

  return (
    <Button
      variant="ghost"
      size="sm"
      className={cn(
        "hidden md:flex w-full items-center gap-3 justify-start text-muted-foreground px-3 py-2",
        isCollapsed && "justify-center px-2"
      )}
      onClick={() => toggleCollapsed()}
    >
      {isCollapsed ? (
        <ChevronRight className="h-5 w-5" />
      ) : (
        <>
          <ChevronLeft className="h-5 w-5" />
          <span className="text-sm">Collapse</span>
        </>
      )}
    </Button>
  );
}
