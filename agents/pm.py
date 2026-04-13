"""PM Agent — Orchestrator.

Receives a user request, calls Planner to get the task list, then routes
each task to the correct worker agent respecting dependencies.
"""

from core import state as state_mgr
from core.models import SessionState, Task, TaskStatus
from agents import backend, frontend, planner, qa

AGENT_MAP = {
    "backend": backend.run,
    "frontend": frontend.run,
    "qa": qa.run,
}


def run(user_request: str) -> SessionState:
    # 1. Create session
    session = state_mgr.new_session(user_request)
    session.status = "in_progress"
    state_mgr.save(session)

    # 2. Plan — Planner must always run first
    try:
        tasks_raw = planner.plan(user_request)
        session.task_queue = [Task(**t) for t in tasks_raw]
        state_mgr.save(session)
    except Exception as exc:
        session.status = "failed"
        session.messages.append({"role": "error", "content": f"Planner failed: {exc}"})
        state_mgr.save(session)
        raise

    # 3. Execute tasks respecting dependencies
    completed_ids: set[str] = set()
    max_rounds = len(session.task_queue) + 1  # safety limit

    for _ in range(max_rounds):
        pending = [t for t in session.task_queue if t.status == TaskStatus.pending]
        if not pending:
            break

        ready = [t for t in pending if all(dep in completed_ids for dep in t.dependencies)]
        if not ready:
            # All pending tasks are blocked — dependency deadlock
            for task in pending:
                task.status = TaskStatus.failed
                task.result = "Dependency deadlock: could not resolve dependencies"
            state_mgr.save(session)
            break

        for task in ready:
            task.status = TaskStatus.in_progress
            state_mgr.save(session)

            agent_fn = AGENT_MAP.get(task.agent)
            if agent_fn is None:
                task.status = TaskStatus.failed
                task.result = f"Unknown agent type: {task.agent}"
            else:
                try:
                    task.result = agent_fn(task.description, session)
                    task.status = TaskStatus.completed
                except Exception as exc:
                    task.status = TaskStatus.failed
                    task.result = str(exc)

            completed_ids.add(task.id)
            state_mgr.save(session)

    session.status = "completed"
    state_mgr.save(session)
    return session
