# Gemini CLI Rules - Todo Frontend

Guidelines for working on the Next.js frontend of the Todo application.

## Tech Stack

- **Framework:** Next.js 15 (App Router)
- **Library:** React 19
- **Styling:** Tailwind CSS 4, Lucide React (icons)
- **Data Fetching:** TanStack Query (v5), Axios
- **UI Components:** Radix UI primitives, shadcn/ui patterns
- **Testing:** Vitest, React Testing Library

## Development Guidelines

### 1. Component Standards

- Use Functional Components with TypeScript interfaces for props.
- Prefer `lucide-react` for icons.
- Use `cn()` utility for conditional Tailwind classes.
- Follow the `components/ui/` pattern for reusable components.

### 2. State Management

- Use TanStack Query for server state.
- Use React `useState`/`useReducer` for local UI state.
- Avoid global state unless absolutely necessary.

### 3. API Communication

- Use the central API client in `lib/api.ts`.
- Define request/response types in `lib/validations.ts` or close to the feature.

### 4. Testing Requirements

- **Location:** `tests/components/` for unit/integration tests.
- **Commands:**
  - `npm test`: Run all tests.
  - `npm run test:watch`: Development mode.
  - `npm run test:cov`: Coverage report.
- Aim for high coverage on business logic and complex components.

### 5. Code Quality

- **Linting:** `npm run lint` (ESLint).
- **Formatting:** `npm run format` (Prettier).
- **Type Checking:** `npm run type-check` (tsc).

## Common Patterns

### Data Fetching with TanStack Query

```tsx
const { data, isLoading } = useQuery({
  queryKey: ['tasks'],
  queryFn: () => api.getTasks(),
});
```

### Shadcn/UI usage

- Check `components.json` for installed components.
- Add new components using the CLI if needed: `npx shadcn@latest add [component]`.

## UX/UI Principles

- Responsive design by default.
- Use `toast` for user feedback on actions.
- Loading states for all async operations.
- Accessible ARIA attributes where applicable.
