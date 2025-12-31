"use client";

/**
 * ChatInterface component using ChatKit React.
 *
 * Integrates with our FastAPI backend's ChatKit endpoint to provide
 * AI-powered task management through natural conversation.
 */

import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { authClient } from '@/lib/auth-client';
import { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { useChatTaskSync } from '@/hooks/useChatTaskSync';

export interface ChatInterfaceProps {
  /**
   * Optional conversation ID to continue an existing conversation
   */
  conversationId?: string;

  /**
   * Custom CSS class name
   */
  className?: string;
}

/**
 * ChatInterface component for AI-powered task management.
 *
 * Features:
 * - Natural language task creation
 * - Real-time streaming responses
 * - Conversation history
 * - Authenticated access
 *
 * @example
 * ```tsx
 * <ChatInterface
 *   conversationId="optional-uuid"
 *   className="h-[600px]"
 * />
 * ```
 */
export function ChatInterface({ conversationId, className }: ChatInterfaceProps) {
  const { toast } = useToast();
  const [isReady, setIsReady] = useState(false);

  // Automatically sync task data when chatbot makes changes
  // Uses on-demand revalidation via router.refresh()
  // No polling - Server Actions handle cache invalidation
  useChatTaskSync({
    refetchOnWindowFocus: true,
    refetchOnVisibilityChange: true,
  });

  // Custom fetch function that adds authentication headers
  const authenticatedFetch: typeof fetch = async (input, init) => {
    try {
      // Get JWT token from auth client
      const { data, error: authError } = await authClient.token();

      // Add authorization header if token exists
      const headers = new Headers(init?.headers);
      if (data?.token && !authError) {
        headers.set("Authorization", `Bearer ${data.token}`);
      }

      // Make the fetch request with auth headers
      return fetch(input, {
        ...init,
        headers,
        credentials: "include",
      });
    } catch (error) {
      console.error("Failed to add auth to ChatKit request:", error);
      // Fallback to regular fetch if auth fails
      return fetch(input, init);
    }
  };

  const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:9000";

  // Configure ChatKit with our backend endpoint
  const { control } = useChatKit({
    api: {
      url: `${BACKEND_URL}/api/v1/chatkit`,
      domainKey: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY!, // Required: verify registered domain
      fetch: authenticatedFetch,
    },

    onError: ({ error }) => {
      console.error('ChatKit error:', error);
      toast({
        title: "Chat Error",
        description: error.message || "An error occurred with the chat service.",
        variant: "destructive",
      });
    },
  });

  // Authentication check is handled by authenticatedFetch and isReady state
  useEffect(() => {
    async function checkAuth() {
      try {
        const { data, error: authError } = await authClient.token();

        if (authError || !data?.token) {
          toast({
            title: "Authentication Required",
            description: "Please sign in to use the chat feature.",
            variant: "destructive",
          });
          return;
        }

        setIsReady(true);
      } catch (err) {
        console.error('Auth check failed:', err);
        toast({
          title: "Authentication Error",
          description: "Failed to verify authentication. Please try signing in again.",
          variant: "destructive",
        });
      }
    }

    checkAuth();
  }, [toast]);

  if (!isReady) {
    return (
      <Card className={className}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading chat...</p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <div className={className}>
      <ChatKit
        control={control}
        className="h-full w-full"
      />
    </div>
  );
}
