# Tasks: Full-Stack Todo App — Part 1: Foundation, Database & Authentication

**Input**: Design documents from `specs/002-fullstack-todo-app/part-1/`
**Prerequisites**: plan.md (loaded), spec.md (loaded), data-model.md (loaded), contracts/ (loaded), research.md (loaded), quickstart.md (loaded)

**Tests**: Not included — frontend tests deferred to Part 3 (vitest), backend tests are optional for Part 1.

**Organization**: Part 1 covers a single user story (US1 — Registration and Authentication). Tasks are organized as Setup → Foundational → US1 Implementation → Polish.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[US1]**: User Story 1 — User Registration and Authentication
- Exact file paths included in every task description

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create monorepo structure and initialize both projects

- [x] T001 Create monorepo directory structure with `frontend/` and `backend/` directories at repository root
- [x] T002 [P] Initialize backend with UV: run `uv init` in `backend/`, configure `backend/pyproject.toml` (name, version, python >=3.13), create `backend/.python-version` with `3.13`
- [x] T003 [P] Initialize frontend with `create-next-app@latest` in `frontend/` (App Router, TypeScript, Tailwind CSS, no src/ directory — app/ at `frontend/app/`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before User Story 1 implementation can begin

**CRITICAL**: No user story work can begin until this phase is complete

### Backend Core Infrastructure

- [x] T004 Install backend dependencies in `backend/pyproject.toml`: fastapi, uvicorn[standard], sqlmodel, asyncpg, pyjwt, alembic, python-dotenv, httpx
- [x] T005 Create backend app package structure with `__init__.py` files: `backend/app/__init__.py`, `backend/app/core/__init__.py`, `backend/app/models/__init__.py`, `backend/app/schemas/__init__.py`, `backend/app/api/__init__.py`
- [x] T006 Implement Pydantic Settings configuration in `backend/app/core/config.py` — load DATABASE_URL, BETTER_AUTH_SECRET, FRONTEND_URL from environment using python-dotenv
- [x] T007 Implement async database engine and session dependency in `backend/app/core/database.py` — create_async_engine with asyncpg driver, NullPool, pool_pre_ping=True, statement_cache_size=0; provide `get_session` async generator dependency
- [x] T008 [P] Implement Task SQLModel table definition in `backend/app/models/task.py` — fields: id (UUID PK), user_id (str, indexed), title (str, max 200), description (optional str, max 1000), is_completed (bool, default false), created_at (datetime UTC), updated_at (datetime UTC)
- [x] T009 [P] Implement shared Pydantic response schemas in `backend/app/schemas/common.py` — HealthResponse schema with status field
- [x] T010 Set up Alembic with async support: initialize `backend/alembic/` directory, configure `backend/alembic.ini` and `backend/alembic/env.py` for async SQLModel, create initial migration for the `task` table
- [x] T011 Implement health check endpoint in `backend/app/api/health.py` — GET /api/health returning `{"status": "ok"}`, no authentication required
- [x] T012 Implement FastAPI application entry point in `backend/app/main.py` — create FastAPI app, configure CORS (allow FRONTEND_URL origin), include health router at `/api` prefix

### Frontend Core Infrastructure

- [x] T013 Install Better Auth and Zod dependencies in `frontend/`: `npm install better-auth pg zod`
- [x] T014 Create Better Auth server configuration with JWT plugin (HS256) and pg adapter in `frontend/lib/auth.ts` — betterAuth() with database Pool(DATABASE_URL), secret from BETTER_AUTH_SECRET, JWT plugin with HS256 algorithm and 15-minute expiration
- [x] T015 Create Better Auth client instance in `frontend/lib/auth-client.ts` — createAuthClient() with baseURL from NEXT_PUBLIC_BETTER_AUTH_URL
- [x] T016 Create Better Auth catch-all API handler in `frontend/app/api/auth/[...all]/route.ts` — export GET and POST using toNextJsHandler(auth)
- [x] T017 Create Zod validation schemas for auth form inputs in `frontend/lib/validations.ts` — signUpSchema (name: trim 1–100 chars, email: valid format, password: min 8 chars), signInSchema (email, password)

**Checkpoint**: Both backend and frontend are scaffolded, Better Auth is configured, database engine is ready. User story implementation can begin.

---

## Phase 3: User Story 1 — User Registration and Authentication (Priority: P1)

**Goal**: A user can sign up with display name, email, and password; sign in with credentials; be redirected when unauthenticated; and sign out to end their session.

**Independent Test**: Create an account → auto-signed-in → redirected to dashboard → sign out → redirected to signin → sign back in → dashboard access restored → visit protected page while signed out → redirected to signin.

**Acceptance Criteria**:
- AC-1: Visitor signs up → account created, signed in, redirected to dashboard
- AC-2: Registered user signs in → authenticated, redirected to dashboard
- AC-3: User enters wrong password → error message, no access
- AC-4: Signed-in user signs out → session ended, redirected to signin
- AC-5: Unauthenticated user visits protected page → redirected to signin
- AC-6: Duplicate email on signup → appropriate error message

### Auth Pages & Forms

- [x] T018 [US1] Create centered auth layout in `frontend/app/(auth)/layout.tsx` — centered card layout for signin/signup pages, minimal styling with Tailwind
- [x] T019 [US1] Create signup form component in `frontend/components/auth/signup-form.tsx` — form fields: display name, email, password; client-side Zod validation using signUpSchema; call `authClient.signUp.email()`; handle success (redirect to /dashboard) and errors (duplicate email, validation failures); show loading state
- [x] T020 [US1] Create signup page in `frontend/app/(auth)/signup/page.tsx` — render SignUpForm component, link to signin page
- [x] T021 [US1] Create signin form component in `frontend/components/auth/signin-form.tsx` — form fields: email, password; client-side Zod validation using signInSchema; call `authClient.signIn.email()`; handle success (redirect to /dashboard) and errors (invalid credentials); show loading state
- [x] T022 [US1] Create signin page in `frontend/app/(auth)/signin/page.tsx` — render SignInForm component, link to signup page, display session-expired message if query param present

### Route Protection

- [x] T023 [US1] Implement JWT verification dependency in `backend/app/core/security.py` — HTTPBearer scheme, decode JWT with BETTER_AUTH_SECRET (HS256), extract `sub` claim as user_id, return 401 on missing/invalid/expired token
- [x] T024 [US1] Create route protection proxy in `frontend/proxy.ts` — check session via `auth.api.getSession()`; redirect unauthenticated users from protected routes (`/dashboard/*`) to `/signin`; redirect authenticated users from auth routes (`/signin`, `/signup`) to `/dashboard`; skip `/api/*` routes
- [x] T025 [US1] Create protected routes layout with server-side session check in `frontend/app/(protected)/layout.tsx` — verify session using `auth.api.getSession()`, redirect to `/signin` if no session
- [x] T026 [US1] Create dashboard page with empty state placeholder in `frontend/app/(protected)/dashboard/page.tsx` — display user greeting with display name, empty state message ("No tasks yet — you'll be able to create tasks in Part 2"), sign-out button
- [x] T027 [US1] Create root landing page with redirect logic in `frontend/app/page.tsx` — redirect to `/dashboard` (proxy.ts handles auth check)
- [x] T028 [US1] Update root layout in `frontend/app/layout.tsx` — ensure Tailwind CSS globals are imported, set metadata (title, description), wrap children with any needed providers

### Sign-out & Session Handling

- [x] T029 [US1] Implement sign-out functionality — call `authClient.signOut()` from dashboard sign-out button, redirect to `/signin` on success, handle errors gracefully
- [x] T030 [US1] Handle session expiry — detect expired session on protected page access via proxy.ts/layout check, redirect to `/signin?expired=true`, display "Session expired, please sign in again" message on signin page

**Checkpoint**: User Story 1 is fully functional — signup, signin, signout, route protection, session expiry all working. AC-1 through AC-6 should pass.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Environment documentation, project conventions, and final verification

- [x] T031 [P] Create `backend/.env.example` with template values for DATABASE_URL, BETTER_AUTH_SECRET, FRONTEND_URL
- [x] T032 [P] Create `frontend/.env.example` with template values for DATABASE_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL, NEXT_PUBLIC_API_URL, NEXT_PUBLIC_BETTER_AUTH_URL
- [x] T033 [P] Write `backend/CLAUDE.md` — document backend conventions: Python 3.13+, UV, FastAPI, SQLModel, asyncpg, Alembic, project structure, dev commands
- [x] T034 [P] Write `frontend/CLAUDE.md` — document frontend conventions: Next.js 16+, TypeScript, Tailwind, Better Auth, Zod, project structure, dev commands
- [x] T035 Update root `CLAUDE.md` with Phase II monorepo context — document monorepo structure (frontend/ + backend/), shared env vars, dev workflow (two terminals), active technologies
- [ ] T036 Run quickstart.md verification checklist — confirm: backend health endpoint responds, frontend redirects to signin, signup creates account, dashboard accessible after auth, signout works, protected route redirects, JWT verification functional

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion — BLOCKS User Story 1
  - T004–T005 depend on T002 (backend init)
  - T006 depends on T004 (dependencies installed)
  - T007 depends on T006 (config available)
  - T008, T009 can parallel after T004
  - T010 depends on T007, T008 (engine + model)
  - T011 depends on T005 (package structure)
  - T012 depends on T011 (health router)
  - T013 depends on T003 (frontend init)
  - T014–T017 depend on T013 (deps installed)
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) completion
  - T018–T022: Auth pages — can start after T014–T017
  - T023: JWT security — can start after T006 (config)
  - T024–T028: Route protection — depends on T014 (auth config)
  - T029–T030: Sign-out — depends on T026 (dashboard page)
- **Polish (Phase 4)**: Depends on User Story 1 completion
  - T031–T034 can all run in parallel
  - T035 depends on T033, T034
  - T036 depends on all previous tasks

### Parallel Opportunities

```bash
# Phase 1 — parallel project init:
T002: "Initialize backend with UV"
T003: "Initialize frontend with create-next-app"

# Phase 2 — parallel after deps installed:
T008: "Create Task SQLModel in backend/app/models/task.py"
T009: "Create response schemas in backend/app/schemas/common.py"

# Phase 3 — parallel form creation:
T019: "Create signup form in frontend/components/auth/signup-form.tsx"
T021: "Create signin form in frontend/components/auth/signin-form.tsx"

# Phase 4 — parallel documentation:
T031: "Create backend/.env.example"
T032: "Create frontend/.env.example"
T033: "Write backend/CLAUDE.md"
T034: "Write frontend/CLAUDE.md"
```

---

## Implementation Strategy

### MVP (User Story 1 Only — Part 1 scope)

1. Complete Phase 1: Setup → monorepo directories initialized
2. Complete Phase 2: Foundational → both services scaffolded, database connected, Better Auth configured
3. Complete Phase 3: User Story 1 → full authentication flow working
4. **STOP and VALIDATE**: Verify AC-1 through AC-6
5. Complete Phase 4: Polish → documentation, env examples, verification

### Incremental Delivery

1. Setup + Backend Foundational (T001–T012) → `uvicorn` starts, health endpoint responds
2. Frontend Foundational (T013–T017) → Better Auth configured, auth tables migrated
3. Auth Pages (T018–T022) → signup and signin forms visible
4. Route Protection (T023–T028) → full auth flow with redirects
5. Sign-out & Polish (T029–T036) → complete Part 1, ready for Part 2

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [US1] label maps all Phase 3 tasks to User Story 1
- Task model (T008) is created in Part 1 but CRUD endpoints are deferred to Part 2
- Better Auth manages user/session/account tables — do NOT create SQLModel models for these
- HS256 shared secret (BETTER_AUTH_SECRET) must be identical in both services (Constitution §V)
- proxy.ts replaces middleware.ts in Next.js 16 — runs in Node.js runtime
- asyncpg + NullPool avoids double-pooling with Neon's built-in pgbouncer
- Commit after each task or logical group
