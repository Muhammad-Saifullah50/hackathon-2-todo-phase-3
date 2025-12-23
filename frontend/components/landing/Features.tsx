"use client";

import { motion } from "framer-motion";
import {
  Calendar,
  Tags,
  LayoutDashboard,
  Zap,
  Users,
  Shield,
  Smartphone,
  Palette,
} from "lucide-react";
import { scrollFadeIn, staggerContainer } from "@/lib/animations";

const features = [
  {
    icon: Calendar,
    title: "Smart Due Dates",
    description:
      "Visual indicators for overdue, due soon, and upcoming tasks. Never miss a deadline again.",
    color: "text-blue-600 dark:text-blue-400",
    bgColor: "bg-blue-100 dark:bg-blue-900/30",
  },
  {
    icon: Tags,
    title: "Color-Coded Tags",
    description:
      "Organize tasks with custom tags and colors. Filter and search with lightning speed.",
    color: "text-cyan-600 dark:text-cyan-400",
    bgColor: "bg-cyan-100 dark:bg-cyan-900/30",
  },
  {
    icon: LayoutDashboard,
    title: "Multiple Views",
    description:
      "Switch between List, Grid, Kanban, and Calendar views. Work the way you want.",
    color: "text-teal-600 dark:text-teal-400",
    bgColor: "bg-teal-100 dark:bg-teal-900/30",
  },
  {
    icon: Zap,
    title: "Keyboard Shortcuts",
    description:
      "Power-user features with command palette. Navigate and create tasks at lightning speed.",
    color: "text-yellow-600 dark:text-yellow-400",
    bgColor: "bg-yellow-100 dark:bg-yellow-900/30",
  },
  {
    icon: Users,
    title: "Subtasks & Progress",
    description:
      "Break down complex tasks into manageable steps. Track progress with visual indicators.",
    color: "text-green-600 dark:text-green-400",
    bgColor: "bg-green-100 dark:bg-green-900/30",
  },
  {
    icon: Shield,
    title: "Secure & Private",
    description:
      "Your data is encrypted and protected. SOC 2 compliant with enterprise-grade security.",
    color: "text-red-600 dark:text-red-400",
    bgColor: "bg-red-100 dark:bg-red-900/30",
  },
  {
    icon: Smartphone,
    title: "Mobile Optimized",
    description:
      "Swipe gestures, bottom navigation, and touch-friendly controls. Productivity on the go.",
    color: "text-indigo-600 dark:text-indigo-400",
    bgColor: "bg-indigo-100 dark:bg-indigo-900/30",
  },
  {
    icon: Palette,
    title: "Beautiful Themes",
    description:
      "Choose from 5 stunning themes. Dark mode included. Customize to match your style.",
    color: "text-orange-600 dark:text-orange-400",
    bgColor: "bg-orange-100 dark:bg-orange-900/30",
  },
];

/**
 * Features section showcasing key product capabilities.
 * Grid layout with icons, titles, descriptions, and hover effects.
 */
export default function Features() {
  return (
    <section id="features" className="py-24 bg-white dark:bg-gray-900">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center max-w-3xl mx-auto mb-16"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={scrollFadeIn}
        >
          <h2 className="text-4xl sm:text-5xl font-bold tracking-tight mb-4">
            Everything you need to stay organized
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            Powerful features designed to help you and your team accomplish more, faster.
          </p>
        </motion.div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8"
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
        >
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                className="group relative"
                variants={scrollFadeIn}
                whileHover={{ y: -8 }}
                transition={{ duration: 0.3 }}
              >
                <div className="h-full p-6 rounded-2xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 transition-all duration-300 hover:shadow-xl">
                  {/* Icon */}
                  <div className={`inline-flex p-3 rounded-xl ${feature.bgColor} mb-4`}>
                    <Icon className={`h-6 w-6 ${feature.color}`} />
                  </div>

                  {/* Title */}
                  <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
                    {feature.title}
                  </h3>

                  {/* Description */}
                  <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                    {feature.description}
                  </p>

                  {/* Hover effect gradient */}
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-500/5 via-cyan-500/5 to-teal-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10" />
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
