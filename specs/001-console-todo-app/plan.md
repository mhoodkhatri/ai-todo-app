# Implementation Plan: Console Todo Application (Phase I)

**Branch**: `001-console-todo-app` | **Date**: 2026-03-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-console-todo-app/spec.md`

## Summary

Build an in-memory Python console application providing full CRUD operations and task completion toggling. The app presents a numbered interactive menu, stores tasks in memory using a dictionary-based collection, and validates all user input gracefully. This is Phase I of the Evolution of Todo hackathon project — no persistence, no external dependencies, Python standard library only.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Python standard library only (dataclasses, datetime)
**Storage**: In-memory dictionary (no file or database persistence)
**Testing**: pytest (standard Python test framework, installed via UV as dev dependency)
**Target Platform**: Console/terminal (any OS with Python 3.13+)
**Project Type**: single — simple Python project layout per constitution Phase I rules
**Performance Goals**: N/A — single-user console app, no latency or throughput targets
**Constraints**: Standard library only, in-memory storage, UV package manager, no GUI/web
**Scale/Scope**: Single user, ephemeral data, ~6 menu operations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | PASS | spec.md exists and is complete; plan follows workflow |
| II. AI-First Implementation | PASS | Using Claude Code with Spec-Kit Plus |
| III. Phased Evolution | PASS | Phase I scope: in-memory console app with Basic Level features (Add, Delete, Update, View, Mark Complete) |
| IV. Cloud-Native Architecture | N/A | Not applicable until Phase II |
| V. Clean Code & Structure | PASS | Python 3.13+, UV package manager, no hardcoded secrets. Note: Constitution requires WSL 2 for Windows users — verify development environment |
| VI. Monorepo Organization | PASS | Phase I uses simple layout: `/src`, `README.md`, `CLAUDE.md` — no monorepo overhead |
| Technology Stack | PASS | Python 3.13+, UV — all prescribed technologies for Phase I |

**Gate Result**: PASS — no violations. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/001-console-todo-app/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── main.py              # Entry point: welcome banner, menu loop, exit
├── models/
│   ├── __init__.py
│   └── task.py          # Task dataclass with validation
├── services/
│   ├── __init__.py
│   └── task_service.py  # TaskService: CRUD operations, in-memory store
└── ui/
    ├── __init__.py
    └── console.py       # Display formatting, input prompts, error messages

tests/
├── __init__.py
├── test_task_model.py   # Task creation, validation, defaults
├── test_task_service.py # CRUD operations, ID auto-increment, edge cases
└── test_console_ui.py   # Output formatting, input handling (mocked I/O)

pyproject.toml           # UV project config, Python 3.13+ requirement
```

**Structure Decision**: Single project layout per constitution Principle VI (Phase I). Three-layer separation: models (data), services (logic), ui (presentation). Entry point at `src/main.py`. Tests mirror source structure under `tests/`.

## Complexity Tracking

No constitution violations — table not required.

## Architecture Decisions

### Decision 1: Three-Layer Separation (Models / Services / UI)

**Rationale**: Separating data representation (models), business logic (services), and user interaction (ui) enables independent testing of each layer and prepares the codebase for Phase II migration to FastAPI + Next.js, where these layers map naturally to ORM models, API services, and frontend components.

**Alternative rejected**: Single-file script — would work for Phase I but creates a migration burden and violates clean code principles.

### Decision 2: Dataclass-Based Task Model

**Rationale**: Python `dataclasses` provide clean, type-hinted data containers with auto-generated `__init__`, `__repr__`, and `__eq__`. No need for heavier patterns (attrs, Pydantic) since there's no serialization or API validation in Phase I.

**Alternative rejected**: Plain dict — no type safety, no validation, harder to refactor into SQLModel in Phase II.

### Decision 3: Dictionary-Based In-Memory Store with Auto-Increment Counter

**Rationale**: `dict[int, Task]` provides O(1) lookup by ID, simple enumeration, and easy deletion. A class-level counter tracks the next ID, mimicking database auto-increment for consistent behavior across phases.

**Alternative rejected**: List-based storage — O(n) lookup by ID, deletion shifts indices, ID management is fragile.

### Decision 4: Input Validation in UI Layer, Business Rules in Service Layer

**Rationale**: The UI layer handles type coercion (string → int for IDs) and format validation (empty input, length limits). The service layer handles business rules (ID existence, status toggling). This separation keeps each layer focused and testable.

### Decision 5: Graceful Ctrl+C Handling via KeyboardInterrupt

**Rationale**: Wrapping the main loop in a try/except for `KeyboardInterrupt` ensures clean exit with a goodbye message, meeting the edge case requirement from the spec. `EOFError` is also caught for piped input scenarios.
