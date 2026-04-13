import os

from fastapi import FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from agents import pm
from core import state as state_mgr
from core.models import SessionState

app = FastAPI(title="AI Dev Team", version="0.1.0")

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def _require_api_key(key: str | None = Security(_api_key_header)) -> None:
    expected = os.environ.get("API_KEY")
    if not expected:
        return  # API_KEY not set — dev mode, skip auth
    if key != expected:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")


class RunRequest(BaseModel):
    request: str = Field(..., min_length=1, max_length=2000)


class RunResponse(BaseModel):
    session_id: str
    status: str
    tasks: list[dict]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse, dependencies=[Security(_require_api_key)])
def run(body: RunRequest):
    session: SessionState = pm.run(body.request)
    return RunResponse(
        session_id=session.session_id,
        status=session.status,
        tasks=[t.model_dump() for t in session.task_queue],
    )


@app.get("/sessions/{session_id}", dependencies=[Security(_require_api_key)])
def get_session(session_id: str):
    try:
        session = state_mgr.load(session_id)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="Session not found")
    return session.model_dump()
