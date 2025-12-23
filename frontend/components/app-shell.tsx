import { Sidebar } from "@/components/sidebar/Sidebar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Sidebar />
      <main className="md:ml-56 min-h-screen">
        {children}
      </main>
    </>
  );
}
