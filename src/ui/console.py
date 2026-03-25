from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.task import Task
    from src.services.task_service import TaskService


def display_welcome_banner() -> None:
    print("=" * 40)
    print("       Welcome to Todo App!")
    print("=" * 40)


def display_menu() -> None:
    print("\n--- Todo Menu ---")
    print("1. Add Task")
    print("2. View All Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Toggle Complete")
    print("6. Exit")


def get_valid_int_input(prompt: str) -> int | None:
    try:
        return int(input(prompt).strip())
    except ValueError:
        display_error("Please enter a valid number")
        return None


def display_error(message: str) -> None:
    print(f"Error: {message}")


def display_success(message: str) -> None:
    print(f"Success: {message}")


def format_task_row(task: Task) -> str:
    status = "\u2705" if task.completed else "\u274c"
    date_str = task.created_at.strftime("%Y-%m-%d %H:%M")
    return f"  [{task.id}] {status} {task.title} (Created: {date_str})"


def prompt_add_task(service: TaskService) -> None:
    print("\n--- Add New Task ---")
    title = input("Enter task title: ").strip()
    if not title:
        display_error("Title is required")
        return
    if len(title) > 200:
        display_error("Title must be 200 characters or less")
        return

    description = input("Enter task description (optional): ").strip()
    if len(description) > 1000:
        display_error("Description must be 1000 characters or less")
        return

    task = service.add_task(title, description)
    display_success(f"Task created successfully with ID: {task.id}")


def display_all_tasks(service: TaskService) -> None:
    print("\n--- All Tasks ---")
    tasks = service.get_all_tasks()
    if not tasks:
        print("No tasks found.")
        return
    for task in tasks:
        print(format_task_row(task))
    total, completed = service.get_summary()
    incomplete = total - completed
    print(f"\nTotal: {total} tasks ({completed} complete, {incomplete} incomplete)")


def prompt_update_task(service: TaskService) -> None:
    print("\n--- Update Task ---")
    task_id = get_valid_int_input("Enter task ID to update: ")
    if task_id is None:
        return
    task = service.get_task(task_id)
    if task is None:
        display_error(f"Task with ID {task_id} not found")
        return

    print(f"Current title: {task.title}")
    print(f"Current description: {task.description}")

    new_title = input("Enter new title (blank to keep current): ").strip()
    if new_title and len(new_title) > 200:
        display_error("Title must be 200 characters or less")
        return

    new_desc = input("Enter new description (blank to keep current): ").strip()
    if new_desc and len(new_desc) > 1000:
        display_error("Description must be 1000 characters or less")
        return

    title_arg = new_title if new_title else None
    desc_arg = new_desc if new_desc else None
    service.update_task(task_id, title_arg, desc_arg)
    display_success(f"Task {task_id} updated successfully")


def prompt_delete_task(service: TaskService) -> None:
    print("\n--- Delete Task ---")
    task_id = get_valid_int_input("Enter task ID to delete: ")
    if task_id is None:
        return
    task = service.get_task(task_id)
    if task is None:
        display_error(f"Task with ID {task_id} not found")
        return

    confirm = input(f"Are you sure you want to delete task {task_id}? (y/n): ").strip().lower()
    if confirm == "y":
        service.delete_task(task_id)
        display_success(f"Task {task_id} deleted successfully")
    else:
        print("Delete cancelled.")


def prompt_toggle_task(service: TaskService) -> None:
    print("\n--- Toggle Task Completion ---")
    task_id = get_valid_int_input("Enter task ID to toggle: ")
    if task_id is None:
        return
    task = service.toggle_task(task_id)
    if task is None:
        display_error(f"Task with ID {task_id} not found")
        return
    status = "complete" if task.completed else "incomplete"
    display_success(f"Task {task_id} marked as {status}")
