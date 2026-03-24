# Research: Console Todo Application (Phase I)

**Feature**: 001-console-todo-app | **Date**: 2026-03-24

## Research Tasks & Findings

### R1: Python 3.13+ Dataclass Patterns for Domain Models

**Decision**: Use `@dataclass` from the standard library with `field()` defaults for optional attributes and timestamps.

**Rationale**: Dataclasses are the idiomatic Python approach for typed data containers. They provide `__init__`, `__repr__`, `__eq__` automatically. Python 3.13 fully supports `dataclasses` with no known issues. Using `field(default_factory=...)` for mutable defaults (like `datetime.now()`) avoids the classic mutable default argument bug.

**Alternatives considered**:
- **NamedTuple**: Immutable, which conflicts with the need to update task fields (title, description, completed, updated_at).
- **Pydantic BaseModel**: Adds a third-party dependency, violating the standard-library-only constraint. Will be appropriate in Phase II with FastAPI.
- **Plain dict**: No type safety, no IDE support, harder to migrate to SQLModel in Phase II.

### R2: In-Memory Collection Strategy

**Decision**: Use `dict[int, Task]` with an integer counter for auto-incrementing IDs, encapsulated in a `TaskService` class.

**Rationale**: Dictionary provides O(1) lookup/delete by integer key, which maps directly to the "find by ID" pattern used by all operations (update, delete, toggle). The counter never decrements (even after deletion), preventing ID reuse — consistent with database auto-increment behavior.

**Alternatives considered**:
- **List with index**: ID = index breaks when items are deleted (IDs shift). Using a separate ID field with list scan is O(n).
- **OrderedDict**: Unnecessary — insertion order is preserved in standard dict since Python 3.7+.

### R3: Console Input/Output Best Practices

**Decision**: Use `input()` for user prompts, `print()` for output, with `try/except ValueError` for integer parsing. Wrap the main loop in `try/except (KeyboardInterrupt, EOFError)` for clean shutdown.

**Rationale**: The standard `input()` function is sufficient for a console menu application. No need for `curses`, `readline`, or third-party TUI libraries given the simple numbered-menu interface.

**Key patterns**:
- Menu display: numbered options printed in a loop, `input("Enter choice: ")` for selection
- ID input: `int(input(...))` wrapped in `try/except ValueError` to catch non-numeric input
- Confirmation: `input("Are you sure? (y/n): ").lower().strip()` with default to "no" on unexpected input
- Title validation: `strip()` before length check to catch whitespace-only input

**Alternatives considered**:
- **Rich library**: Beautiful output but violates standard-library-only constraint.
- **argparse CLI**: Not appropriate — the app is interactive menu-driven, not command-line argument-driven.

### R4: Testing Strategy for Console Applications

**Decision**: Use pytest with `unittest.mock.patch` to mock `input()` and `builtins.print` for UI tests. Test models and services directly without mocking.

**Rationale**: Three test layers:
1. **Model tests**: Direct instantiation and assertion — no mocking needed
2. **Service tests**: Create `TaskService` instances, call methods, assert state — no mocking needed
3. **UI tests**: Mock `input()` with `side_effect` lists and capture `print()` calls to verify output formatting

**Alternatives considered**:
- **pytest-mock**: Convenience wrapper over `unittest.mock`, but adds a dev dependency. Standard `unittest.mock` is sufficient.
- **Click testing**: Not applicable — we're not using Click.
- **Subprocess testing**: Running the app as a subprocess and checking stdout — fragile, slow, harder to debug.

### R5: UV Project Configuration

**Decision**: Use `pyproject.toml` with UV-compatible configuration. Define Python 3.13+ requirement, pytest as dev dependency, and a script entry point.

**Rationale**: UV is the prescribed package manager per constitution. `pyproject.toml` is the modern Python standard (PEP 621) for project metadata. UV reads it natively.

**Key configuration**:
- `[project]` section: name, version, requires-python = ">=3.13"
- `[dependency-groups]` section: dev = ["pytest>=8.0"]
- `[project.scripts]` section: `todo = "src.main:main"` for `uv run todo` entry point

### R6: Status Indicators (UTF-8)

**Decision**: Use `✅` for complete and `❌` for incomplete tasks in the display list. The spec assumes UTF-8 console support.

**Rationale**: The spec explicitly states "console environment supports UTF-8 characters for status indicators" in assumptions. Checkmark and cross are universally recognized. The spec's acceptance scenarios reference "checkmark indicator" and "X indicator".

**Alternatives considered**:
- ASCII-only `[X]` / `[ ]`: Works everywhere but less visually distinctive. Could be used as fallback if UTF-8 issues arise, but spec assumes UTF-8.

### R7: Timestamp Handling

**Decision**: Use `datetime.now()` from the standard library. Store as `datetime` objects, display formatted as `YYYY-MM-DD HH:MM`.

**Rationale**: No timezone requirements for a single-user local console app. `datetime.now()` gives local time, which matches user expectations. Formatting with `strftime("%Y-%m-%d %H:%M")` is clean and readable in a console table.

**Alternatives considered**:
- **UTC with timezone**: Over-engineering for Phase I. Phase II with database storage will need timezone-aware timestamps.
