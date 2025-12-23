"use client";

import { useRouter } from "next/navigation";
import { authClient } from "@/lib/auth-client";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { LogOut } from "lucide-react";
import { cn } from "@/lib/utils";

interface LogoutButtonProps {
  isCollapsed: boolean;
}

export function LogoutButton({ isCollapsed }: LogoutButtonProps) {
  const router = useRouter();

  const handleSignOut = async () => {
    await authClient.signOut({
      fetchOptions: {
        onSuccess: () => {
          router.push("/");
        },
      },
    });
  };

  const buttonContent = (
    <Button
      variant="ghost"
      size="sm"
      className={cn(
        "w-full flex items-center gap-3 justify-start text-muted-foreground hover:text-destructive hover:bg-destructive/10 px-3 py-2",
        isCollapsed && "justify-center px-2"
      )}
      onClick={handleSignOut}
    >
      <LogOut className="h-5 w-5 flex-shrink-0" />
      {!isCollapsed && <span className="text-sm">Logout</span>}
    </Button>
  );

  if (isCollapsed) {
    return (
      <Tooltip delayDuration={0}>
        <TooltipTrigger asChild>{buttonContent}</TooltipTrigger>
        <TooltipContent side="right" className="font-medium">
          Logout
        </TooltipContent>
      </Tooltip>
    );
  }

  return buttonContent;
}
