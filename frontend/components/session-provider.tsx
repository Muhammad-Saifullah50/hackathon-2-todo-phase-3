"use client";

import { createContext, useContext, useEffect, useState, useRef, ReactNode } from "react";
import { authClient } from "@/lib/auth-client";

interface SessionContextType {
  session: { user: unknown } | null;
  isLoading: boolean;
  refreshSession: () => Promise<void>;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<{ user: unknown } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const hasFetchedRef = useRef(false);

  const fetchSession = async () => {
    try {
      const { data } = await authClient.getSession();
      setSession(data);
    } catch (error) {
      console.error("Error fetching session:", error);
      setSession(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Only fetch once per app lifecycle
    if (hasFetchedRef.current) return;

    hasFetchedRef.current = true;
    fetchSession();
  }, []);

  const refreshSession = async () => {
    setIsLoading(true);
    await fetchSession();
  };

  return (
    <SessionContext.Provider value={{ session, isLoading, refreshSession }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error("useSession must be used within a SessionProvider");
  }
  return context;
}
