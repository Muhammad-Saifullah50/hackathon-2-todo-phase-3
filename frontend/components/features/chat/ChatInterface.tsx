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

  // Configure ChatKit with our backend endpoint
  const { control, error } = useChatKit({
    api: {
      async makeRequest(path, options) {
        // Get authentication token
        const { data, error: authError } = await authClient.token();

        if (authError || !data?.token) {
          throw new Error('Authentication failed. Please sign in.');
        }

        const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        // Make request to our ChatKit endpoint
        const response = await fetch(`${baseURL}/api/v1/chatkit`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${data.token}`,
            ...options?.headers,
          },
          credentials: 'include',
          body: options?.body,
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || errorData.error || `HTTP error! status: ${response.status}`);
        }

        return response;
      },
    },

    // Optional: Add conversation context
    initialMessages: conversationId ? [] : undefined,

    // Branding and customization
    appearance: {
      theme: 'auto', // Follow system theme
    },
  });

  // Handle authentication check on mount
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

  // Handle ChatKit errors
  useEffect(() => {
    if (error) {
      console.error('ChatKit error:', error);
      toast({
        title: "Chat Error",
        description: error.message || "An error occurred with the chat service.",
        variant: "destructive",
      });
    }
  }, [error, toast]);

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
