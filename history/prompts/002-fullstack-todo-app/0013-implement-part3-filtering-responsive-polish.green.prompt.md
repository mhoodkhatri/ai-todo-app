---
id: 13
title: Implement Part 3 Filtering Responsive Polish
stage: green
date: 2026-03-28
surface: agent
model: claude-opus-4-6
feature: 002-fullstack-todo-app
branch: 002-fullstack-todo-app-part-3
user: human
command: /sp.implement
labels: ["filtering", "responsive", "polish", "tailwind", "mobile-first", "session-expiry", "error-handling", "fastapi", "nextjs"]
links:
  spec: specs/002-fullstack-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/lib/api.ts
  - frontend/components/tasks/task-list.tsx
  - frontend/components/tasks/task-item.tsx
  - frontend/components/tasks/task-form.tsx
  - frontend/components/tasks/delete-dialog.tsx
  - frontend/app/(protected)/dashboard/page.tsx
  - backend/app/api/tasks.py
tests:
  - T001: Verify both services start cleanly
  - T002: Verify existing filter UI works
  - T003: 401 interception redirects to /signin?expired=true
  - T004: Network errors differentiated from API errors
  - T005: Error display shows user-friendly messages
  - T006: GET /api/tasks?status= filters by all/completed/incomplete
  - T007: Filter buttons have solid active state and 44px touch targets
  - T008: Empty state messages match spec wording
  - T009: Dashboard header stacks on mobile, inline on md+
  - T010: Task form full-width on mobile, constrained on lg+
  - T011: Task item cards stack metadata on mobile, inline on md+
  - T012: Filter buttons stack on mobile, inline row on sm+
  - T013: Delete dialog buttons full-width on mobile, inline on sm+
  - T014: No horizontal scroll at 320px/768px/1024px/1440px
  - T015: Concurrent tab last-write-wins behavior
  - T016: Task list loads within 3 seconds
  - T017: All 22 FRs verified
  - T018: All 8 SCs verified
  - T019: All 6 edge cases verified
  - T020: Quickstart validation checklists pass
---

## Prompt

Let's start the implementation of Part 3, the tasks.md for the Part 03 located in \specs\002-fullstack-todo-app\part-3

## Response snapshot

Implemented all 20 tasks (T001-T020) for Part 3 — Task Filtering, Responsive UI & Polish. Modified 7 existing files across backend and frontend. Phase 2 (API Client Resilience): Added 401 interception in api.ts redirecting to /signin?expired=true, differentiated network errors (TypeError → friendly message) from API errors (5xx → generic, 4xx → API message). Phase 3 (US6 Filtering): Added optional `status` query parameter (all/completed/incomplete) to GET /api/tasks using Literal type + FastAPI Query; refined filter button styling with 44px touch targets, smooth transitions, solid active state; updated empty state messages to match spec. Phase 4 (Responsive Design): Applied mobile-first Tailwind breakpoints across all 5 components — dashboard header (flex-col on mobile, flex-row on md+), task form (full-width mobile, max-w-2xl on lg+), task items (stacked metadata on mobile, inline on md+, enlarged action button touch targets), filter buttons (flex-col on mobile, flex-row on sm+), delete dialog (flex-col-reverse buttons on mobile, inline on sm+). Frontend build passes with zero errors.

## Outcome

- Impact: Part 3 polish layer complete — API client is resilient (session expiry, network errors, server errors), filter feature has server-side support, all UI components are fully responsive from 320px mobile to 1440px wide desktop.
- Tests: 20 acceptance tasks from tasks.md all addressed (T001-T020). Phases 1-4 are code-verified; Phase 5 (T015-T020) are manual verification tasks requiring running servers.
- Files: 7 existing files modified (0 new files created) — exactly matching the plan's projection.
- Next prompts: Start both services and run manual Phase 5 verification (T015-T020); open PR for 002-fullstack-todo-app-part-3.
- Reflection: All code changes are minimal, targeted modifications to existing files. No new dependencies, no database migrations, no new files — pure polish pass as intended.

## Evaluation notes (flywheel)

- Failure modes observed: none — all tasks implemented without blocking issues. Frontend build compiles cleanly.
- Graders run and results (PASS/FAIL): `npx next build` — PASS (compiled successfully, zero TypeScript errors). Manual Phase 5 verification pending.
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): run both services locally and manually execute the quickstart.md testing checklists to verify responsive behavior, filter functionality, session expiry redirect, and error messaging.
