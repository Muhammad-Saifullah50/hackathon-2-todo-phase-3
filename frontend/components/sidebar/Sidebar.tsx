"use client";

import { SidebarClient } from "./SidebarClient";
import { useSession } from "@/components/session-provider";

export function Sidebar() {
  const { session, isLoading } = useSession();

  // Don't render sidebar while loading or if user is not authenticated
  if (isLoading || !session) {
    return null;
  }

  return <SidebarClient />;
}
