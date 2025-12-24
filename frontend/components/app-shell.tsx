import { Sidebar } from "@/components/sidebar/Sidebar";
import { ChatWidget } from "@/components/features/chat/chat-widget";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Sidebar />
      <main className="md:ml-56 max-h-[80vh]">
        {children}
      </main>
      <ChatWidget />
    </>
  );
}
