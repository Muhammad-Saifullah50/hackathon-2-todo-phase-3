"use client";

import { SidebarClient } from "./SidebarClient";
import { authClient } from "@/lib/auth-client";
import { use, cache } from "react";

// Cache the session fetch to prevent duplicate requests
const getSession = cache(async () => {
  try {
    const { data } = await authClient.getSession();
    return data;
  } catch (error) {
    console.error("Error fetching session:", error);
    return null;
  }
});

export function Sidebar() {
  const session = use(getSession());

  // Don't render sidebar if user is not authenticated
  if (!session) {
    return null;
  }

  return <SidebarClient />;
}