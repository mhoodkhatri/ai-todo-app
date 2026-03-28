# Tasks: Task Filtering, Responsive UI & Polish (Part 3)

**Input**: Design documents from `/specs/002-fullstack-todo-app/part-3/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/filter-query.md, quickstart.md
**Branch**: `002-fullstack-todo-app-part-3`

**Tests**: Not requested in the feature specification. No test tasks included.

**Organization**: Tasks are grouped by functional area. Part 3 has one user story (US6 — Filter Tasks by Status) plus cross-cutting polish work (responsive UI, error handling, session expiry, performance). Cross-cutting phases are labeled without a story tag since they span all stories.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[US6]**: Belongs to User Story 6 — Filter Tasks by Status
- Exact file paths included in descriptions

---

## Phase 1: Setup

**Purpose**: Verify dev environment and establish Part 3 working context

- [x] T001 Verify both services start cleanly: `backend/` on port 8000, `frontend/` on port 3000 per `specs/002-fullstack-todo-app/part-3/quickstart.md`
- [x] T002 Verify existing filter UI works (all/completed/incomplete client-side) on current `frontend/components/tasks/task-list.tsx`

**Checkpoint**: Dev environment confirmed — existing Part 1+2 functionality intact

---

## Phase 2: Foundational (API Client Resilience)

**Purpose**: Harden the API client layer (`frontend/lib/api.ts`) — these changes affect ALL API calls and MUST be complete before other phases

**Why foundational**: Session expiry interception (401 → redirect) and error differentiation change the behavior of every API call. Completing this first ensures all subsequent work inherits correct error handling.

- [x] T003 Implement 401 interception in `frontend/lib/api.ts` — when any `apiFetch` response returns 401, redirect to `/signin?expired=true` using `window.location.href` (hard redirect to clear React state)
- [x] T004 Differentiate network errors from API errors in `frontend/lib/api.ts` — catch `TypeError: Failed to fetch` (network) separately from HTTP error responses: network error → "Unable to connect to the server. Please check your connection and try again."; 5xx → "Something went wrong. Please try again later."; 4xx → display API error message; 401 → redirect (from T003)
- [x] T005 Update error display in `frontend/components/tasks/task-list.tsx` to render differentiated error messages from the improved `apiFetch` (network vs server errors)

**Checkpoint**: API client correctly handles 401 redirect, network errors, and server errors with user-friendly messages

---

## Phase 3: User Story 6 — Filter Tasks by Status (Priority: P3)

**Goal**: Complete the filtering feature with server-side API support, polished filter UI, and correct empty states per spec US6 acceptance scenarios 1–4

**Independent Test**: Create several tasks, mark some complete, verify each filter option (All/Completed/Incomplete) shows the correct subset. Apply a filter with 0 matching results and verify empty state message.

### Implementation for User Story 6

- [x] T006 [US6] Add optional `status` query parameter to `GET /api/tasks` endpoint in `backend/app/api/tasks.py` — accept `"all"` (default), `"completed"`, `"incomplete"` per `specs/002-fullstack-todo-app/part-3/contracts/filter-query.md`; use `Query(default="all")` with validation; filter by `is_completed` boolean accordingly
- [x] T007 [US6] Refine filter button styling in `frontend/components/tasks/task-list.tsx` — ensure active filter state is visually clear (solid background, not just hover), touch-friendly minimum 44x44px tap targets, smooth transition between states
- [x] T008 [US6] Verify filter empty state messages in `frontend/components/tasks/task-list.tsx` match spec wording — "no tasks" (zero tasks total) vs "No tasks match the selected filter" (filter produces empty results) per US6 acceptance scenario 4

**Checkpoint**: User Story 6 fully functional — all 4 acceptance scenarios pass; backend supports server-side filtering; client-side filtering remains primary mechanism

---

## Phase 4: Responsive Design

**Purpose**: Apply mobile-first responsive Tailwind classes across all components to meet FR-019 (responsive web interface) and SC-004 (desktop 1024px+ and mobile 320px+). Three breakpoints: base (320px+), `md` (768px+), `lg` (1024px+) per research.md R2.

- [x] T009 [P] Make dashboard header responsive in `frontend/app/(protected)/dashboard/page.tsx` — stack title and user greeting vertically on mobile (base), horizontal `flex-row` on `md`+; ensure header padding and font sizes scale appropriately across breakpoints
- [x] T010 [P] Make task form responsive in `frontend/components/tasks/task-form.tsx` — full-width inputs on mobile (base), constrained max-width on `lg`+; ensure submit button is full-width on mobile with minimum 44x44px touch target; ensure proper spacing between form fields on all breakpoints
- [x] T011 [P] Make task item cards responsive in `frontend/components/tasks/task-item.tsx` — stack task metadata (title, description, date) vertically on mobile (base), horizontal layout on `md`+; ensure action buttons (edit, delete) have minimum 44x44px touch targets; ensure checkbox touch target is minimum 44x44px; adjust text sizes and spacing per breakpoint
- [x] T012 [P] Make filter buttons responsive in `frontend/components/tasks/task-list.tsx` — full-width stacked buttons on mobile (base via `flex flex-col`), inline row on `sm`+ (via `sm:flex-row`); ensure each button has minimum 44x44px touch target on mobile
- [x] T013 [P] Make delete confirmation dialog responsive in `frontend/components/tasks/delete-dialog.tsx` — ensure proper mobile margins (`mx-4`), readable text, and touch-friendly buttons (minimum 44x44px) at 320px viewport; verify modal content doesn't overflow on small screens
- [x] T014 Verify no horizontal scroll at 320px, 768px, 1024px, and 1440px viewports across all pages — audit `frontend/app/globals.css` and add any needed responsive utility overrides (e.g., `overflow-x-hidden` on body if needed)

**Checkpoint**: All components render correctly at 320px (mobile), 768px (tablet), 1024px (desktop), and 1440px (wide). No horizontal scroll. All interactive elements meet 44x44px minimum touch target on mobile.

---

## Phase 5: Polish & Cross-Cutting Verification

**Purpose**: Performance verification, edge-case validation, and final FR/SC checklist sign-off

- [x] T015 Verify concurrent tab behavior — open app in two tabs, edit the same task in both, confirm last-write-wins behavior works without errors (edge case from spec)
- [x] T016 Measure task list load performance per SC-008 — load dashboard with 10+ tasks, verify total time from navigation to full task list render is under 3 seconds on standard broadband; document measurement method and result
- [x] T017 Run through all 22 Functional Requirements (FR-001 through FR-022) from `specs/002-fullstack-todo-app/spec.md` — verify each passes with current implementation; document any gaps found
- [x] T018 Run through all 8 Success Criteria (SC-001 through SC-008) from `specs/002-fullstack-todo-app/spec.md` — verify each passes; document any gaps found
- [x] T019 Verify all 6 edge cases from `specs/002-fullstack-todo-app/spec.md` — session expiry redirect (T003), whitespace title rejection, whitespace display name rejection, concurrent tab edits (T015), database unavailability error message (T004), task URL manipulation returns 404
- [x] T020 Run quickstart.md validation — execute all testing checklists from `specs/002-fullstack-todo-app/part-3/quickstart.md` (responsive testing, filter testing, session expiry testing, error resilience testing, performance testing)

**Checkpoint**: All 22 FRs, 8 SCs, 6 edge cases, and 4 acceptance scenarios for US6 verified. Part 3 complete.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — verify environment first
- **Phase 2 (Foundational — API Client)**: Depends on Phase 1 — BLOCKS Phase 3 (filter error states depend on improved error handling)
- **Phase 3 (US6 — Filtering)**: Depends on Phase 2 — backend and frontend filter work
- **Phase 4 (Responsive)**: Depends on Phase 2 — can run IN PARALLEL with Phase 3 (different files)
- **Phase 5 (Verification)**: Depends on Phases 3 AND 4 completion

### Task Dependencies Within Phases

**Phase 2** (sequential):
- T003 → T004 → T005 (each builds on prior api.ts changes)

**Phase 3** (mostly sequential):
- T006 (backend) can run in parallel with T007/T008 (frontend) since client-side filtering is primary
- T007 and T008 are on the same file — run sequentially

**Phase 4** (high parallelism):
- T009, T010, T011, T012, T013 all marked [P] — different files, no dependencies
- T014 depends on T009–T013 (audit after all responsive changes applied)

**Phase 5** (sequential verification):
- T015–T020 should run sequentially as a validation sweep

### Parallel Opportunities

```
Phase 2 complete
├── Phase 3: US6 Filtering (T006–T008)
│   └── T006 (backend) ║ T007+T008 (frontend)
└── Phase 4: Responsive (T009–T014)
    └── T009 ║ T010 ║ T011 ║ T012 ║ T013 → T014

Both Phase 3 & Phase 4 → Phase 5: Verification (T015–T020)
```

---

## Parallel Example: Phase 4 (Responsive Design)

```bash
# Launch all responsive tasks together (all different files):
Task T009: "Make dashboard header responsive in frontend/app/(protected)/dashboard/page.tsx"
Task T010: "Make task form responsive in frontend/components/tasks/task-form.tsx"
Task T011: "Make task item cards responsive in frontend/components/tasks/task-item.tsx"
Task T012: "Make filter buttons responsive in frontend/components/tasks/task-list.tsx"
Task T013: "Make delete dialog responsive in frontend/components/tasks/delete-dialog.tsx"
```

---

## Implementation Strategy

### MVP First (Phase 2 + Phase 3 Only)

1. Complete Phase 1: Setup verification
2. Complete Phase 2: API client resilience (401 redirect + error differentiation)
3. Complete Phase 3: User Story 6 — filter polish + backend status param
4. **STOP and VALIDATE**: Test filtering works end-to-end, session expiry redirects correctly
5. Responsive and verification can follow

### Incremental Delivery

1. Phase 1: Setup → Environment confirmed
2. Phase 2: API Client → Session expiry and error handling hardened
3. Phase 3: US6 Filtering → Filter feature complete with server-side support
4. Phase 4: Responsive → All components mobile-friendly (320px+)
5. Phase 5: Verification → All 22 FRs, 8 SCs, 6 edge cases confirmed

### Single-Developer Strategy (Recommended for Part 3)

Part 3 is a polish/refinement scope with no new features requiring parallel staffing:

1. Phase 2: API client changes first (small, high-impact, blocks filter error states)
2. Phase 3: Backend filter param + frontend filter refinement (US6 completion)
3. Phase 4: Responsive sweep across 5 components (batch all together)
4. Phase 5: Full verification sweep (final sign-off)

---

## Summary

| Metric | Value |
|--------|-------|
| **Total tasks** | 20 |
| **Phase 1 (Setup)** | 2 tasks |
| **Phase 2 (Foundational)** | 3 tasks |
| **Phase 3 (US6 Filtering)** | 3 tasks |
| **Phase 4 (Responsive)** | 6 tasks |
| **Phase 5 (Verification)** | 6 tasks |
| **Parallelizable tasks** | 7 (T009–T013 responsive + T006 backend) |
| **User stories covered** | US6 (P3) — primary; US1–US5 verified in Phase 5 |
| **Suggested MVP scope** | Phase 2 + Phase 3 (API resilience + US6 filtering) |
| **Files modified** | 7 existing files (no new files created) |

---

## Notes

- [P] tasks = different files, no dependencies
- [US6] label maps task to User Story 6 (Filter Tasks by Status)
- Tasks without story labels are cross-cutting (affect all stories)
- No new npm/Python dependencies required
- No database migrations required
- All changes are modifications to existing files
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
