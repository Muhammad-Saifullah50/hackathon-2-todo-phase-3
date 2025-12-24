"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { LayoutDashboard } from "lucide-react";
import { useSession } from "@/components/session-provider";

export default function Navbar() {
  const { session, isLoading } = useSession();
  const pathname = usePathname();

  // Check if we're on the landing page
  const isLandingPage = pathname === "/";

  return (
    <nav className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-4 py-3 flex items-center justify-between">
      <Link href={session ? "/tasks" : "/"} className="text-xl font-bold md:ml-0 ml-10">
        Todoly
      </Link>
      <div className="flex items-center gap-4">
        {!isLoading && (
          <>
            {session && isLandingPage && (
              <Button asChild>
                <Link href="/tasks" className="flex items-center gap-2">
                  <LayoutDashboard className="h-4 w-4" />
                  Dashboard
                </Link>
              </Button>
            )}
            {!session && (
              <>
                <Button variant="ghost" asChild>
                  <Link href="/sign-in">Login</Link>
                </Button>
                <Button asChild>
                  <Link href="/sign-up">Sign Up</Link>
                </Button>
              </>
            )}
          </>
        )}
      </div>
    </nav>
  );
}
