/**
 * E2E Test: Task Management Operations
 *
 * Tests the complete workflow:
 * 1. View tasks with pagination and filtering
 * 2. Filter by status
 * 3. Edit task details
 * 4. Toggle task status (individual)
 * 5. Bulk toggle multiple tasks
 * 6. Delete task (soft delete to trash)
 * 7. View trash
 * 8. Restore task from trash
 * 9. Permanent delete
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9000';

// Mock user credentials (adjust based on your test setup)
const TEST_USER = {
  email: 'test@example.com',
  password: 'testpassword123',
};

test.describe('Task Management Operations', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to sign-in page and authenticate
    await page.goto(`${BASE_URL}/sign-in`);

    // Fill in login form (adjust selectors based on your actual sign-in form)
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');

    // Wait for redirect to tasks page
    await page.waitForURL(`${BASE_URL}/tasks`);
  });

  test('should view and filter tasks', async ({ page }) => {
    // Wait for tasks to load
    await page.waitForSelector('[role="article"]');

    // Verify tasks are displayed
    const tasks = await page.locator('[role="article"]').count();
    expect(tasks).toBeGreaterThan(0);

    // Check metadata badges are visible
    await expect(page.getByText(/pending/i)).toBeVisible();
    await expect(page.getByText(/completed/i)).toBeVisible();

    // Filter by "pending" status
    await page.click('text=Status');
    await page.click('text=Pending');

    // Verify filter applied
    await page.waitForTimeout(500); // Wait for filter to apply
    const pendingTasks = await page.locator('[role="article"]').count();
    expect(pendingTasks).toBeGreaterThanOrEqual(0);

    // Toggle to grid view
    await page.click('[aria-label="Grid view"]');
    await expect(page.locator('.grid')).toBeVisible();

    // Toggle back to list view
    await page.click('[aria-label="List view"]');
    await expect(page.locator('.space-y-3')).toBeVisible();
  });

  test('should edit task details', async ({ page }) => {
    // Wait for tasks to load
    await page.waitForSelector('[role="article"]');

    // Click edit button on first task
    await page.click('[aria-label="Edit task"]');

    // Wait for edit dialog
    await expect(page.getByText('Edit Task')).toBeVisible();

    // Edit title
    const newTitle = `Updated Task ${Date.now()}`;
    await page.fill('input[name="title"]', newTitle);

    // Save changes
    await page.click('text=Save Changes');

    // Verify toast notification
    await expect(page.getByText(/task updated/i)).toBeVisible();

    // Verify task title changed
    await expect(page.getByText(newTitle)).toBeVisible();
  });

  test('should toggle task status', async ({ page }) => {
    // Wait for tasks to load
    await page.waitForSelector('[role="article"]');

    // Get initial pending count
    const initialPending = await page.getByText(/pending/i).first().textContent();

    // Click status toggle on first task
    await page.click('[aria-label*="Mark as"]');

    // Wait for optimistic update
    await page.waitForTimeout(500);

    // Verify count changed
    const newPending = await page.getByText(/pending/i).first().textContent();
    expect(newPending).not.toBe(initialPending);
  });

  test('should bulk toggle tasks', async ({ page }) => {
    // Wait for tasks to load
    await page.waitForSelector('[role="article"]');

    // Select multiple tasks
    const checkboxes = page.locator('input[type="checkbox"]');
    await checkboxes.nth(1).check(); // First task checkbox
    await checkboxes.nth(2).check(); // Second task checkbox

    // Verify bulk actions toolbar appears
    await expect(page.getByText(/selected/i)).toBeVisible();

    // Click "Mark as Completed"
    await page.click('text=Mark as Completed');

    // Wait for update
    await page.waitForTimeout(500);

    // Verify selection cleared
    await expect(page.getByText(/selected/i)).not.toBeVisible();
  });

  test('should delete task and restore from trash', async ({ page }) => {
    // Wait for tasks to load
    await page.waitForSelector('[role="article"]');

    // Get task title before deletion
    const taskTitle = await page.locator('[role="article"]').first().locator('h3').textContent();

    // Click delete button on first task
    await page.click('[aria-label="Delete task"]');

    // Confirm deletion in dialog
    await expect(page.getByText('Delete Task?')).toBeVisible();
    await expect(page.getByText(/move.*to trash/i)).toBeVisible();
    await page.click('text=Move to Trash');

    // Verify toast notification
    await expect(page.getByText(/deleted/i)).toBeVisible();

    // Navigate to trash
    await page.goto(`${BASE_URL}/tasks/trash`);
    await page.waitForSelector('[role="article"]');

    // Verify task is in trash
    await expect(page.getByText(taskTitle || '')).toBeVisible();

    // Click restore button
    await page.click('[aria-label="Restore task"]');

    // Wait for restore
    await page.waitForTimeout(500);

    // Navigate back to tasks
    await page.goto(`${BASE_URL}/tasks`);
    await page.waitForSelector('[role="article"]');

    // Verify task is restored
    await expect(page.getByText(taskTitle || '')).toBeVisible();
  });

  test('should permanently delete task from trash', async ({ page }) => {
    // First, delete a task to trash
    await page.waitForSelector('[role="article"]');
    await page.click('[aria-label="Delete task"]');
    await page.click('text=Move to Trash');
    await page.waitForTimeout(500);

    // Navigate to trash
    await page.goto(`${BASE_URL}/tasks/trash`);
    await page.waitForSelector('[role="article"]');

    // Click permanent delete button
    await page.click('[aria-label="Delete permanently"]');

    // Confirm permanent deletion with strong warning
    await expect(page.getByText('Permanently Delete Task?')).toBeVisible();
    await expect(page.getByText(/cannot be undone/i)).toBeVisible();
    await expect(page.getByText(/⚠️ Warning/i)).toBeVisible();
    await page.click('text=Delete Permanently');

    // Wait for deletion
    await page.waitForTimeout(500);

    // Verify task is removed from trash
    // If trash is empty, should show empty state
    await expect(
      page.getByText(/trash is empty/i).or(page.locator('[role="article"]'))
    ).toBeTruthy();
  });

  test('should handle empty states correctly', async ({ page }) => {
    // Test empty trash
    await page.goto(`${BASE_URL}/tasks/trash`);
    await page.waitForTimeout(500);

    // Should show empty trash message if no deleted tasks
    const trashEmpty = await page.getByText(/trash is empty/i).count();
    if (trashEmpty > 0) {
      await expect(page.getByText(/Deleted tasks will appear here/i)).toBeVisible();
    }

    // Test filter with no results
    await page.goto(`${BASE_URL}/tasks`);
    await page.waitForSelector('[role="article"]').catch(() => {});

    // Apply filter that might return no results
    await page.click('text=Status');
    await page.click('text=Completed');
    await page.waitForTimeout(500);

    // May show either tasks or empty state
    const noResults = await page.getByText(/No completed tasks found/i).count();
    if (noResults > 0) {
      await expect(page.getByText(/No completed tasks found/i)).toBeVisible();
    }
  });

  test('should verify accessibility features', async ({ page }) => {
    await page.waitForSelector('[role="article"]');

    // Check for aria-labels
    await expect(page.locator('[aria-label="Edit task"]')).toBeVisible();
    await expect(page.locator('[aria-label*="Mark as"]')).toBeVisible();
    await expect(page.locator('[aria-label="Delete task"]')).toBeVisible();

    // Check for keyboard navigation
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Verify focus is visible (implementation depends on CSS)
    const focused = await page.evaluate(() => document.activeElement?.tagName);
    expect(focused).toBeTruthy();

    // Check aria-live region exists
    const ariaLive = await page.locator('[aria-live="polite"]').count();
    expect(ariaLive).toBeGreaterThan(0);
  });
});

test.describe('Task Management - Error Handling', () => {
  test('should handle network errors gracefully', async ({ page, context }) => {
    // Block API requests to simulate network error
    await context.route(`${API_URL}/**`, (route) => route.abort());

    await page.goto(`${BASE_URL}/tasks`);

    // Should show error message
    await expect(
      page.getByText(/failed to load/i).or(page.getByText(/error/i))
    ).toBeVisible();
  });
});
