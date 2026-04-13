# CLAUDE.md — AI Dev Team Multi-Agent System

## Project Goal

Build a multi-agent system that acts as an AI development team.
The user gives a high-level order (e.g. "build a RAG chatbot") and the system autonomously decomposes, delegates, and generates a working codebase.

The existing repo (Paper_Analysis_Chatbot) serves as the reference implementation and first test case.

---

## Architecture

### Pattern: Orchestrator-Worker (Legacy, no LangGraph)

```
User Request
    ↓
PM Agent (Orchestrator)
    ├── Planner Agent     → generates task list + file structure
    ├── Frontend Agent    → UI / React components
    ├── Backend Agent     → FastAPI routes, business logic, DB
    └── QA Agent          → testing, linting, bug fixes
         ↓
Shared State Store (local JSON or DynamoDB)
         ↓
Generated Codebase → Git → AWS Deploy
```

### Agent Design Principle

Each agent = same Claude API, different system prompt.

```python
response = anthropic.messages.create(
    model="claude-sonnet-4-20250514",
    system="<agent-specific role and instructions>",
    messages=[{"role": "user", "content": task}]
)
```

No LangGraph or CrewAI — all orchestration logic is implemented directly.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent brain | Anthropic Claude API (claude-sonnet-4-20250514) |
| API framework | FastAPI |
| Orchestration | Custom (no framework) |
| Shared state | Local JSON file (dev) → DynamoDB (prod) |
| Deployment | AWS ECS |
| CI/CD | GitHub Actions |
| Language | Python 3.11+ |

---

## Agent Roles & System Prompts

### PM Agent (Orchestrator)
- Receives raw user request
- Calls Planner first, gets task list
- Routes each task to the correct worker agent
- Tracks task completion via shared state
- Returns final result to user

### Planner Agent
- Input: user request string
- Output: JSON list of tasks with fields — `id`, `description`, `agent`, `dependencies[]`
- Must be called before any worker agents

### Frontend Agent
- Generates React/Next.js components
- Follows existing repo's frontend conventions if present

### Backend Agent
- Generates FastAPI routes, Pydantic models, DB logic
- Follows existing repo's backend structure

### QA Agent
- Reviews generated code
- Runs lint checks, identifies bugs
- Returns fix suggestions or patches

---

## Shared State Schema

```json
{
  "session_id": "uuid",
  "user_request": "build a RAG chatbot",
  "status": "in_progress",
  "task_queue": [
    {
      "id": "task_001",
      "description": "Set up FastAPI project structure",
      "agent": "backend",
      "status": "pending",
      "dependencies": []
    }
  ],
  "file_tree": {},
  "messages": []
}
```

State is persisted to `state/session_{id}.json` during development.

---

## Project Structure (Target)

```
/
├── CLAUDE.md               ← this file
├── agents/
│   ├── pm.py               ← orchestrator
│   ├── planner.py
│   ├── frontend.py
│   ├── backend.py
│   └── qa.py
├── core/
│   ├── state.py            ← shared state manager
│   ├── llm.py              ← Claude API wrapper
│   └── models.py           ← Pydantic schemas
├── api/
│   └── main.py             ← FastAPI entrypoint
├── state/                  ← session state files (gitignored)
├── tests/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── Dockerfile
└── requirements.txt
```

---

## Development Rules

1. **Do not rewrite existing working code** unless explicitly asked
2. **Planner agent must always run first** before any worker agents
3. **All agents are stateless** — state lives only in the shared state store
4. **Each agent call is a single Claude API request** — no streaming for now
5. **Start simple** — get PM → Planner → Backend working end-to-end before adding Frontend/QA
6. **Validate Planner output** as JSON before passing to PM routing logic

---

## First Task (Start Here)

1. Audit existing codebase and document what's reusable
2. Create the project scaffold based on the target structure above
3. Implement `core/llm.py` — simple Claude API wrapper
4. Implement `core/state.py` — JSON-based state manager
5. Implement `agents/planner.py` — test with "build a RAG chatbot" input
6. Implement `agents/pm.py` — wire up orchestration logic

---

## Environment Variables

```
ANTHROPIC_API_KEY=
AWS_REGION=ap-southeast-2
DYNAMODB_TABLE=agent_state
```

---

## Deployment Target

- AWS ECS (Fargate) — one service per agent or monolith to start
- GitHub Actions triggers deploy on push to `main`
- Melbourne region: `ap-southeast-2`
