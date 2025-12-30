"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, Quote, Star } from "lucide-react";
import { fadeIn } from "@/lib/animations";
import { Button } from "@/components/ui/button";

const testimonials = [
  {
    id: 1,
    name: "Sarah Johnson",
    role: "Product Manager",
    company: "TechCorp",
    avatar: "SJ",
    content:
      "TodoMore has completely transformed how our team manages projects. The visual indicators and multiple views make it so easy to stay on top of everything.",
    rating: 5,
  },
  {
    id: 2,
    name: "Michael Chen",
    role: "Freelance Designer",
    company: "Independent",
    avatar: "MC",
    content:
      "As a freelancer juggling multiple clients, TodoMore's tag system and calendar view are game-changers. I never miss a deadline anymore!",
    rating: 5,
  },
  {
    id: 3,
    name: "Emily Rodriguez",
    role: "Engineering Lead",
    company: "StartupXYZ",
    avatar: "ER",
    content:
      "The keyboard shortcuts and command palette make me feel like a productivity superhero. Our team's efficiency has increased by 40% since switching to TodoMore.",
    rating: 5,
  },
  {
    id: 4,
    name: "David Park",
    role: "Marketing Director",
    company: "GrowthCo",
    avatar: "DP",
    content:
      "Beautiful design meets powerful functionality. TodoMore is the only task manager that my entire team actually enjoys using. The animations are a nice touch!",
    rating: 5,
  },
];

/**
 * Testimonials section with rotating customer quotes.
 * Features avatar images, ratings, and auto-rotate carousel.
 */
export default function Testimonials() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [direction, setDirection] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setDirection(1);
      setCurrentIndex((prev) => (prev + 1) % testimonials.length);
    }, 5000);

    return () => clearInterval(timer);
  }, []);

  const handlePrevious = () => {
    setDirection(-1);
    setCurrentIndex((prev) => (prev - 1 + testimonials.length) % testimonials.length);
  };

  const handleNext = () => {
    setDirection(1);
    setCurrentIndex((prev) => (prev + 1) % testimonials.length);
  };

  const currentTestimonial = testimonials[currentIndex];

  return (
    <section className="py-24 bg-white dark:bg-gray-900 overflow-hidden">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center max-w-3xl mx-auto mb-16"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={fadeIn}
        >
          <h2 className="text-4xl sm:text-5xl font-bold tracking-tight mb-4">
            Loved by thousands of users
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            Join the community of productive teams and individuals who trust TodoMore.
          </p>
        </motion.div>

        <div className="max-w-4xl mx-auto">
          <div className="relative">
            {/* Quote Icon */}
            <div className="absolute -top-6 -left-6 text-gray-200 dark:text-gray-700 opacity-50">
              <Quote className="h-24 w-24" fill="currentColor" />
            </div>

            {/* Testimonial Card */}
            <div className="relative bg-gray-50 dark:bg-gray-800 rounded-2xl p-8 sm:p-12 border border-gray-200 dark:border-gray-700 shadow-xl min-h-[320px] flex flex-col justify-between">
              <AnimatePresence mode="wait" custom={direction}>
                <motion.div
                  key={currentTestimonial.id}
                  custom={direction}
                  initial={{ opacity: 0, x: direction > 0 ? 100 : -100 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: direction > 0 ? -100 : 100 }}
                  transition={{ duration: 0.3 }}
                  className="flex flex-col h-full"
                >
                  {/* Rating */}
                  <div className="flex gap-1 mb-6">
                    {Array.from({ length: currentTestimonial.rating }).map((_, i) => (
                      <Star
                        key={i}
                        className="h-5 w-5 fill-yellow-400 text-yellow-400"
                      />
                    ))}
                  </div>

                  {/* Content */}
                  <blockquote className="text-xl sm:text-2xl text-gray-900 dark:text-gray-100 font-medium mb-8 flex-1">
                    &ldquo;{currentTestimonial.content}&rdquo;
                  </blockquote>

                  {/* Author */}
                  <div className="flex items-center gap-4">
                    <div className="flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 via-cyan-500 to-teal-500 flex items-center justify-center text-white font-semibold">
                      {currentTestimonial.avatar}
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900 dark:text-gray-100">
                        {currentTestimonial.name}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        {currentTestimonial.role} at {currentTestimonial.company}
                      </div>
                    </div>
                  </div>
                </motion.div>
              </AnimatePresence>
            </div>

            {/* Navigation */}
            <div className="flex items-center justify-center gap-4 mt-8">
              <Button
                variant="outline"
                size="icon"
                onClick={handlePrevious}
                className="rounded-full"
                aria-label="Previous testimonial"
              >
                <ChevronLeft className="h-5 w-5" />
              </Button>

              {/* Indicators */}
              <div className="flex gap-2">
                {testimonials.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setDirection(index > currentIndex ? 1 : -1);
                      setCurrentIndex(index);
                    }}
                    className={`w-2 h-2 rounded-full transition-all ${
                      index === currentIndex
                        ? "bg-teal-500 w-8"
                        : "bg-gray-300 dark:bg-gray-600"
                    }`}
                    aria-label={`Go to testimonial ${index + 1}`}
                  />
                ))}
              </div>

              <Button
                variant="outline"
                size="icon"
                onClick={handleNext}
                className="rounded-full"
                aria-label="Next testimonial"
              >
                <ChevronRight className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
