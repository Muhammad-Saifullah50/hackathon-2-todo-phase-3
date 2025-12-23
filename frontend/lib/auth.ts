import { auth } from "@/auth";
import { headers } from "next/headers";
import { cache } from "react";

/**
 * Get the current session server-side
 * This is cached per request to avoid multiple database calls
 */
export const getSession = cache(async () => {
  try {
    const session = await auth.api.getSession({
      headers: await headers(),
    });
    return session;
  } catch (error) {
    console.error("Error fetching session:", error);
    return null;
  }
});
