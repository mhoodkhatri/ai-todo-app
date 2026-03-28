# Quickstart: Part 3 — Task Filtering, Responsive UI & Polish

**Branch**: `002-fullstack-todo-app-part-3` | **Date**: 2026-03-28

## Prerequisites

- Parts 1 and 2 fully implemented and working on `main`
- Node.js 18+ and npm installed
- Python 3.13+ and UV installed
- Neon PostgreSQL database provisioned with migrations applied
- `.env` files configured in both `frontend/` and `backend/`

## Environment Variables (unchanged from Parts 1–2)

### `frontend/.env`
```
DATABASE_URL=postgresql://...@...neon.tech/...
BETTER_AUTH_SECRET=<shared-secret>
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### `backend/.env`
```
DATABASE_URL=postgresql+asyncpg://...@...neon.tech/...
BETTER_AUTH_SECRET=<shared-secret>
FRONTEND_URL=http://localhost:3000
```

## Development Setup

### Terminal 1 — Backend
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — Frontend
```bash
cd frontend
npm install
npm run dev
```

Application available at `http://localhost:3000`.

## Part 3 Scope — What Changes

| Area | Files Modified | Change Type |
|------|---------------|-------------|
| Filter API | `backend/app/api/tasks.py` | Add optional `status` query param |
| Session expiry | `frontend/lib/api.ts` | 401 interception → redirect |
| Responsive UI | `frontend/components/tasks/*.tsx` | Tailwind responsive classes |
| Dashboard | `frontend/app/(protected)/dashboard/page.tsx` | Responsive header layout |
| Error handling | `frontend/lib/api.ts`, `frontend/components/tasks/task-list.tsx` | Differentiated error messages |

### No New Dependencies
Part 3 requires no additional npm or Python packages.

### No Database Migrations
Part 3 introduces no schema changes. Existing migrations from Parts 1–2 are sufficient.

## Testing Checklist

### Responsive Testing
- Open Chrome DevTools → Device Toolbar
- Test at: 320px (mobile), 768px (tablet), 1024px (desktop), 1440px (wide)
- Verify: No horizontal scroll, readable text, touch-friendly buttons

### Filter Testing
1. Create 3+ tasks, mark some complete
2. Click "All" → see all tasks
3. Click "Completed" → see only completed tasks
4. Click "Incomplete" → see only incomplete tasks
5. With filter active showing 0 results → see empty state message

### Session Expiry Testing
1. Sign in and use the app normally
2. Manually expire/invalidate the session (clear cookies or wait for token expiry)
3. Perform any task action → should redirect to signin with expiry message

### Error Resilience Testing
1. Stop the backend server
2. Attempt to load dashboard or perform a task action
3. Verify user-friendly error message (not raw error)

### Performance Testing
1. Create 10+ tasks
2. Open Network tab in DevTools
3. Hard refresh dashboard
4. Verify task list renders within 3 seconds
