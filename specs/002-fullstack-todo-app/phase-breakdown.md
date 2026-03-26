# Phase II Breakdown: Full-Stack Todo Web Application

**Spec**: [spec.md](./spec.md) (single, unified — do not split)
**Branch**: `002-fullstack-todo-app`
**Created**: 2026-03-24
**Purpose**: Break Phase II into three implementable sub-phases, each processed via `/sp.plan` → `/sp.tasks` → `/sp.implement`

---

## Part 1: Project Foundation, Database & Authentication

**Goal**: Stand up the monorepo, database, and full authentication flow. After this part, a user can sign up, sign in, sign out, and be redirected when unauthenticated. No task features yet.

### User Stories Covered
- **User Story 1** — User Registration and Authentication (P1)

### Functional Requirements Covered
| ID | Requirement |
|----|-------------|
| FR-001 | User registration with display name, email, password |
| FR-002 | User authentication with email/password |
| FR-003 | Secure JWT token issuance and inclusion in requests |
| FR-004 | Reject task requests without valid auth token (401) |
| FR-016 | Redirect unauthenticated users to sign-in page |
| FR-017 | User sign-out ending session |
| FR-022 | Dual validation on auth inputs (display name 1–100 chars, valid email, password min 8 chars) |

### Success Criteria Covered
| ID | Criteria |
|----|----------|
| SC-001 | Sign up and reach dashboard in under 2 minutes |
| SC-006 | Invalid auth inputs rejected with clear error messages |

### Scope of Work
1. **Monorepo structure** — `frontend/`, `backend/`, root and subfolder `CLAUDE.md` files per Constitution §VI
2. **Frontend scaffolding** — Next.js 16+ (App Router), Tailwind CSS, TypeScript
3. **Backend scaffolding** — FastAPI, SQLModel, Pydantic, UV package manager
4. **Database** — Neon Serverless PostgreSQL connection, User and Task table schemas (SQLModel models)
5. **Better Auth** — Integration on Next.js frontend with JWT plugin, session management
6. **JWT middleware** — FastAPI middleware verifying `Authorization: Bearer <token>` using shared `BETTER_AUTH_SECRET`
7. **Auth pages** — Sign-up page (display name + email + password), Sign-in page, Sign-out action
8. **Protected routes** — Frontend middleware redirecting unauthenticated users; backend 401 on missing/invalid token
9. **Validation** — Dual (frontend + backend): display name 1–100 chars (no whitespace-only), valid email, password min 8 chars
10. **Error handling** — Duplicate email rejection, incorrect password message, session expiry redirect

### Edge Cases Addressed
- Session token expiry → redirect to sign-in with message
- Whitespace-only display name → reject with validation error

### Acceptance Scenarios (from User Story 1)
- Scenarios 1–6 (signup, signin, wrong password, signout, unauthenticated redirect, duplicate email)

---

## Part 2: Task CRUD Operations (Full-Stack)

**Goal**: Implement all task create, read, update, delete, and completion toggle features. After this part, users can fully manage their tasks through the web UI.

### User Stories Covered
- **User Story 2** — Create and View Tasks (P1)
- **User Story 3** — Update Task Details (P2)
- **User Story 4** — Mark Task as Complete/Incomplete (P2)
- **User Story 5** — Delete a Task (P2)

### Functional Requirements Covered
| ID | Requirement |
|----|-------------|
| FR-005 | Create tasks with title (1–200 chars) and optional description (max 1,000 chars) |
| FR-006 | Dual validation: reject empty/whitespace titles, oversized title/description |
| FR-007 | Persist tasks to durable database |
| FR-008 | Display task list with title, completion status, creation date |
| FR-009 | Update task title and description |
| FR-010 | Toggle task completion status |
| FR-011 | Delete task after confirmation |
| FR-013 | User isolation on all data operations (CRUD + toggle) |
| FR-014 | RESTful API exposing task operations |
| FR-015 | Return 404 (not 403) for another user's task |
| FR-018 | Record creation and last-updated timestamps |
| FR-020 | Empty state with call-to-action for zero tasks |
| FR-021 | Task list sorted by creation date, newest first |

### Success Criteria Covered
| ID | Criteria |
|----|----------|
| SC-001 | Create first task and view in list in under 2 minutes |
| SC-002 | Create, update, complete, delete each under 30 seconds |
| SC-003 | 100% user isolation on all task operations |
| SC-005 | Task data persists across sessions, devices, restarts |
| SC-006 | Invalid task inputs rejected with clear messages |

### Scope of Work
1. **RESTful API endpoints** — `POST /api/tasks`, `GET /api/tasks`, `GET /api/tasks/{id}`, `PUT /api/tasks/{id}`, `PATCH /api/tasks/{id}/toggle`, `DELETE /api/tasks/{id}`
2. **User isolation** — All DB queries filtered by authenticated user ID; 404 for unauthorized task access
3. **Create task** — Form with title (required) and description (optional), frontend + backend validation
4. **Task list view** — Display title, completion status, creation date; sorted newest first
5. **Empty state** — Message + CTA when user has zero tasks
6. **Update task** — Edit form for title and description with validation
7. **Toggle completion** — Checkbox/button to toggle complete/incomplete, visual distinction for completed tasks
8. **Delete task** — Confirmation dialog before permanent deletion
9. **Timestamps** — `created_at` and `updated_at` on every task, auto-managed
10. **Validation** — Dual (frontend + backend): title 1–200 chars non-whitespace, description max 1,000 chars

### Edge Cases Addressed
- Whitespace-only title → reject with validation error
- URL manipulation to access another user's task → 404 response
- Concurrent edits (two tabs) → last write wins (no optimistic concurrency)
- Database temporarily unavailable → user-friendly error message

### Acceptance Scenarios
- User Story 2: Scenarios 1–6 (create with title, create with description, empty title, long title, long description, user isolation)
- User Story 3: Scenarios 1–4 (update title, update description, clear title, unauthorized update)
- User Story 4: Scenarios 1–3 (mark complete, mark incomplete, unauthorized toggle)
- User Story 5: Scenarios 1–3 (delete confirmed, delete cancelled, unauthorized delete)

---

## Part 3: Task Filtering, Responsive UI & Polish

**Goal**: Add status filtering, ensure responsive design across viewports, and handle remaining edge cases. After this part, Phase II is feature-complete.

### User Stories Covered
- **User Story 6** — Filter Tasks by Status (P3)

### Functional Requirements Covered
| ID | Requirement |
|----|-------------|
| FR-012 | Filter task list by status: all, completed, incomplete |
| FR-019 | Responsive web interface for desktop and mobile |

### Success Criteria Covered
| ID | Criteria |
|----|----------|
| SC-004 | Usable on desktop (1024px+) and mobile (320px+) viewports |
| SC-007 | Filter correctly shows accurate subset for each option |
| SC-008 | Task list loads and renders within 3 seconds |

### Scope of Work
1. **Filter UI** — Tab/button group for "All", "Completed", "Incomplete" filter options
2. **Filter logic** — Client-side or API query parameter filtering by completion status
3. **Filter empty state** — Message when no tasks match the selected filter
4. **Responsive layout** — Tailwind responsive breakpoints: mobile-first (320px+), tablet, desktop (1024px+)
5. **Mobile optimization** — Touch-friendly targets, readable typography, proper spacing
6. **Desktop optimization** — Efficient use of wider viewport, appropriate content width
7. **Session expiry UX** — Detect expired token, redirect to sign-in with informative message
8. **Database error UX** — Graceful error display when backend/DB is unreachable
9. **Performance** — Optimize initial load to render task list within 3 seconds
10. **End-to-end verification** — Validate all 22 FRs, 8 SCs, and 6 edge cases pass

### Edge Cases Addressed
- No tasks matching selected filter → empty state message
- Session token expires during active use → redirect with message
- Database temporarily unavailable → user-friendly error
- Concurrent tab edits → last write wins (verified)

### Acceptance Scenarios
- User Story 6: Scenarios 1–4 (filter completed, filter incomplete, show all, empty filter result)

---

## Implementation Order

```
Part 1 ──→ Part 2 ──→ Part 3
```

Each part follows the SDD workflow independently:
1. `/sp.plan` — Generate implementation plan from this breakdown + spec.md
2. `/sp.tasks` — Break plan into testable tasks
3. `/sp.implement` — Execute tasks via Claude Code

### Cross-Reference: Complete FR Coverage

| FR | Part 1 | Part 2 | Part 3 |
|----|--------|--------|--------|
| FR-001 | x | | |
| FR-002 | x | | |
| FR-003 | x | | |
| FR-004 | x | | |
| FR-005 | | x | |
| FR-006 | | x | |
| FR-007 | | x | |
| FR-008 | | x | |
| FR-009 | | x | |
| FR-010 | | x | |
| FR-011 | | x | |
| FR-012 | | | x |
| FR-013 | | x | |
| FR-014 | | x | |
| FR-015 | | x | |
| FR-016 | x | | |
| FR-017 | x | | |
| FR-018 | | x | |
| FR-019 | | | x |
| FR-020 | | x | |
| FR-021 | | x | |
| FR-022 | x | | |

**All 22 functional requirements, 8 success criteria, 6 user stories, and 6 edge cases are accounted for.**
