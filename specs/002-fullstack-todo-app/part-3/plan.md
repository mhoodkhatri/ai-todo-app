# Implementation Plan: Task Filtering, Responsive UI & Polish (Part 3)

**Branch**: `002-fullstack-todo-app-part-3` | **Date**: 2026-03-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-fullstack-todo-app/spec.md` — Part 3 scope from [phase-breakdown.md](./phase-breakdown.md)

## Summary

Part 3 completes Phase II by delivering **status filtering refinement**, **fully responsive UI** across mobile (320px+) through desktop (1024px+), **session expiry UX**, **database error resilience**, and **performance optimization**. Most functional code exists from Parts 1–2; this part focuses on polish, edge-case handling, and end-to-end verification of all 22 FRs and 8 SCs.

## Technical Context

**Language/Version**: TypeScript 5.x (Next.js 16+), Python 3.13+ (FastAPI)
**Primary Dependencies**: React 19, Tailwind CSS 4, Better Auth 1.5 (JWT/EdDSA), Zod, SQLModel, asyncpg
**Storage**: Neon Serverless PostgreSQL (no schema changes in Part 3)
**Testing**: Manual E2E verification against acceptance scenarios; browser responsive testing via DevTools
**Target Platform**: Web — desktop browsers (1024px+), tablet (768px), mobile (320px+)
**Project Type**: Web (monorepo — `frontend/` + `backend/`)
**Performance Goals**: Task list renders within 3 seconds on standard broadband (SC-008)
**Constraints**: No new database tables or migrations; no new API endpoints; minimal bundle size impact
**Scale/Scope**: Single-user experience polish; no pagination needed (assumption from spec)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | PASS | Plan generated from spec.md + phase-breakdown.md via `/sp.plan` |
| II. AI-First Implementation | PASS | Claude Code + Spec-Kit Plus workflow |
| III. Phased Incremental Evolution | PASS | Part 3 builds on Part 1 (auth) and Part 2 (CRUD) — no skips |
| IV. Cloud-Native Architecture | N/A | Phase IV+ concern; no infra changes in Part 3 |
| V. Clean Code & Project Structure | PASS | TypeScript + Tailwind CSS + FastAPI conventions maintained |
| VI. Monorepo Organization | PASS | Changes scoped to existing `frontend/` and `backend/` structure |
| JWT Security Model | PASS | No auth changes; existing JWT/JWKS flow preserved |

**Gate result**: PASS — no violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/002-fullstack-todo-app/
├── spec.md              # Feature specification (unchanged)
├── phase-breakdown.md   # Phase breakdown (unchanged)
├── plan.md              # This file (Part 3 plan)
├── research.md          # Phase 0 output — research findings
├── data-model.md        # Phase 1 output — no schema changes documented
├── quickstart.md        # Phase 1 output — dev setup for Part 3
└── contracts/           # Phase 1 output — API contract additions
    └── filter-query.md  # Filter query parameter contract
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── (auth)/              # Auth pages (unchanged)
│   ├── (protected)/
│   │   └── dashboard/
│   │       └── page.tsx     # Dashboard — responsive header refinement
│   ├── api/auth/[...all]/   # Better Auth handler (unchanged)
│   ├── layout.tsx           # Root layout (unchanged)
│   └── globals.css          # May add responsive utility styles
├── components/
│   ├── auth/                # Auth components (unchanged)
│   └── tasks/
│       ├── task-list.tsx     # Filter UI polish + responsive grid
│       ├── task-item.tsx     # Responsive task card layout
│       ├── task-form.tsx     # Mobile-optimized form
│       └── delete-dialog.tsx # Responsive modal (unchanged or minor)
├── lib/
│   ├── api.ts               # Session expiry interception (401 → redirect)
│   ├── auth.ts              # Unchanged
│   ├── auth-client.ts       # Unchanged
│   └── validations.ts       # Unchanged
└── proxy.ts                 # Route protection (unchanged)

backend/
├── app/
│   ├── api/
│   │   └── tasks.py         # Add optional `status` query parameter
│   └── ...                  # All other backend files unchanged
└── ...
```

**Structure Decision**: No new directories or files needed. All changes are modifications to existing files in the established monorepo structure.

## Complexity Tracking

> No constitution violations — this section is intentionally empty.

---

## Design Decisions

### D1: Client-Side vs Server-Side Filtering

**Decision**: Hybrid approach — add optional `status` query parameter to `GET /api/tasks` for server-side filtering support, but keep the existing client-side filter as the primary mechanism.

**Rationale**:
- Client-side filtering is already implemented and works well for the current scale (no pagination, single-user view)
- Adding a server-side `status` parameter future-proofs the API for when pagination is added in later phases
- The API contract is minimal (one optional query param) with no breaking changes
- Client-side remains primary to avoid unnecessary network requests on filter switches

**Alternatives rejected**:
- Server-side only: Would add network latency on every filter switch for small datasets
- Client-side only: Would not future-proof for pagination; API would need breaking changes later

### D2: Responsive Breakpoint Strategy

**Decision**: Mobile-first Tailwind approach with three breakpoints:
- Base (320px+): Single-column, stacked layout, touch-optimized
- `md` (768px+): Wider form inputs, horizontal task metadata
- `lg` (1024px+): Max-width container, comfortable spacing, side-by-side elements

**Rationale**: Tailwind CSS 4 mobile-first paradigm. Three breakpoints cover the spec requirements (320px mobile, 1024px+ desktop) with a tablet middle ground.

### D3: Session Expiry Detection

**Decision**: Centralized 401 interception in the API client (`lib/api.ts`). When any API call returns 401, redirect to `/signin?expired=true` with an informative banner.

**Rationale**:
- Single point of change — all API calls already go through `lib/api.ts`
- The signin page already supports a `session-expired` query parameter (from Part 1)
- No polling or token refresh needed — Better Auth handles session management; we only need to handle the expired-token case gracefully

### D4: Database Error UX

**Decision**: Catch network/fetch errors in the API client and display a user-friendly error banner in the task list. No retry logic — just clear messaging.

**Rationale**:
- Spec says "user-friendly error message" — not auto-retry
- Error state already exists in `task-list.tsx` (red banner)
- Network errors (fetch failures) need distinct messaging from API errors (4xx/5xx)

### D5: Performance Strategy

**Decision**: Verify existing performance meets the 3-second target. If not, apply targeted optimizations:
1. Ensure task list fetch starts early (not blocked by unnecessary renders)
2. Minimize component re-renders during filter switching
3. Verify no unnecessary re-fetches on filter change (data already loaded)

**Rationale**: The task list is already fetched once on mount and filtered client-side — this should already be fast. Measurement first, optimization only if needed.

---

## Implementation Approach

### Phase A: Filter & API Polish
1. Add optional `status` query parameter to backend `GET /api/tasks` endpoint
2. Refine filter UI styling — ensure active state is clear, touch-friendly on mobile
3. Verify filter empty states match spec wording

### Phase B: Responsive Design
4. Audit all components for responsive behavior at 320px, 768px, 1024px
5. Apply mobile-first Tailwind responsive classes to:
   - Dashboard header (stack on mobile, horizontal on desktop)
   - Task form (full-width inputs on mobile)
   - Task items (stack metadata on mobile, inline on desktop)
   - Filter buttons (full-width on mobile, inline on desktop)
   - Delete dialog (proper mobile margins)
6. Ensure touch targets are minimum 44x44px on mobile
7. Test typography scales across breakpoints

### Phase C: Edge Case & Error Handling
8. Implement 401 interception in `lib/api.ts` → redirect to `/signin?expired=true`
9. Distinguish network errors from API errors in error display
10. Verify concurrent tab edits (last-write-wins)

### Phase D: Performance & Verification
11. Measure task list load time — optimize if exceeding 3 seconds
12. Run through all 22 FRs checklist
13. Run through all 8 SCs checklist
14. Verify all 6 edge cases
15. Test all User Story 6 acceptance scenarios (1–4)
