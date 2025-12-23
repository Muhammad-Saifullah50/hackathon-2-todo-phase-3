"use client";

import { motion } from "framer-motion";
import { Check, Sparkles } from "lucide-react";
import Link from "next/link";
import { scrollFadeIn, scaleIn } from "@/lib/animations";
import { Button } from "@/components/ui/button";

const plans = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Perfect for individuals getting started",
    features: [
      "Up to 100 tasks",
      "List and Grid views",
      "Basic tags (up to 10)",
      "Due dates with reminders",
      "Mobile app access",
      "Community support",
    ],
    cta: "Get Started Free",
    href: "/sign-up",
    popular: false,
  },
  {
    name: "Premium",
    price: "$9",
    period: "per month",
    description: "For power users and teams",
    features: [
      "Unlimited tasks",
      "All views (List, Grid, Kanban, Calendar)",
      "Unlimited custom tags",
      "Priority support",
      "Subtasks and templates",
      "Recurring tasks",
      "Advanced keyboard shortcuts",
      "Team collaboration (coming soon)",
      "Custom themes and branding",
    ],
    cta: "Start 14-Day Free Trial",
    href: "/sign-up?plan=premium",
    popular: true,
  },
];

/**
 * Pricing section with Free and Premium tier comparison.
 * Features list, CTA buttons, and popular badge.
 */
export default function Pricing() {
  return (
    <section id="pricing" className="py-24 bg-gray-50 dark:bg-gray-800">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center max-w-3xl mx-auto mb-16"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={scrollFadeIn}
        >
          <h2 className="text-4xl sm:text-5xl font-bold tracking-tight mb-4">
            Simple, transparent pricing
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            Start for free, upgrade when you&apos;re ready. No hidden fees, cancel anytime.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              className="relative"
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              variants={scaleIn}
              custom={index}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 z-10">
                  <div className="flex items-center gap-1 bg-gradient-to-r from-blue-500 via-cyan-500 to-teal-500 text-white px-4 py-1.5 rounded-full text-sm font-semibold shadow-lg">
                    <Sparkles className="h-4 w-4" />
                    Most Popular
                  </div>
                </div>
              )}

              <div
                className={`h-full p-8 rounded-2xl bg-white dark:bg-gray-900 border-2 transition-all hover:shadow-2xl ${
                  plan.popular
                    ? "border-teal-500 shadow-xl scale-105"
                    : "border-gray-200 dark:border-gray-700"
                }`}
              >
                {/* Plan Name */}
                <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                  {plan.name}
                </h3>

                {/* Description */}
                <p className="text-gray-600 dark:text-gray-400 mb-6">{plan.description}</p>

                {/* Price */}
                <div className="mb-6">
                  <div className="flex items-baseline gap-2">
                    <span className="text-5xl font-extrabold text-gray-900 dark:text-gray-100">
                      {plan.price}
                    </span>
                    <span className="text-gray-600 dark:text-gray-400">/ {plan.period}</span>
                  </div>
                </div>

                {/* CTA Button */}
                <Button
                  size="lg"
                  className="w-full mb-8"
                  variant={plan.popular ? "default" : "outline"}
                  asChild
                >
                  <Link href={plan.href}>{plan.cta}</Link>
                </Button>

                {/* Features */}
                <div className="space-y-4">
                  <p className="text-sm font-semibold text-gray-900 dark:text-gray-100 uppercase tracking-wide">
                    What&apos;s included:
                  </p>
                  <ul className="space-y-3">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-3">
                        <Check className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <span className="text-gray-700 dark:text-gray-300">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* FAQ Link */}
        <motion.div
          className="text-center mt-12"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={scrollFadeIn}
        >
          <p className="text-gray-600 dark:text-gray-400">
            Have questions?{" "}
            <Link href="#faq" className="text-teal-600 hover:text-teal-700 font-medium">
              Check out our FAQ
            </Link>{" "}
            or{" "}
            <Link href="/contact" className="text-teal-600 hover:text-teal-700 font-medium">
              contact support
            </Link>
          </p>
        </motion.div>
      </div>
    </section>
  );
}
