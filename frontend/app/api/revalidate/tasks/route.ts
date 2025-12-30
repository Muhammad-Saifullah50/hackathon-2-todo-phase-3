import { revalidatePath, revalidateTag } from 'next/cache';
import { NextRequest, NextResponse } from 'next/server';

// Type-safe wrappers for Next.js revalidation functions
const _revalidatePath = revalidatePath as (path: string, type?: 'page' | 'layout') => void;
const _revalidateTag = revalidateTag as (tag: string, maxAge?: number) => void;

/**
 * API Route for on-demand revalidation of task data.
 * Called by the backend chatbot after it makes changes to tasks.
 *
 * Usage from backend:
 * POST /api/revalidate/tasks
 * {
 *   "action": "create" | "update" | "delete" | "restore"
 * }
 *
 * This will trigger Next.js to revalidate the tasks cache.
 */

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action } = body;

    // Revalidate all task-related paths
    _revalidatePath('/tasks', 'page');
    _revalidatePath('/tasks/dashboard', 'page');
    _revalidatePath('/tasks/kanban', 'page');
    _revalidatePath('/tasks/calendar', 'page');
    _revalidatePath('/tasks/trash', 'page');

    // Revalidate cache tags with maxAge for deprecation warning fix
    _revalidateTag('tasks', 0);
    _revalidateTag('analytics', 0);

    console.log(`[Revalidate API] Revalidated tasks cache after action: ${action}`);

    return NextResponse.json({
      success: true,
      message: `Cache revalidated after ${action}`,
      revalidatedPaths: [
        '/tasks',
        '/tasks/dashboard',
        '/tasks/kanban',
        '/tasks/calendar',
        '/tasks/trash',
      ],
    });
  } catch (error) {
    console.error('[Revalidate API] Error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to revalidate cache' },
      { status: 500 }
    );
  }
}
