import type { Metadata } from "next";
import { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Settings",
  description: "Manage your account settings, preferences, and task templates",
};

export default function SettingsLayout({ children }: { children: ReactNode }) {
  return children;
}
