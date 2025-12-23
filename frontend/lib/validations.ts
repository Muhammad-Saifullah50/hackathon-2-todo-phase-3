import { z } from 'zod';

/**
 * Shared validation schemas using Zod.
 * These schemas will be populated as features (Auth, Tasks) are implemented.
 */

// Example placeholder schema
export const placeholderSchema = z.object({
  id: z.string().uuid(),
});
