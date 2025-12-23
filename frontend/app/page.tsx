import Hero from "@/components/landing/Hero";
import Features from "@/components/landing/Features";
import Demo from "@/components/landing/Demo";
import Testimonials from "@/components/landing/Testimonials";
import Pricing from "@/components/landing/Pricing";
import { CTA } from "@/components/landing/CTA";
import { Footer } from "@/components/landing/Footer";
import type { Metadata } from "next";

/**
 * SEO Metadata for landing page
 */
export const metadata: Metadata = {
  title: "Beautiful Task Management for Everyone",
  description:
    "Transform your productivity with Todoly's beautiful, intuitive task manager. Features include due dates, tags, subtasks, recurring tasks, kanban boards, and more. Free forever plan available.",
  keywords: [
    "task management",
    "todo list",
    "productivity",
    "kanban board",
    "project management",
    "task organizer",
    "free task manager",
    "todoly",
  ],
  openGraph: {
    title: "Todoly - Beautiful Task Management for Everyone",
    description:
      "Transform your productivity with Todoly's beautiful, intuitive task manager. Free forever plan available.",
    url: "/",
    siteName: "Todoly",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Todoly - Task Management Dashboard",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Todoly - Beautiful Task Management for Everyone",
    description:
      "Transform your productivity with Todoly's beautiful, intuitive task manager. Free forever plan available.",
    images: ["/og-image.png"],
    creator: "@todoly",
  },
  verification: {
    google: "google-site-verification-code",
  },
};

/**
 * Landing Page - Main entry point for new visitors
 *
 * Structure:
 * 1. Hero - Animated hero section with headline and CTA
 * 2. Features - 6+ feature cards with icons and descriptions
 * 3. Demo - Interactive product demo with tabbed navigation
 * 4. Testimonials - Rotating user testimonials
 * 5. Pricing - Free/Premium tier comparison
 * 6. CTA - Final call-to-action
 * 7. Footer - Navigation links and social icons
 *
 * All sections use scroll-triggered animations via Framer Motion
 * Responsive breakpoints: mobile (320px-767px), tablet (768px-1024px), desktop (1920px+)
 */
export default function LandingPage() {
  return (
    <main className="min-h-screen bg-background">
      {/* Hero Section */}
      <Hero />

      {/* Features Section */}
      <Features />

      {/* Interactive Demo Section */}
      <Demo />

      {/* Testimonials Section */}
      <Testimonials />

      {/* Pricing Section */}
      <Pricing />

      {/* Final CTA Section */}
      <CTA />

      {/* Footer */}
      <Footer />
    </main>
  );
}
