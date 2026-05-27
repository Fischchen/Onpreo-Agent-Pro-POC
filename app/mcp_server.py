"""Onpreo MCP server: a single call-activity tool over Streamable HTTP.

Run:  uv run python -m app.mcp_server
Serves http://127.0.0.1:8000/mcp ; requires header `Authorization: Bearer <MCP_BEARER_TOKEN>`.
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from app.crud import create_call_activity
from app.db import get_session

mcp = FastMCP("onpreo-poc", stateless_http=True, json_response=True)


class CallActivityResult(BaseModel):
    activity_id: int
    contact_id: int | None


@mcp.tool()
def onpreo_create_call_activity(
    title: str | None,
    description: str | None,
    caller_first_name: str | None,
    caller_last_name: str | None,
) -> CallActivityResult:
    """Record a call activity for the current caller in onpreo. Use when the call has produced a meaningful summary or outcome worth recording on the contact's CRM record. If the caller has stated their name during this call, always fill caller_first_name and caller_last_name so the contact record can be enriched. Leave them null only if the name was never mentioned."""
    with get_session() as session:
        activity = create_call_activity(
            session, title, description, caller_first_name, caller_last_name
        )
        return CallActivityResult(activity_id=activity.id, contact_id=activity.contact_id)


def _make_app():
    """FastMCP's Starlette app wrapped in a minimal ASGI bearer-token gate."""
    from starlette.responses import JSONResponse

    from app.config import settings

    inner = mcp.streamable_http_app()
    expected = f"Bearer {settings.mcp_bearer_token}"

    async def app(scope, receive, send):
        if scope["type"] == "http":
            headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}
            if headers.get("authorization") != expected:
                response = JSONResponse({"error": "unauthorized"}, status_code=401)
                await response(scope, receive, send)
                return
        await inner(scope, receive, send)

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(_make_app(), host="127.0.0.1", port=8000)
