# Tasks: Console Todo Application (Phase I)

**Input**: Design documents from `/specs/001-console-todo-app/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested in the feature specification. Test files are defined in plan.md architecture — generate test tasks separately if needed.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, directory structure, and package configuration

- [x] T001 Create project directory structure: `src/`, `src/models/`, `src/services/`, `src/ui/`, `tests/` per plan.md
- [x] T002 [P] Initialize pyproject.toml with UV configuration: project name "todo", requires-python >= 3.13, dev dependency pytest>=8.0, script entry point `todo = "src.main:main"` per research.md R5
- [x] T003 [P] Create all `__init__.py` package files: `src/__init__.py`, `src/models/__init__.py`, `src/services/__init__.py`, `src/ui/__init__.py`, `tests/__init__.py`

**Checkpoint**: Project skeleton ready — `uv sync` should succeed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data model, service skeleton, UI helpers, and menu loop that ALL user stories depend on

**Includes User Story 6 (Menu Navigation, P1)**: The menu system is the application's sole interface — it is foundational infrastructure, not an independent feature phase.

**US6 Acceptance Covered**:
- Welcome banner on startup (T007)
- Exit with goodbye message (T007)
- Invalid input handling with re-prompt (T007)
- Valid option routing to feature flows (T007, wired per-story in Phases 3–7)

- [x] T004 [P] Implement Task dataclass with all fields (id, title, description, completed, created_at, updated_at), defaults (completed=False, timestamps=datetime.now), and `__repr__` in src/models/task.py per data-model.md
- [x] T005 [P] Implement base console UI helpers in src/ui/console.py: display_welcome_banner(), display_menu(), get_valid_int_input(prompt), display_error(message), display_success(message), format_task_row(task) with UTF-8 status indicators (✅/❌) per research.md R6
- [x] T006 Initialize TaskService class with _tasks: dict[int, Task], _next_id: int = 1, and get_task(task_id) → Task | None method in src/services/task_service.py (depends on T004)
- [x] T007 Implement main entry point in src/main.py: import TaskService and UI, display welcome banner, run numbered menu loop (1-6), route valid options, handle invalid input with error message and re-prompt, exit on option 6 with goodbye message, wrap in try/except for KeyboardInterrupt and EOFError per research.md R3/R5 (depends on T005, T006)

**Checkpoint**: App launches with `uv run todo`, shows welcome banner, displays menu, handles invalid input, exits cleanly on option 6 or Ctrl+C. US6 is fully functional.

---

## Phase 3: User Story 1 — Add a New Task (Priority: P1) MVP

**Goal**: Users can add a task with a required title and optional description, receiving a confirmation with the assigned task ID.

**Independent Test**: Launch the app, select "Add Task", enter a title and description, verify confirmation shows a valid task ID. Try empty title and over-length inputs to verify validation.

### Implementation for User Story 1

- [x] T008 [US1] Implement add_task(title: str, description: str = "") → Task method in src/services/task_service.py: create Task with auto-incremented ID, store in _tasks dict, increment _next_id, return created Task
- [x] T009 [US1] Implement add task UI flow in src/ui/console.py: prompt_add_task(service) that prompts for title (required, 1-200 chars, strip whitespace, reject empty/whitespace-only), prompts for description (optional, max 1000 chars), calls service.add_task(), displays "Task created successfully with ID: {id}"
- [x] T010 [US1] Wire "Add Task" (option 1) in src/main.py menu to call prompt_add_task(service)

**Checkpoint**: User Story 1 fully functional — add tasks with validation, see confirmation with ID

---

## Phase 4: User Story 2 — View All Tasks (Priority: P1)

**Goal**: Users can view all tasks in a formatted list with ID, title, status indicator, creation date, and a summary of total/complete counts.

**Independent Test**: Add several tasks (some toggled complete later), select "View All Tasks", verify formatted list with correct indicators and summary counts. Also verify "No tasks found" when empty.

### Implementation for User Story 2

- [x] T011 [US2] Implement get_all_tasks() → list[Task] and get_summary() → tuple[int, int] methods in src/services/task_service.py: return all tasks as list, return (total_count, completed_count) tuple
- [x] T012 [US2] Implement view all tasks display in src/ui/console.py: display_all_tasks(service) that shows "No tasks found" if empty, otherwise displays each task as formatted row (ID, title, ✅/❌, creation date as YYYY-MM-DD HH:MM), followed by summary line "Total: {n} tasks ({c} complete, {i} incomplete)"
- [x] T013 [US2] Wire "View All Tasks" (option 2) in src/main.py menu to call display_all_tasks(service)

**Checkpoint**: User Stories 1 AND 2 functional — add tasks and view them in formatted list with summary

---

## Phase 5: User Story 3 — Update an Existing Task (Priority: P2)

**Goal**: Users can update a task's title and/or description by ID. Leaving a field blank preserves the existing value. Updated_at timestamp is refreshed.

**Independent Test**: Add a task, update its title, verify change persists when viewing. Try updating non-existent ID. Try leaving fields blank to confirm preservation.

### Implementation for User Story 3

- [x] T014 [US3] Implement update_task(task_id: int, title: str | None, description: str | None) → Task | None method in src/services/task_service.py: look up task, update non-None/non-empty fields, set updated_at = datetime.now(), return updated Task or None if not found
- [x] T015 [US3] Implement update task UI flow in src/ui/console.py: prompt_update_task(service) that prompts for task ID (validated int), shows "Task with ID {id} not found" if missing, displays current title and description, prompts for new title (blank=keep, validate 1-200 chars if provided) and new description (blank=keep, validate max 1000 chars if provided), calls service.update_task(), displays confirmation
- [x] T016 [US3] Wire "Update Task" (option 3) in src/main.py menu to call prompt_update_task(service)

**Checkpoint**: User Stories 1, 2, AND 3 functional — add, view, and update tasks

---

## Phase 6: User Story 4 — Delete a Task (Priority: P2)

**Goal**: Users can delete a task by ID with a confirmation prompt before permanent removal.

**Independent Test**: Add a task, delete it with confirmation, verify it no longer appears in list. Try declining confirmation. Try deleting non-existent ID.

### Implementation for User Story 4

- [x] T017 [US4] Implement delete_task(task_id: int) → bool method in src/services/task_service.py: remove task from _tasks if exists, return True; return False if not found
- [x] T018 [US4] Implement delete task UI flow in src/ui/console.py: prompt_delete_task(service) that prompts for task ID (validated int), shows "Task with ID {id} not found" if missing, asks "Are you sure? (y/n)" confirmation, deletes on "y" with success message, shows cancellation message on any other input
- [x] T019 [US4] Wire "Delete Task" (option 4) in src/main.py menu to call prompt_delete_task(service)

**Checkpoint**: User Stories 1, 2, 3, AND 4 functional — full CRUD minus toggle

---

## Phase 7: User Story 5 — Toggle Task Completion (Priority: P2)

**Goal**: Users can toggle a task between complete and incomplete status by ID, seeing the new state confirmed.

**Independent Test**: Add a task (defaults incomplete), toggle to complete, verify status indicator changes. Toggle again back to incomplete.

### Implementation for User Story 5

- [x] T020 [US5] Implement toggle_task(task_id: int) → Task | None method in src/services/task_service.py: flip completed boolean, set updated_at = datetime.now(), return updated Task or None if not found
- [x] T021 [US5] Implement toggle task UI flow in src/ui/console.py: prompt_toggle_task(service) that prompts for task ID (validated int), shows "Task with ID {id} not found" if missing, calls service.toggle_task(), displays "Task {id} marked as complete" or "Task {id} marked as incomplete" based on new state
- [x] T022 [US5] Wire "Toggle Complete" (option 5) in src/main.py menu to call prompt_toggle_task(service)

**Checkpoint**: ALL user stories functional — complete CRUD + toggle + menu navigation

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Edge case hardening and end-to-end validation across all stories

- [x] T023 [P] Validate all edge cases across all flows: non-numeric ID input shows "Please enter a valid number", whitespace-only title rejected, negative/zero IDs return "not found", Ctrl+C returns to menu or exits cleanly, per spec edge cases section
- [x] T024 Run quickstart.md end-to-end validation: `uv sync` succeeds, `uv run todo` launches correctly, all 6 menu options work per quickstart.md scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational (Phase 2) — No dependencies on other stories
- **US2 (Phase 4)**: Depends on Foundational (Phase 2) — No dependencies on other stories (can parallel with US1)
- **US3 (Phase 5)**: Depends on Foundational (Phase 2) — No dependencies on other stories
- **US4 (Phase 6)**: Depends on Foundational (Phase 2) — No dependencies on other stories
- **US5 (Phase 7)**: Depends on Foundational (Phase 2) — No dependencies on other stories
- **US6 (Menu)**: Handled within Foundational (Phase 2) — complete after Phase 7 wiring
- **Polish (Phase 8)**: Depends on all user stories being complete

### Within Each User Story

- Service method first (data layer)
- UI flow second (presentation layer, depends on service interface)
- Wire in main.py third (integration, depends on UI function)

### Parallel Opportunities

- **Phase 1**: T002 and T003 can run in parallel after T001
- **Phase 2**: T004 (model) and T005 (UI helpers) can run in parallel; T006 depends on T004; T007 depends on T005 and T006
- **Cross-story**: US1, US2, US3, US4, US5 can theoretically start in parallel after Phase 2 (all operate on different service methods and UI functions), though sequential by priority (P1 → P2) is recommended for a single developer
- **Phase 8**: T023 and T024 can run in parallel

---

## Parallel Example: After Foundational Phase

```bash
# Sequential (recommended for single developer):
Phase 3: US1 (Add Task) → Phase 4: US2 (View All) → Phase 5-7: US3, US4, US5

# Parallel (if multiple developers):
Developer A: Phase 3 (US1 - Add Task)     → Phase 5 (US3 - Update Task)
Developer B: Phase 4 (US2 - View All)     → Phase 6 (US4 - Delete Task)
Developer C: Phase 7 (US5 - Toggle Complete)
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 + Menu)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (includes US6 menu — BLOCKS all stories)
3. Complete Phase 3: User Story 1 (Add Task)
4. Complete Phase 4: User Story 2 (View All Tasks)
5. **STOP and VALIDATE**: App can add and display tasks — this is the MVP
6. Demo if ready

### Incremental Delivery

1. Setup + Foundational → App launches with menu (US6 done)
2. Add US1 (Add Task) → Can create tasks → Demo
3. Add US2 (View All) → Can create and see tasks → **MVP Demo**
4. Add US3 (Update Task) → Full edit capability → Demo
5. Add US4 (Delete Task) → Full CRUD → Demo
6. Add US5 (Toggle Complete) → Complete feature set → Demo
7. Polish → Production-ready → **Final Demo**

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- US6 (Menu Navigation) is handled in Foundational phase since it IS the application skeleton
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Total tasks: 24 (3 setup + 4 foundational + 15 story + 2 polish)
- Tests not included — add test phases if TDD approach is requested
