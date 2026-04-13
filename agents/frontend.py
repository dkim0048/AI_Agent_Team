from core.llm import call_agent
from core.models import SessionState

SYSTEM_PROMPT = """You are a senior frontend engineer specializing in React and TypeScript.

Given a task description and project context, generate production-quality UI code.

Guidelines:
- Use React with TypeScript; functional components and hooks only
- Include a comment at the top with the intended file path (e.g. # file: src/components/ChatBox.tsx)
- Write complete, runnable code — no placeholders
- Keep components focused and composable
- Use Tailwind CSS for styling if no other framework is specified"""


def run(task_description: str, session: SessionState) -> str:
    context = f"Project: {session.user_request}\n\nTask: {task_description}"
    return call_agent(SYSTEM_PROMPT, context)
