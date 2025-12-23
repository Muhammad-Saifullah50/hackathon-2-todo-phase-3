import type { Metadata } from "next";
import { SignUpForm } from "@/components/auth/SignUpForm";

export const metadata: Metadata = {
  title: "Sign Up",
  description: "Create a new Todoly account and start organizing your tasks",
};

export default function SignUpPage() {
  return <SignUpForm />;
}
