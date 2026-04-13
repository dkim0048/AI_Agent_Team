import json
import re

from core.llm import call_agent

SYSTEM_PROMPT = """You are a software project planner for an AI development team.

Given a user request, output a JSON array of tasks needed to complete the project.
Each task must have exactly these fields:
- id: string like "task_001", "task_002", etc.
- description: clear, actionable description of what needs to be built
- agent: one of "backend", "frontend", or "qa"
- dependencies: array of task ids that must complete first (empty array if none)

Rules:
- Always start with backend tasks (API, data models, business logic)
- Frontend tasks depend on backend tasks they consume
- QA tasks depend on the tasks they are testing
- Keep tasks focused and concrete

Output ONLY a valid JSON array. No markdown, no explanation, no code fences."""


def plan(user_request: str) -> list[dict]:
    raw = call_agent(SYSTEM_PROMPT, user_request)
    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw.strip())
    tasks = json.loads(raw)
    if not isinstance(tasks, list):
        raise ValueError(f"Planner returned non-list: {type(tasks)}")
    return tasks
