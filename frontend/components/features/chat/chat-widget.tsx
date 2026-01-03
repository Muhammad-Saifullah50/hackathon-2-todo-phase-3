"use client";

import { useState, useEffect } from "react";
import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { X, MessageCircle } from "lucide-react";
import { authClient } from "@/lib/auth-client";
import { useChatTaskSync } from "@/hooks/useChatTaskSync";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:9000";
const DOMAIN_KEY = process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || "todomore-app";

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [pendingMessage, setPendingMessage] = useState<string | null>(null);

  // Get the revalidation function directly
  const { revalidateTasks } = useChatTaskSync({
    refetchOnWindowFocus: false,
    refetchOnVisibilityChange: false,
  });

  // Listen for custom revalidation event from backend
  useEffect(() => {
    const handleRevalidate = () => {
      console.log('📢 [ChatWidget] Received revalidation event from backend');
      revalidateTasks();
    };

    window.addEventListener('chatkit:revalidate', handleRevalidate);
    return () => window.removeEventListener('chatkit:revalidate', handleRevalidate);
  }, [revalidateTasks]);

  // Custom fetch function that adds authentication headers
  const authenticatedFetch: typeof fetch = async (input, init) => {
    try {
      // Get JWT token from Better Auth
      const { data, error } = await authClient.token();

      // Add authorization header if token exists
      const headers = new Headers(init?.headers);
      if (data?.token && !error) {
        headers.set("Authorization", `Bearer ${data.token}`);
      }

      // Make the fetch request with auth headers
      return fetch(input, {
        ...init,
        headers,
        credentials: "include", // Include cookies
      });
    } catch (error) {
      console.error("Failed to add auth to ChatKit request:", error);
      // Fallback to regular fetch if auth fails
      return fetch(input, init);
    }
  };

  let control, sendUserMessage;
  try {
    const result = useChatKit({
      api: {
        url: `${BACKEND_URL}/chatkit`,
        domainKey: DOMAIN_KEY,
        fetch: authenticatedFetch, // Use custom fetch with auth
      },
    // Save thread ID when it changes
    onThreadChange: ({ threadId }) => {
      if (typeof window !== "undefined") {
        if (threadId) {
          localStorage.setItem("chatkit_last_thread_id", threadId);
        } else {
          localStorage.removeItem("chatkit_last_thread_id");
        }
      }
    },
    // Trigger instant revalidation when response ends (task operations complete)
    onResponseEnd: () => {
      console.log('⏹️⏹️⏹️ [ChatWidget] ===== RESPONSE ENDED - TRIGGERING REVALIDATION =====');

      // Call immediately
      revalidateTasks().then(() => {
        console.log('✅ [ChatWidget] Immediate revalidation completed');
      });

      // Also trigger after delay to catch async database commits
      setTimeout(() => {
        console.log('🔄 [ChatWidget] Delayed revalidation (1s)');
        revalidateTasks();
      }, 1000);
    },
    theme: {
      colorScheme: "light",
      color: {
        accent: {
          primary: "#3b82f6", // Blue-500
          level: 2,
        },
      },
      radius: "round",
      density: "normal",
      typography: { fontFamily: "system-ui, sans-serif" },
    },
    header: {
      enabled: true,
    },
    history: {
      enabled: true,
      showDelete: true,
      showRename: true,
    },
    startScreen: {
      greeting: "Hi! I'm your TodoBot - Task Management Assistant.",
      prompts: [
        {
          label: "Create Task",
          prompt: "Add a task to buy groceries",
          icon: "agent",
        },
        {
          label: "List Tasks",
          prompt: "Show me my pending tasks",
          icon: "search",
        },
        {
          label: "High Priority",
          prompt: "Create a high priority task to finish the report by Friday",
          icon: "bolt",
        },
      ],
    },
    composer: {
      placeholder: "Ask me to create, list, or manage tasks...",
    },
    });
    control = result.control;
    sendUserMessage = result.sendUserMessage;
  } catch (error) {
    console.error("[ChatWidget] Failed to initialize:", error);
    // Return minimal UI if ChatKit fails to initialize
    return (
      <div className="fixed bottom-4 right-4 z-50 p-4 bg-red-500 text-white rounded-lg">
        ChatKit failed to load
      </div>
    );
  }

  // Expose global handler for potential external triggers
  useEffect(() => {
    if (typeof window !== "undefined") {
      (window as any).openTaskChat = (text?: string) => {
        if (text) {
          setPendingMessage(text);
        }
        setIsOpen(true);
      };
    }
  }, []);

  // Send pending message when chat opens
  useEffect(() => {
    if (isOpen && pendingMessage && sendUserMessage) {
      // Wait a bit for ChatKit to be ready
      const timer = setTimeout(() => {
        sendUserMessage({ text: pendingMessage });
        setPendingMessage(null);
      }, 100);

      return () => clearTimeout(timer);
    }
  }, [isOpen, pendingMessage, sendUserMessage]);

  // CRITICAL: Manually call setOptions when chat opens
  // The React wrapper doesn't always call it automatically
  useEffect(() => {
    if (isOpen && control?.options) {
      setTimeout(() => {
        const chatkitEl = document.querySelector("openai-chatkit") as any;
        if (chatkitEl && typeof chatkitEl.setOptions === "function") {
          chatkitEl.setOptions(control.options);
        }
      }, 100);
    }
  }, [isOpen, control]);

  // Closed state - show floating button
  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 z-50 w-14 h-14 rounded-full shadow-2xl flex items-center justify-center transition-all hover:scale-105 bg-blue-600 hover:bg-blue-500 shadow-blue-600/25"
        aria-label="Open chat"
      >
        <MessageCircle className="w-6 h-6 text-white" />
      </button>
    );
  }

  // Open state - show full chat widget
  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Close Button */}
      <button
        onClick={() => setIsOpen(false)}
        className="absolute -top-10 right-0 w-8 h-8 rounded-full flex items-center justify-center transition-colors shadow-lg focus:outline-none bg-blue-600 hover:bg-blue-500 text-gray-300 hover:text-white"
        aria-label="Close chat"
      >
        <X className="w-4 h-4" />
      </button>

      {/* Chat Widget */}
      <div className="w-[400px] h-[600px] shadow-2xl rounded-xl overflow-hidden">
        {/* ChatKit Content - no extra wrapper, ChatKit handles its own styling */}
        <ChatKit control={control} className="h-full w-full" />
      </div>
    </div>
  );
}
