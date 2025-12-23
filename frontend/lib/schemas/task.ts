/**
 * Zod validation schemas for task-related forms.
 * Mirrors backend validation rules for consistent UX.
 */

import { z } from 'zod';

/**
 * Validation schema for creating a new task.
 * Matches backend validation rules:
 * - Title: 1-100 characters AND 1-50 words
 * - Description: 0-500 characters (optional)
 * - Priority: LOW, MEDIUM, or HIGH (optional, defaults to MEDIUM)
 * - Due date: Optional date (ISO string or null)
 */
export const createTaskSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(100, "Title must be 100 characters or less")
    .refine(
      (val) => {
        const words = val.trim().split(/\s+/);
        return words.length <= 50;
      },
      { message: "Title must be 50 words or less" }
    ),

  description: z
    .string()
    .max(500, "Description must be 500 characters or less")
    .nullable()
    .transform((val) => {
      // Convert empty string to null
      if (val === "" || val === null) return null;
      return val.trim() || null;
    }),

  priority: z.enum(["low", "medium", "high"]).optional(),

  due_date: z
    .string()
    .nullable()
    .transform((val) => {
      if (!val || val === "") return null;
      return val;
    }),
});

/**
 * Infer TypeScript type from the Zod schema.
 * Use this type for form data in React Hook Form.
 */
export type CreateTaskFormData = z.infer<typeof createTaskSchema>;
