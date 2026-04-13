import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def call_agent(system_prompt: str, user_message: str) -> str:
    """Call Claude with a role-specific system prompt and user message.

    Uses prompt caching on the system prompt to reduce costs across repeated
    calls with the same agent role.
    """
    client = get_client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=8096,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_message}],
    )
    block = response.content[0]
    if block.type != "text":
        raise ValueError(f"Unexpected response block type: {block.type}")
    return block.text
