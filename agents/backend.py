from core.llm import call_agent
from core.models import SessionState

SYSTEM_PROMPT = """You are a senior backend engineer specializing in Python and FastAPI.

Given a task description and project context, generate production-quality code.

Guidelines:
- Use FastAPI for API routes, Pydantic for data models
- Include a comment at the top with the intended file path (e.g. # file: api/routes/chat.py)
- Write complete, runnable code — no placeholders
- Follow Python best practices (type hints, docstrings on public functions)
- Keep it concise but complete"""


def run(task_description: str, session: SessionState) -> str:
    context = f"Project: {session.user_request}\n\nTask: {task_description}"
    return call_agent(SYSTEM_PROMPT, context)
