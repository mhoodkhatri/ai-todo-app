from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __repr__(self) -> str:
        status = "completed" if self.completed else "incomplete"
        return f"Task(id={self.id}, title='{self.title}', {status})"
