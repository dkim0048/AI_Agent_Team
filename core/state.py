import re
import uuid
from pathlib import Path

from core.models import SessionState, Task, TaskStatus

STATE_DIR = Path("state")

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def _path(session_id: str) -> Path:
    if not _UUID_RE.match(session_id):
        raise ValueError(f"Invalid session_id: {session_id!r}")
    return STATE_DIR / f"session_{session_id}.json"


def new_session(user_request: str) -> SessionState:
    session = SessionState(
        session_id=str(uuid.uuid4()),
        user_request=user_request,
    )
    save(session)
    return session


def load(session_id: str) -> SessionState:
    return SessionState.model_validate_json(_path(session_id).read_text())


def save(session: SessionState) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    _path(session.session_id).write_text(session.model_dump_json(indent=2))


def update_task(session: SessionState, task_id: str, **kwargs) -> SessionState:
    for task in session.task_queue:
        if task.id == task_id:
            for key, value in kwargs.items():
                setattr(task, key, value)
            break
    save(session)
    return session
