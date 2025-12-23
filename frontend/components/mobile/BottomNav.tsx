"use client";

/**
 * BottomNav Component - Fixed bottom navigation bar for mobile devices.
 * Provides quick access to Tasks, Dashboard, Calendar, and Settings.
 * Only visible on mobile viewports (<768px).
 */

import { usePathname, useRouter } from "next/navigation";
import {
  ListTodo,
  LayoutDashboard,
  Calendar,
  Kanban
} from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface NavItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  href: string;
  matchPaths?: string[];
}

const navItems: NavItem[] = [
  {
    id: "tasks",
    label: "Tasks",
    icon: ListTodo,
    href: "/tasks",
    matchPaths: ["/tasks", "/tasks/trash"],
  },
  {
    id: "kanban",
    label: "Kanban",
    icon: Kanban,
    href: "/tasks/kanban",
    matchPaths: ["/tasks/kanban"],
  },
  {
    id: "calendar",
    label: "Calendar",
    icon: Calendar,
    href: "/tasks/calendar",
    matchPaths: ["/tasks/calendar"],
  },
  {
    id: "dashboard",
    label: "Dashboard",
    icon: LayoutDashboard,
    href: "/tasks/dashboard",
    matchPaths: ["/tasks/dashboard"],
  },
];

/**
 * Trigger haptic feedback for navigation tap.
 */
function triggerHapticFeedback() {
  if (typeof navigator !== "undefined" && "vibrate" in navigator) {
    try {
      navigator.vibrate([10]);
    } catch {
      // Vibration not supported
    }
  }
}

export function BottomNav() {
  const pathname = usePathname();
  const router = useRouter();

  const handleNavClick = (href: string) => {
    triggerHapticFeedback();
    router.push(href);
  };

  const isActive = (item: NavItem) => {
    if (item.matchPaths) {
      return item.matchPaths.some(
        (path) => pathname === path || (path !== "/" && pathname.startsWith(path + "/"))
      );
    }
    return pathname === item.href;
  };

  // Don't show on landing page
  if (pathname === "/") {
    return null;
  }

  return (
    <nav
      className={cn(
        "fixed bottom-0 left-0 right-0 z-50",
        "bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60",
        "border-t border-border",
        "md:hidden", // Only visible on mobile
        "safe-area-inset-bottom" // iOS safe area support
      )}
      aria-label="Mobile navigation"
      role="navigation"
    >
      <div className="flex items-center justify-around h-16 px-2">
        {navItems.map((item) => {
          const isItemActive = isActive(item);
          const Icon = item.icon;

          return (
            <button
              key={item.id}
              onClick={() => handleNavClick(item.href)}
              className={cn(
                "flex flex-col items-center justify-center",
                "min-w-[64px] min-h-[44px]", // Minimum 44x44 tap target
                "px-3 py-2",
                "rounded-lg",
                "transition-colors duration-200",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                isItemActive
                  ? "text-primary"
                  : "text-muted-foreground hover:text-foreground"
              )}
              aria-current={isItemActive ? "page" : undefined}
              aria-label={item.label}
            >
              <motion.div
                initial={false}
                animate={{
                  scale: isItemActive ? 1.1 : 1,
                  y: isItemActive ? -2 : 0,
                }}
                transition={{ type: "spring", stiffness: 400, damping: 25 }}
              >
                <Icon className={cn("h-5 w-5", isItemActive && "stroke-[2.5px]")} />
              </motion.div>
              <span
                className={cn(
                  "text-[10px] mt-1 font-medium",
                  isItemActive && "font-semibold"
                )}
              >
                {item.label}
              </span>
              {isItemActive && (
                <motion.div
                  layoutId="bottomNavIndicator"
                  className="absolute bottom-1 h-0.5 w-8 rounded-full bg-primary"
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                />
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
