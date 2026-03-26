# Quickstart: Task CRUD Operations (Part 2)

**Prerequisites**: Part 1 fully implemented (auth, scaffold, database, JWT). Both `frontend/.env.local` and `backend/.env` configured with Neon DATABASE_URL and BETTER_AUTH_SECRET.

## 1. Start Backend

```bash
cd backend
uv sync                                            # Install deps (if not done)
uv run alembic upgrade head                        # Ensure task table exists
uv run uvicorn app.main:app --reload --port 8000   # Start FastAPI dev server
```

Verify: `curl http://localhost:8000/api/health` → `{"status": "ok"}`

## 2. Start Frontend

```bash
cd frontend
npm install                                        # Install deps (if not done)
npm run dev                                        # Start Next.js dev server (port 3000)
```

Verify: Open `http://localhost:3000` → should redirect to sign-in or dashboard

## 3. Part 2 Implementation Order

The implementation follows this dependency chain:

```
Backend schemas → Backend router → Frontend API client → Frontend components → Dashboard integration
```

### Step-by-step:

1. **Backend: Task schemas** (`backend/app/schemas/task.py`)
   - `TaskCreate`, `TaskUpdate`, `TaskResponse` Pydantic models
   - Validation: title trim + 1-200 chars, description max 1000

2. **Backend: Task router** (`backend/app/api/tasks.py`)
   - 6 endpoints: POST, GET list, GET by ID, PUT, PATCH toggle, DELETE
   - All use `Depends(get_current_user)` for auth
   - All queries filter by `user_id` for isolation
   - Register in `main.py`

3. **Frontend: Zod schemas** (`frontend/lib/validations.ts`)
   - Add `taskCreateSchema` and `taskUpdateSchema`

4. **Frontend: API client** (`frontend/lib/api.ts`)
   - Typed functions: `createTask`, `listTasks`, `getTask`, `updateTask`, `toggleTask`, `deleteTask`
   - Gets JWT from Better Auth session, sets Authorization header

5. **Frontend: Task components** (`frontend/components/tasks/`)
   - `task-form.tsx` — Create/edit form with Zod validation
   - `task-list.tsx` — List view with empty state
   - `task-item.tsx` — Row with toggle, edit, delete actions
   - `delete-dialog.tsx` — Confirmation before deletion

6. **Frontend: Dashboard** (`frontend/app/(protected)/dashboard/page.tsx`)
   - Replace placeholder with `<TaskList />` component

## 4. Manual Verification Checklist

After implementation, verify these scenarios:

- [x] Create task with title only → appears in list
- [x] Create task with title + description → both visible
- [x] Submit empty title → validation error shown
- [x] Submit 201+ char title → validation error shown
- [x] Submit 1001+ char description → validation error shown
- [x] View task list → sorted newest first
- [x] Empty state → shows CTA message when no tasks
- [x] Edit task title → updated in list
- [x] Edit task description → updated in list
- [x] Clear title during edit → validation error
- [x] Toggle complete → visual distinction applied
- [x] Toggle incomplete → reverts to normal style
- [x] Delete with confirm → task removed
- [x] Delete cancelled → task remains
- [x] Sign out + sign in → tasks persist
- [x] Two users → each sees only own tasks
- [x] URL manipulation to other user's task → 404 response

## 5. API Testing (curl)

After starting both servers and signing up via the frontend:

```bash
# Get a JWT token (copy from browser DevTools → Application → Cookies or Network tab)
TOKEN="<your-jwt-token>"

# Create a task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'

# List tasks
curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN"

# Toggle completion (replace TASK_ID)
curl -X PATCH http://localhost:8000/api/tasks/TASK_ID/toggle \
  -H "Authorization: Bearer $TOKEN"

# Update task
curl -X PUT http://localhost:8000/api/tasks/TASK_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries and snacks"}'

# Delete task
curl -X DELETE http://localhost:8000/api/tasks/TASK_ID \
  -H "Authorization: Bearer $TOKEN"
```
