import { Sidebar } from "@/components/sidebar/Sidebar";
import { ChatWidget } from "@/components/features/chat/chat-widget";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Sidebar />
      <main className="md:ml-56 min-h-screen">
        {children}
      </main>
      <ChatWidget />
    </>
  );
}
