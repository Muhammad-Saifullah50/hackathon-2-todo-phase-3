"use client"

import { motion } from "framer-motion"
import { ArrowRight, CheckCircle2, Calendar, Tags } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { fadeIn, slideIn, staggerContainer } from "@/lib/animations"

/**
 * Hero section with animated gradient background, headline, and floating task cards.
 * Features parallax effect and scroll-triggered animations.
 */
export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 dark:from-gray-900 dark:via-cyan-900/20 dark:to-teal-900/20">
      {/* Animated gradient background */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-cyan-500/10 to-teal-500/10 animate-gradient-x" />

      {/* Floating orbs */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-blue-400/30 rounded-full blur-3xl animate-float" />
      <div
        className="absolute bottom-20 right-10 w-96 h-96 bg-teal-400/20 rounded-full blur-3xl animate-float"
        style={{ animationDelay: "2s" }}
      />

      {/* Content */}
      <motion.div
        className="relative z-10 container mx-auto px-4 py-16 sm:px-6 lg:px-8"
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
      >
        <div className="max-w-4xl mx-auto text-center">
          {/* Headline */}
          <motion.h1
            className="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight mb-6"
            variants={slideIn}
          >
            <span className="bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600 bg-clip-text text-transparent">
              Task Management
            </span>
            <br />
            Made Beautiful
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            className="text-xl sm:text-2xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto"
            variants={fadeIn}
          >
            Stay organized, hit deadlines, and achieve more with TodoMore&apos;s
            intuitive interface and powerful features.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            className="flex flex-col sm:flex-row gap-4 justify-center mb-12"
            variants={fadeIn}
          >
            <Button size="lg" className="text-lg px-8 py-6" asChild>
              <Link href="/sign-up">
                Get Started Free
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>

            <Button
              size="lg"
              variant="outline"
              className="text-lg px-8 py-6"
              asChild
            >
              <Link href="#demo">See It In Action</Link>
            </Button>
          </motion.div>

          {/* Social Proof */}
          <motion.p
            className="text-sm text-gray-500 dark:text-gray-400"
            variants={fadeIn}
          >
            Trusted by 10,000+ productive teams worldwide
          </motion.p>
        </div>

        {/* Floating Task Cards */}
        <div className="hidden lg:block">
          {/* Card 1 */}
          <motion.div
            className="absolute top-32 left-16 bg-white dark:bg-gray-800 rounded-lg shadow-2xl p-4 w-72"
            initial={{ opacity: 0, x: -40 }}
            animate={{ opacity: 1, x: -16 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            whileHover={{ scale: 1.05 }}
          >
            <div className="flex items-start gap-3">
              <CheckCircle2 className="h-5 w-5 text-green-500 mt-0.5" />
              <div>
                <h3 className="font-semibold text-sm mb-1">
                  Launch marketing campaign
                </h3>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <Calendar className="h-3 w-3" />
                  <span>Completed today</span>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Card 2 */}
          <motion.div
            className="absolute top-48 right-20 bg-white dark:bg-gray-800 rounded-lg shadow-2xl p-4 w-72"
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 32 }}
            transition={{ delay: 0.7, duration: 0.6 }}
            whileHover={{ scale: 1.05 }}
          >
            <div className="flex items-start gap-3">
              <div className="h-5 w-5 rounded-full border-2 border-orange-500" />
              <div>
                <h3 className="font-semibold text-sm mb-1">
                  Review Q4 budget proposal
                </h3>
                <div className="flex items-center gap-2 text-xs text-orange-600">
                  <Calendar className="h-3 w-3" />
                  <span>Due tomorrow</span>
                </div>
                <div className="flex gap-1 mt-2 items-center">
                  <Tags className="h-3 w-3 text-gray-400" />
                  <span className="text-xs">Finance</span>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Card 3 */}
          <motion.div
            className="absolute bottom-32 left-24 bg-white dark:bg-gray-800 rounded-lg shadow-2xl p-4 w-72"
            initial={{ opacity: 0, x: -40, y: 20 }}
            animate={{ opacity: 1, x: -24, y: 20 }}
            transition={{ delay: 0.9, duration: 0.6 }}
            whileHover={{ scale: 1.05 }}
          >
            <h3 className="font-semibold text-sm mb-1">
              Prepare design mockups
            </h3>
            <div className="text-xs text-gray-500">Due in 5 days</div>
          </motion.div>
        </div>

        {/* Scroll Indicator */}
        <motion.div
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            delay: 1.2,
            duration: 0.6,
            repeat: Infinity,
            repeatType: "reverse",
          }}
        >
          <div className="w-6 h-10 border-2 border-gray-400 rounded-full flex justify-center p-2">
            <div className="w-1.5 h-2 bg-gray-400 rounded-full animate-bounce" />
          </div>
        </motion.div>
      </motion.div>
    </section>
  )
}
