from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class Task(BaseModel):
    id: str
    description: str
    agent: Literal["backend", "frontend", "qa"]
    status: TaskStatus = TaskStatus.pending
    dependencies: list[str] = []
    result: Optional[str] = None


class SessionState(BaseModel):
    session_id: str
    user_request: str
    status: Literal["pending", "in_progress", "completed", "failed"] = "pending"
    task_queue: list[Task] = []
    file_tree: dict = {}
    messages: list[dict] = []
