---
id: 001
title: Create Phase I Console Todo Spec
stage: spec
date: 2026-03-24
surface: agent
model: claude-opus-4-6
feature: 001-console-todo-app
branch: 001-console-todo-app
user: developer
command: /sp.specify
labels: ["spec", "todo", "console", "phase1", "hackathon"]
links:
  spec: specs/001-console-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-console-todo-app/spec.md
  - specs/001-console-todo-app/checklists/requirements.md
tests:
  - Specification quality checklist validated (all items pass)
---

## Prompt

Prompt:

  You are building Phase I of the "Evolution of Todo" hackathon project — an in-memory Python console application using Spec-Driven Development with Spec-Kit Plus.

  ## Project Setup

  1. Initialize a new Python project using **UV** with **Python 3.13+**
  2. Create this folder structure:

  todo-console-app/
  ├── CLAUDE.md                    # Claude Code instructions
  ├── README.md                    # Setup instructions (how to install UV, run the app)
  ├── constitution.md              # Project constitution (principles, constraints, goals)
  ├── specs/                       # Specs history folder
  │   └── phase1-console.md        # Phase I specification
  ├── src/
  │   └── todo/
  │       ├── init.py
  │       ├── main.py              # Entry point with menu loop
  │       ├── models.py            # Task data model (dataclass or Pydantic)
  │       └── manager.py           # TaskManager class (in-memory store)
  └── pyproject.toml               # UV/Python project config

  ## Specification (specs/phase1-console.md)

  Write a detailed spec covering all 5 Basic Level features:

  ### Feature 1: Add Task
  - User provides a title (required, 1-200 chars) and description (optional, max 1000 chars)
  - Each task gets a unique auto-incrementing integer ID
  - New tasks default to incomplete status
  - Display confirmation with the assigned task ID

  ### Feature 2: View Task List
  - Display all tasks in a formatted table/list
  - Show: ID, Title, Status (checkmark complete / X incomplete), Created Date
  - Show a message if no tasks exist
  - Show total count of tasks and how many are complete

  ### Feature 3: Update Task
  - User provides task ID to update
  - Allow updating title and/or description
  - If user leaves a field blank, keep the existing value
  - Show error if task ID doesn't exist
  - Display confirmation after successful update

  ### Feature 4: Delete Task
  - User provides task ID to delete
  - Ask for confirmation before deleting
  - Show error if task ID doesn't exist
  - Display confirmation after successful deletion

  ### Feature 5: Mark as Complete/Incomplete
  - User provides task ID to toggle
  - Toggle between complete and incomplete status
  - Show error if task ID doesn't exist
  - Display the new status after toggling

  ## Implementation Requirements

  ### Task Model
  - Fields: id (int), title (str), description (str | None), completed (bool), created_at (datetime), updated_at (datetime)
  - Use Python dataclass or Pydantic BaseModel

  ### TaskManager Class
  - Store tasks in a dictionary: dict[int, Task]
  - Auto-increment ID counter starting at 1
  - Methods: add_task(), get_task(), get_all_tasks(), update_task(), delete_task(), toggle_complete()
  - All methods should return appropriate success/error results

  ### Console Interface (main.py)
  - Interactive menu loop with numbered options (1-6)
  - Clear user prompts and formatted output
  - Input validation with helpful error messages
  - Graceful handling of invalid input (don't crash on bad input)
  - Display a welcome banner on startup

  ## Quality Standards
  - Use type hints throughout
  - Follow PEP 8 style conventions
  - Keep functions small and focused (single responsibility)
  - Add a clear docstring to each class and public method
  - Handle edge cases (empty input, non-existent IDs, non-numeric input)
  - The app should never crash from user input

## Response snapshot

Generated the Phase I feature specification for the Console Todo Application at `specs/001-console-todo-app/spec.md`. The spec covers:

- **6 user stories** (P1: Add Task, View Tasks, Menu Navigation; P2: Update, Delete, Toggle) with detailed Given/When/Then acceptance scenarios
- **17 functional requirements** (FR-001 through FR-017) covering all CRUD operations, input validation, and UI behavior
- **9 measurable success criteria** (SC-001 through SC-009) — all technology-agnostic
- **5 edge cases** identified (non-numeric input, Ctrl+C, whitespace-only, large lists, negative IDs)
- **Key entities**: Task and Task Collection
- **Assumptions**, **Constraints**, and **Out of Scope** sections clearly defined

Quality checklist at `specs/001-console-todo-app/checklists/requirements.md` — all 16 items pass. No [NEEDS CLARIFICATION] markers needed.

## Outcome

- Impact: Feature specification created, ready for planning phase
- Tests: Specification quality checklist — all 16 items PASS
- Files: 2 files created (spec.md, checklists/requirements.md)
- Next prompts: `/sp.clarify` to refine or `/sp.plan` to begin architecture planning
- Reflection: User prompt was comprehensive; no clarifications needed. All requirements were specific and testable.

## Evaluation notes (flywheel)

- Failure modes observed: Branch already existed (script failed), created spec structure manually
- Graders run and results (PASS/FAIL): Spec quality checklist — PASS (16/16)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
