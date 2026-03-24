from datetime import datetime

from src.models.task import Task


class TaskService:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def get_task(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

    def add_task(self, title: str, description: str = "") -> Task:
        task = Task(id=self._next_id, title=title, description=description)
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get_all_tasks(self) -> list[Task]:
        return list(self._tasks.values())

    def get_summary(self) -> tuple[int, int]:
        total = len(self._tasks)
        completed = sum(1 for t in self._tasks.values() if t.completed)
        return (total, completed)

    def update_task(self, task_id: int, title: str | None, description: str | None) -> Task | None:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        if title is not None and title.strip():
            task.title = title.strip()
        if description is not None:
            task.description = description
        task.updated_at = datetime.now()
        return task

    def delete_task(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def toggle_task(self, task_id: int) -> Task | None:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        task.completed = not task.completed
        task.updated_at = datetime.now()
        return task
