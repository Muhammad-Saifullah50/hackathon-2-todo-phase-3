import { revalidatePath, revalidateTag } from 'next/cache';
import { NextRequest, NextResponse } from 'next/server';

/**
 * API Route for on-demand revalidation of task data.
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
    revalidatePath('/tasks', 'page');
    revalidatePath('/tasks/dashboard', 'page');
    revalidatePath('/tasks/kanban', 'page');
    revalidatePath('/tasks/calendar', 'page');
    revalidatePath('/tasks/trash', 'page');

    // Revalidate cache tags (use "max" for Next.js 16 behavior)
    revalidateTag('tasks', 'max');
    revalidateTag('analytics', 'max');

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
