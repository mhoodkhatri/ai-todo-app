# Implementation Plan: Full-Stack Todo App — Part 1: Foundation, Database & Authentication

**Branch**: `002-fullstack-todo-app` | **Date**: 2026-03-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/002-fullstack-todo-app/spec.md` + [phase-breakdown.md](./phase-breakdown.md) Part 1
**Scope**: FR-001, FR-002, FR-003, FR-004, FR-016, FR-017, FR-022 | User Story 1

## Summary

Stand up the monorepo with a Next.js 16+ (App Router) frontend and a FastAPI backend, connect both to Neon Serverless PostgreSQL, and implement the full authentication flow using Better Auth with its JWT plugin. After Part 1, a user can sign up, sign in, sign out, and be redirected when unauthenticated. The Task database schema is created but no task CRUD is exposed yet (Part 2).

**Key architectural pattern**: Better Auth runs on the Next.js side, manages user accounts, and issues JWT tokens. The FastAPI backend verifies JWTs via Better Auth's JWKS endpoint and extracts the authenticated user ID. All future task queries will filter by this user ID for data isolation.

## Technical Context

**Language/Version**: TypeScript 5.x (Next.js 16+), Python 3.13+ (FastAPI)
**Primary Dependencies**:
- Frontend: Next.js 16+ (App Router), Tailwind CSS, Better Auth (JWT plugin), Zod
- Backend: FastAPI, SQLModel, Pydantic, PyJWT, uvicorn, asyncpg
**Storage**: Neon Serverless PostgreSQL (single database — Better Auth tables + application tables)
**Testing**: pytest + httpx (backend), vitest (frontend — deferred to Part 3)
**Target Platform**: Web (Desktop 1024px+, Mobile 320px+)
**Project Type**: Web application (monorepo: `frontend/` + `backend/`)
**Performance Goals**: Page loads within 3 seconds (SC-008)
**Constraints**: WSL 2 Ubuntu development environment (Constitution §V); UV for Python; npm for Node
**Scale/Scope**: Multi-user, no user or task count limit in Phase II

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Evidence |
|---|-----------|--------|----------|
| I | Spec-Driven Development | ✅ PASS | spec.md → plan.md → tasks.md workflow |
| II | AI-First Implementation | ✅ PASS | Claude Code with Spec-Kit Plus |
| III | Phased Evolution | ✅ PASS | Phase II, Part 1 of 3 |
| IV | Cloud-Native Architecture | ✅ PASS | Stateless services, JWT auth, Neon serverless DB |
| V | Clean Code & Structure | ✅ PASS | Python 3.13+/UV, TypeScript/Next.js/Tailwind, FastAPI/SQLModel, .env for secrets |
| V | JWT Security Model | ✅ PASS | Better Auth JWT (EdDSA) → JWKS endpoint → FastAPI verification → user_id isolation |
| V | WSL 2 Requirement | ✅ PASS | Development environment: WSL 2 Ubuntu |
| VI | Monorepo Organization | ✅ PASS | `frontend/` + `backend/` + per-folder `CLAUDE.md` |

**Gate Result**: ALL PASS — proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/002-fullstack-todo-app/
├── spec.md              # Feature specification
├── phase-breakdown.md   # 3-part breakdown
├── plan.md              # This file (Part 1 plan)
├── research.md          # Phase 0 research output
├── data-model.md        # Phase 1 data model
├── quickstart.md        # Phase 1 setup guide
├── contracts/           # Phase 1 API contracts
│   ├── auth-flow.md     # Authentication flow contract
│   └── backend-api.yaml # FastAPI OpenAPI stub
└── tasks.md             # Phase 2 output (/sp.tasks — NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/                              # Next.js 16+ (App Router)
├── app/
│   ├── (auth)/                        # Public auth route group
│   │   ├── layout.tsx                 # Centered auth layout
│   │   ├── signin/
│   │   │   └── page.tsx               # Sign-in page
│   │   └── signup/
│   │       └── page.tsx               # Sign-up page
│   ├── (protected)/                   # Authenticated route group
│   │   ├── layout.tsx                 # Auth-check layout
│   │   └── dashboard/
│   │       └── page.tsx               # Task dashboard (empty state for Part 1)
│   ├── api/
│   │   └── auth/
│   │       └── [...all]/
│   │           └── route.ts           # Better Auth catch-all handler
│   ├── layout.tsx                     # Root layout (providers, global styles)
│   └── page.tsx                       # Landing → redirect to /dashboard or /signin
├── lib/
│   ├── auth.ts                        # Better Auth server config + JWT plugin
│   ├── auth-client.ts                 # Better Auth client instance
│   └── validations.ts                 # Zod schemas for auth form inputs
├── components/
│   ├── auth/
│   │   ├── signin-form.tsx            # Sign-in form component
│   │   └── signup-form.tsx            # Sign-up form component
│   └── ui/                            # Shared UI primitives
├── proxy.ts                           # Next.js 16 route protection (replaces middleware.ts)
├── next.config.ts
├── tailwind.config.ts
├── package.json
├── tsconfig.json
├── .env.local                         # Local env vars (gitignored)
├── .env.example                       # Env var template
└── CLAUDE.md                          # Frontend conventions

backend/                               # FastAPI + SQLModel
├── app/
│   ├── __init__.py
│   ├── main.py                        # FastAPI app, CORS, router includes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                  # Pydantic Settings from env
│   │   ├── database.py                # Async engine + session dependency
│   │   └── security.py                # JWT verification dependency (HS256 shared secret)
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py                    # SQLModel Task table definition
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── common.py                  # Shared Pydantic response schemas
│   └── api/
│       ├── __init__.py
│       └── health.py                  # GET /api/health
├── alembic/                           # Database migrations
│   ├── versions/
│   └── env.py
├── alembic.ini
├── pyproject.toml                     # UV project config
├── .python-version                    # 3.13
├── .env                               # Local env vars (gitignored)
├── .env.example                       # Env var template
└── CLAUDE.md                          # Backend conventions
```

**Structure Decision**: Web application monorepo — `frontend/` for Next.js 16+ with Better Auth, `backend/` for FastAPI with SQLModel. Both connect to a single Neon PostgreSQL database (Better Auth manages auth tables, SQLModel manages application tables). Root `CLAUDE.md` provides project overview per Constitution §VI.

## Architecture Decisions

### 1. JWT Verification via JWKS (EdDSA)

**Decision**: Better Auth JWT plugin uses EdDSA (Ed25519) with automatic key pair management. FastAPI verifies JWTs by fetching the public key from Better Auth's `/api/auth/jwks` endpoint.

**Rationale**: Better Auth's JWT plugin exclusively supports asymmetric algorithms (EdDSA, RS256, ES256) with JWKS-based key management. HS256 symmetric signing is not supported by the plugin. EdDSA (Ed25519) is the default and most performant option. The backend caches the JWKS response to avoid per-request overhead.

**Amendment**: Constitution §V originally mandated HS256 with shared secret. Amended to EdDSA + JWKS after discovering Better Auth's JWT plugin does not support symmetric algorithms. The `BETTER_AUTH_SECRET` env var is still shared for Better Auth's internal session management, but JWT signing/verification uses EdDSA asymmetric keys managed by Better Auth.

**Alternatives rejected**:
- HS256 with shared secret: Not supported by Better Auth's JWT plugin — only asymmetric algorithms available.
- Custom HS256 signing (bypass plugin): Would require reimplementing JWT issuance outside Better Auth, adding complexity and losing key rotation.
- Session-based auth (no JWT): Would require FastAPI to call back to Next.js on every request. Adds latency and coupling.

### 2. No separate SQLModel User model

**Decision**: The Task table stores `user_id` as a plain string referencing Better Auth's user ID. No SQLModel `User` model or foreign key constraint to Better Auth's tables.

**Rationale**: Better Auth fully manages user lifecycle (create, read, update, delete) using its own Kysely-based database adapter. Creating a parallel SQLModel User model would cause schema conflicts and dual-write complexity. The JWT token carries the user ID — that's all FastAPI needs.

**Alternatives rejected**:
- SQLModel User model with FK to Better Auth: Schema coupling between two different ORM systems managing the same table.
- Duplicate user data in SQLModel: Sync issues, data drift, unnecessary complexity.

### 3. asyncpg + NullPool for Neon

**Decision**: Use `asyncpg` driver with SQLAlchemy `NullPool` for Neon Serverless PostgreSQL connections.

**Rationale**: Neon provides built-in pgbouncer pooling. Using `NullPool` on the SQLAlchemy side avoids double-pooling. `asyncpg` provides the best async performance for FastAPI (5x faster than psycopg3 in benchmarks). `statement_cache_size=0` is required for pgbouncer transaction mode.

### 4. Next.js 16 proxy.ts for route protection

**Decision**: Use `proxy.ts` (Next.js 16's replacement for `middleware.ts`) for route protection. Runs in Node.js runtime.

**Rationale**: Next.js 16 deprecates `middleware.ts` in favor of `proxy.ts`. The proxy runs in Node.js runtime (not Edge), which is compatible with Better Auth's session checking.

## Environment Variables

```env
# === Shared (identical in both services — Constitution §V) ===
DATABASE_URL=postgresql://user:password@ep-xxx.region.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=<openssl rand -base64 32>

# === Frontend (.env.local) ===
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_URL=http://localhost:3000

# === Backend (.env) ===
FRONTEND_URL=http://localhost:3000
BETTER_AUTH_SECRET=<same value as frontend — shared secret for JWT verification>
```

## Implementation Phases (Part 1 Scope)

### Phase A: Monorepo & Backend Scaffolding
1. Initialize `backend/` with UV: `uv init`, pyproject.toml, .python-version
2. Install dependencies: fastapi, uvicorn, sqlmodel, asyncpg, pyjwt, cryptography, alembic
3. Create `app/` package structure (core/, models/, schemas/, api/)
4. Implement `core/config.py` (Pydantic Settings)
5. Implement `core/database.py` (async engine, session dependency)
6. Implement `models/task.py` (SQLModel Task table)
7. Set up Alembic with async support, create initial migration
8. Implement `api/health.py` (GET /api/health)
9. Implement `app/main.py` (CORS, router includes)
10. Write `backend/CLAUDE.md`

### Phase B: Frontend Scaffolding & Better Auth
1. Initialize `frontend/` with `create-next-app@latest` (App Router, TypeScript, Tailwind)
2. Install Better Auth: `npm install better-auth`
3. Create `lib/auth.ts` (Better Auth server config + JWT plugin + pg adapter)
4. Create `lib/auth-client.ts` (Better Auth client)
5. Create `app/api/auth/[...all]/route.ts` (Better Auth handler)
6. Run Better Auth migration: `npx @better-auth/cli migrate`
7. Create `lib/validations.ts` (Zod schemas for auth inputs)
8. Write `frontend/CLAUDE.md`

### Phase C: Auth Pages & Forms
1. Create `app/(auth)/layout.tsx` (centered layout for auth pages)
2. Create `components/auth/signup-form.tsx` with dual validation (display name 1–100, email, password min 8)
3. Create `app/(auth)/signup/page.tsx`
4. Create `components/auth/signin-form.tsx` with validation
5. Create `app/(auth)/signin/page.tsx`
6. Handle error states: duplicate email, invalid credentials, whitespace-only display name

### Phase D: Route Protection & JWT Middleware
1. Create `proxy.ts` — redirect unauthenticated users to `/signin`, redirect authenticated users away from auth pages
2. Create `app/(protected)/layout.tsx` (server-side session check)
3. Create `app/(protected)/dashboard/page.tsx` (empty state placeholder)
4. Create `app/page.tsx` (landing redirect logic)
5. Implement `backend/app/core/security.py` — JWT verification via JWKS, extract user_id
6. Apply JWT dependency to FastAPI app (global or per-router)
7. Test end-to-end: signup → JWT issued → protected route access → FastAPI verification

### Phase E: Sign-out, Session Expiry & Polish
1. Implement sign-out action (Better Auth client `signOut()`)
2. Handle session expiry: detect expired token, redirect to signin with message
3. Update root `CLAUDE.md` with Phase II monorepo context
4. Create `.env.example` files for both frontend and backend
5. Verify all Part 1 acceptance scenarios pass

## Acceptance Criteria (from User Story 1)

- [ ] **AC-1**: Visitor signs up with display name, email, password → account created, signed in, redirected to dashboard
- [ ] **AC-2**: Registered user signs in with valid credentials → authenticated, redirected to dashboard
- [ ] **AC-3**: User enters wrong password → error message, no access
- [ ] **AC-4**: Signed-in user clicks sign out → session ended, redirected to signin
- [ ] **AC-5**: Unauthenticated user visits protected page → redirected to signin
- [ ] **AC-6**: Duplicate email on signup → appropriate error message

## Validation Rules (FR-022, Dual — Frontend + Backend)

| Field | Rule | Frontend | Backend |
|-------|------|----------|---------|
| Display Name | 1–100 characters, not whitespace-only | Zod schema | Pydantic/Better Auth |
| Email | Valid email format | Zod schema | Better Auth |
| Password | Minimum 8 characters | Zod schema | Better Auth |

## Risks & Follow-ups

1. **Better Auth + Neon cold starts**: Neon serverless may have cold start latency on first auth request. Mitigate: use Neon's connection pooler endpoint.
2. **Better Auth HS256 support**: Must verify that Better Auth's JWT plugin supports HS256 algorithm configuration. If not, escalate — do not fall back to asymmetric keys without amending the constitution.
3. **Next.js 16 proxy.ts stability**: proxy.ts replaces middleware.ts in Next.js 16. If unstable, fallback to middleware.ts with Edge runtime.

## Complexity Tracking

> No constitution violations. No complexity justifications needed.
