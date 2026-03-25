# Quickstart: Console Todo Application (Phase I)

## Prerequisites

- Python 3.13+
- UV package manager ([install guide](https://docs.astral.sh/uv/getting-started/installation/))

## Setup

```bash
# Clone and enter the project
git clone <repo-url>
cd "HACKATHON 02"

# Install dependencies (creates virtual environment automatically)
uv sync
```

## Run the Application

```bash
uv run todo
```

This launches the interactive console menu:

```
========================================
       Welcome to Todo App!
========================================

--- Todo Menu ---
1. Add Task
2. View All Tasks
3. Update Task
4. Delete Task
5. Toggle Complete
6. Exit

Enter your choice (1-6):
```

## Run Tests

```bash
uv run pytest
```

## Project Structure

```
src/
├── main.py              # Entry point (menu loop)
├── models/task.py       # Task dataclass
├── services/task_service.py  # CRUD operations
└── ui/console.py        # Display & input handling

tests/
├── test_task_model.py
├── test_task_service.py
└── test_console_ui.py
```

## Key Operations

| Menu Option | What It Does |
|-------------|-------------|
| 1. Add Task | Prompts for title (required) and description (optional) |
| 2. View All Tasks | Shows all tasks with ID, title, status, date + summary |
| 3. Update Task | Updates title/description by ID (blank = keep existing) |
| 4. Delete Task | Deletes by ID with confirmation prompt |
| 5. Toggle Complete | Flips complete/incomplete status by ID |
| 6. Exit | Exits with goodbye message |
