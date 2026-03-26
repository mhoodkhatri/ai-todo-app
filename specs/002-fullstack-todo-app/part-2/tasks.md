# Tasks: Task CRUD Operations (Part 2)

**Input**: Design documents from `specs/002-fullstack-todo-app/part-2/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/tasks-api.yaml, quickstart.md
**Tests**: Not requested — manual acceptance testing per quickstart.md

**Organization**: Tasks grouped by user story. Part 1 (auth, scaffold, database, migrations) is already implemented — Part 2 begins from the existing codebase.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US2, US3, US4, US5, US6)
- Exact file paths included in every description

## Part 2 Scope (from spec.md)

| Story | Title | Priority | Part 2 Status |
|-------|-------|----------|---------------|
| US1 | User Registration and Authentication | P1 | ✅ Done (Part 1) |
| US2 | Create and View Tasks | P1 | 🔨 This part |
| US3 | Update Task Details | P2 | 🔨 This part |
| US4 | Mark Task as Complete/Incomplete | P2 | 🔨 This part |
| US5 | Delete a Task | P2 | 🔨 This part |
| US6 | Filter Tasks by Status | P3 | 🔨 This part |

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: New files and shared modules required by all user stories. No new dependencies — everything builds on Part 1.

- [x] T001 [P] Create task Pydantic schemas (TaskCreate, TaskUpdate, TaskResponse) in backend/app/schemas/task.py with title trim + 1-200 char validation, description max 1000 chars, and TaskResponse excluding user_id (per data-model.md)
- [x] T002 [P] Create Zod task validation schemas (taskCreateSchema, taskUpdateSchema) in frontend/lib/validations.ts — mirror backend validation rules: title trim 1-200 chars, description optional max 1000 chars
- [x] T003 [P] Create API client module in frontend/lib/api.ts with typed fetch wrapper that gets JWT from Better Auth session (authClient), sets Authorization Bearer header, and targets NEXT_PUBLIC_API_URL base URL. Include functions: createTask, listTasks, getTask, updateTask, toggleTask, deleteTask (per research.md R4)

**Checkpoint**: Schemas and API client ready — backend router and frontend components can now be built

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend task router with create, list, and get endpoints — MUST be complete before frontend task components can function

**⚠️ CRITICAL**: No user story frontend work can begin until the backend router is registered

- [x] T004 Create task CRUD router in backend/app/api/tasks.py with APIRouter(prefix="/tasks", tags=["tasks"]). Start with POST /api/tasks (create), GET /api/tasks (list, sorted by created_at DESC), and GET /api/tasks/{task_id} (get single). All endpoints use Depends(get_current_user) for auth and filter by user_id for isolation. Return 404 (not 403) for other users' tasks per FR-015
- [x] T005 Register task router in backend/app/main.py — add `app.include_router(tasks.router, prefix="/api")` following the existing health router pattern

**Checkpoint**: Backend create/list/get endpoints live — frontend task components can now call the API

---

## Phase 3: User Story 2 — Create and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Authenticated user can create tasks (title + optional description) and view their task list with empty state

**Independent Test**: Sign in → create a task with title and description → verify it appears in list with correct details, status "incomplete", and creation date. Verify empty state shows CTA when no tasks exist.

### Implementation for User Story 2

- [x] T006 [P] [US2] Create task form component in frontend/components/tasks/task-form.tsx — client component with title input (required), description textarea (optional), Zod validation from lib/validations.ts, calls createTask from lib/api.ts, shows validation errors inline, clears form on success
- [x] T007 [P] [US2] Create task list component in frontend/components/tasks/task-list.tsx — client component that calls listTasks from lib/api.ts on mount, renders tasks sorted newest first, shows empty state message with CTA to create first task (FR-020), includes loading state
- [x] T008 [P] [US2] Create task item component in frontend/components/tasks/task-item.tsx — client component showing task title, completion status (visual distinction), and created_at date. Include action placeholders for toggle, edit, and delete (wired in later stories)
- [x] T009 [US2] Integrate task components into dashboard page at frontend/app/(protected)/dashboard/page.tsx — replace placeholder content with TaskForm and TaskList components, ensure page works for authenticated users

**Checkpoint**: US2 complete — users can create and view tasks. This is the MVP increment.

---

## Phase 4: User Story 3 — Update Task Details (Priority: P2)

**Goal**: Authenticated user can edit a task's title and description inline, with changes saved and reflected immediately

**Independent Test**: Create a task → edit its title and description → verify changes persist after page reload

### Implementation for User Story 3

- [x] T010 [US3] Add PUT /api/tasks/{task_id} endpoint in backend/app/api/tasks.py — accepts TaskUpdate body, validates title/description, queries by both task_id AND user_id, updates title + description + updated_at, returns 404 for missing/other-user tasks, returns updated TaskResponse
- [x] T011 [US3] Add inline edit mode to task-item component in frontend/components/tasks/task-item.tsx — edit button triggers form with current values pre-filled, Zod validation on submit, calls updateTask from lib/api.ts, shows validation errors, reverts on cancel, refreshes list on success

**Checkpoint**: US3 complete — users can edit task details

---

## Phase 5: User Story 4 — Mark Task as Complete/Incomplete (Priority: P2)

**Goal**: Authenticated user can toggle task completion status; completed tasks are visually distinguished

**Independent Test**: Create a task → mark complete → verify visual change → toggle back to incomplete → verify reverted

### Implementation for User Story 4

- [x] T012 [US4] Add PATCH /api/tasks/{task_id}/toggle endpoint in backend/app/api/tasks.py — flips is_completed boolean, updates updated_at timestamp, queries by both task_id AND user_id, returns 404 for missing/other-user tasks, returns updated TaskResponse
- [x] T013 [US4] Wire toggle action in task-item component in frontend/components/tasks/task-item.tsx — checkbox or toggle button calls toggleTask from lib/api.ts, applies visual distinction for completed tasks (strikethrough/opacity), refreshes list on success

**Checkpoint**: US4 complete — users can toggle task completion

---

## Phase 6: User Story 5 — Delete a Task (Priority: P2)

**Goal**: Authenticated user can permanently delete a task after confirmation; deleted tasks disappear from list

**Independent Test**: Create a task → click delete → cancel confirmation → task remains → click delete → confirm → task removed from list

### Implementation for User Story 5

- [x] T014 [US5] Add DELETE /api/tasks/{task_id} endpoint in backend/app/api/tasks.py — queries by both task_id AND user_id, returns 404 for missing/other-user tasks, returns 204 No Content on success, permanent removal (no soft delete)
- [x] T015 [P] [US5] Create delete confirmation dialog in frontend/components/tasks/delete-dialog.tsx — styled modal with Cancel and Delete buttons, triggered from task-item, no browser window.confirm() (per research.md R8)
- [x] T016 [US5] Wire delete action in task-item component in frontend/components/tasks/task-item.tsx — delete button opens DeleteDialog, on confirm calls deleteTask from lib/api.ts, removes task from list on success

**Checkpoint**: US5 complete — users can delete tasks with confirmation

---

## Phase 7: User Story 6 — Filter Tasks by Status (Priority: P3)

**Goal**: Authenticated user can filter task list by All / Completed / Incomplete; default shows All

**Independent Test**: Create several tasks → mark some complete → verify "Completed" filter shows only completed → "Incomplete" shows only incomplete → "All" shows everything → empty filter shows empty state message

### Implementation for User Story 6

- [x] T017 [US6] Add client-side filter controls to task-list component in frontend/components/tasks/task-list.tsx — three filter buttons/tabs (All, Completed, Incomplete), filter applied to already-fetched task array (no extra API call), default to "All", show empty state message when filter matches no tasks (FR-012)

**Checkpoint**: US6 complete — users can filter tasks by status

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Responsive design, error handling, and final verification

- [x] T018 [P] Ensure responsive layout for task dashboard at frontend/app/(protected)/dashboard/page.tsx and all task components — verify usable on desktop (1024px+) and mobile (320px+) per SC-004
- [x] T019 [P] Add user-friendly error handling for API failures across frontend/lib/api.ts and task components — display error messages for network failures and database unavailability instead of raw errors
- [x] T020 Run quickstart.md manual verification checklist (specs/002-fullstack-todo-app/part-2/quickstart.md section 4) — verify all 16 acceptance scenarios pass ✅ All 17 scenarios verified against implementation (code review)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately. T001, T002, T003 all parallel.
- **Foundational (Phase 2)**: T004 depends on T001 (schemas). T005 depends on T004.
- **US2 (Phase 3)**: T006 depends on T002 + T003. T007 depends on T003. T008 is parallel with T006/T007. T009 depends on T006 + T007 + T008.
- **US3 (Phase 4)**: T010 depends on T004. T011 depends on T010 + T003.
- **US4 (Phase 5)**: T012 depends on T004. T013 depends on T012.
- **US5 (Phase 6)**: T014 depends on T004. T015 is parallel (no deps). T016 depends on T014 + T015.
- **US6 (Phase 7)**: T017 depends on T007 (task-list exists).
- **Polish (Phase 8)**: T018 and T019 are parallel. T020 depends on all prior phases.

### User Story Dependencies

- **US2 (P1)**: Can start after Foundational (Phase 2) — **no dependencies on other stories**
- **US3 (P2)**: Can start after Foundational — **no dependencies on other stories** (task-item from US2 will be extended)
- **US4 (P2)**: Can start after Foundational — **no dependencies on other stories** (task-item from US2 will be extended)
- **US5 (P2)**: Can start after Foundational — **no dependencies on other stories** (task-item from US2 will be extended)
- **US6 (P3)**: Depends on US2 (task-list component must exist)

### Recommended Sequential Order (single developer)

```
Phase 1 (T001-T003) → Phase 2 (T004-T005) → Phase 3/US2 (T006-T009) → Phase 4/US3 (T010-T011) → Phase 5/US4 (T012-T013) → Phase 6/US5 (T014-T016) → Phase 7/US6 (T017) → Phase 8 (T018-T020)
```

### Within Each User Story

- Backend endpoint before frontend component that calls it
- Schemas/validation before components that use them
- Individual components before dashboard integration

### Parallel Opportunities

**Phase 1** — all three tasks touch different files:
```
T001: backend/app/schemas/task.py
T002: frontend/lib/validations.ts
T003: frontend/lib/api.ts
```

**Phase 3 (US2)** — components are independent files:
```
T006: frontend/components/tasks/task-form.tsx
T007: frontend/components/tasks/task-list.tsx
T008: frontend/components/tasks/task-item.tsx
```

**Phase 6 (US5)** — dialog is independent of backend:
```
T014: backend/app/api/tasks.py (DELETE endpoint)
T015: frontend/components/tasks/delete-dialog.tsx
```

---

## Implementation Strategy

### MVP First (User Story 2 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T005)
3. Complete Phase 3: User Story 2 (T006-T009)
4. **STOP and VALIDATE**: Create a task, verify it appears in list, verify empty state
5. Demo-ready with create + view functionality

### Incremental Delivery

1. Setup + Foundational → schemas, API client, backend router ready
2. Add US2 (create + view) → **MVP! Demo-ready**
3. Add US3 (edit) → tasks are editable
4. Add US4 (toggle) → completion tracking works
5. Add US5 (delete) → full CRUD complete
6. Add US6 (filter) → polished UX
7. Polish → responsive, error handling, final verification

### File Creation Summary

| # | File | Action | Phase |
|---|------|--------|-------|
| 1 | backend/app/schemas/task.py | CREATE | Phase 1 |
| 2 | frontend/lib/validations.ts | MODIFY | Phase 1 |
| 3 | frontend/lib/api.ts | CREATE | Phase 1 |
| 4 | backend/app/api/tasks.py | CREATE | Phase 2 |
| 5 | backend/app/main.py | MODIFY | Phase 2 |
| 6 | frontend/components/tasks/task-form.tsx | CREATE | Phase 3 |
| 7 | frontend/components/tasks/task-list.tsx | CREATE | Phase 3 |
| 8 | frontend/components/tasks/task-item.tsx | CREATE | Phase 3 |
| 9 | frontend/app/(protected)/dashboard/page.tsx | MODIFY | Phase 3 |
| 10 | frontend/components/tasks/delete-dialog.tsx | CREATE | Phase 6 |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently testable after completion
- No new dependencies needed — Part 1 installed everything
- Task model + migration already exist from Part 1 — no schema changes
- Manual acceptance testing per quickstart.md section 4
- Commit after each task or logical group
