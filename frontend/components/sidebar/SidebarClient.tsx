"use client";

import { useSidebarStore } from "@/lib/sidebar-store";
import { TooltipProvider } from "@/components/ui/tooltip";
import { SidebarNav } from "./SidebarNav";
import { SidebarMobile } from "./SidebarMobile";
import { LogoutButton } from "./LogoutButton";
import { CollapseToggle } from "./CollapseToggle";
import {
  CheckSquare,
  Calendar,
  LayoutGrid,
  BarChart3,
  Trash2,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navItems: NavItem[] = [
  { label: "My Tasks", href: "/tasks", icon: CheckSquare },
  { label: "Calendar", href: "/tasks/calendar", icon: Calendar },
  { label: "Kanban", href: "/tasks/kanban", icon: LayoutGrid },
  { label: "Dashboard", href: "/tasks/dashboard", icon: BarChart3 },
  { label: "Trash", href: "/tasks/trash", icon: Trash2 },
];

export function SidebarClient() {
  const { isCollapsed } = useSidebarStore();

  return (
    <TooltipProvider>
      <SidebarMobile>
        <aside
          className={cn(
            "fixed left-0  z-40 h-[calc(100vh-3.5rem)] border-r bg-background/95 backdrop-blur transition-all duration-300",
            isCollapsed ? "w-16" : "w-56",
            // Mobile styles
            "md:translate-x-0"
          )}
        >
          <div className="flex h-full flex-col">
            {/* Navigation items */}
            <nav className="flex-1 space-y-1 p-3">
              <SidebarNav items={navItems} isCollapsed={isCollapsed} />
            </nav>

            {/* Bottom section */}
            <div className="border-t p-3 space-y-1">
              {/* Settings link */}
              <SidebarNav
                items={[
                  { label: "Settings", href: "/settings", icon: Settings },
                ]}
                isCollapsed={isCollapsed}
              />

              {/* Logout button */}
              <LogoutButton isCollapsed={isCollapsed} />

              {/* Collapse toggle - desktop only */}
              <CollapseToggle />
            </div>
          </div>
        </aside>
      </SidebarMobile>
    </TooltipProvider>
  );
}
