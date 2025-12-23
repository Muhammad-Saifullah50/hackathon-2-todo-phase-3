import type { Metadata } from "next";
import { SignInForm } from "@/components/auth/SignInForm";

export const metadata: Metadata = {
  title: "Sign In",
  description: "Sign in to your Todoly account to manage your tasks",
};

export default function SignInPage() {
  return <SignInForm />;
}
