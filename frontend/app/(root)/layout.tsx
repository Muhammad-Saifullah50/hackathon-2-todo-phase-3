import { AppShell } from "@/components/app-shell";

export default function RootGroupLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AppShell>{children}</AppShell>;
}
