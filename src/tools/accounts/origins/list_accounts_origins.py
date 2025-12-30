from __future__ import annotations

from typing import Any, Dict, List

from strands import tool

from src.clients import CLIENT


METADATA: Dict[str, Any] = {
    "resource": "accounts.origins",
    "operation": "read",
    "tags": [],
    "http_method": "get",
    "http_path": "/v1/accounts/origins",
    "operation_id": "list-origins",
}


def _serialize_origin(origin: Any) -> Dict[str, Any]:
    """
    Normalize SDK origin objects into plain dicts.
    """
    if hasattr(origin, "model_dump"):
        return origin.model_dump()
    if hasattr(origin, "dict"):
        return origin.dict()
    return dict(origin)


async def list_accounts_origins() -> List[Dict[str, Any]]:
    """
    List all configured origins for the current account.
    """
    raw = await CLIENT.accounts.origins.list()
    return [_serialize_origin(origin) for origin in raw]


@tool(
    name="list_accounts_origins",
    description="**Note:** This API is currently in beta.  \nReturns an array of all configured origins for the current account.\n",
    inputSchema={
        "json": {
            "type": "object",
            "properties": {},
            "required": [],
        }
    },
)
async def list_accounts_origins_tool() -> List[Dict[str, Any]]:
    """
    List all configured origins for the current account.
    """
    return await list_accounts_origins()
