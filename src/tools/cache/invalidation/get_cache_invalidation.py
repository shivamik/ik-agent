from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "cache.invalidation",
    "operation": "read",
    "tags": [],
    "http_method": "get",
    "http_path": "/v1/files/purge/{request_id}",
    "operation_id": "purge-status",
}


def _serialize_invalidation_status(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def get_cache_invalidation(
    *,
    request_id: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Get the status of a cache invalidation request.

    - Returns status (Pending or Completed) for the purge request.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.cache.invalidation.get(request_id)
    response = _serialize_invalidation_status(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="get_cache_invalidation",
    description="When using this tool, always use the `glom spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nThis API returns the status of a purge cache request.\n\n\n# Response Schema\n```json\n{\n  type: 'object',\n  properties: {\n    status: {\n      type: 'string',\n      description: 'Status of the purge request.',\n      enum: [        'Pending',\n        'Completed'\n      ]\n    }\n  }\n}\n```",
    inputSchema={
        "json": {
            "properties": {
                "filter_spec": {
                    "description": "A glom spec to apply to the response to "
                    "include certain fields. Consult the "
                    "output schema in the tool description to "
                    "see the fields that are available.\n"
                    "\n"
                    "For example: to include only the `name` "
                    "field in every object of a results array, "
                    'you can provide ".results[].name".\n'
                    "\n"
                    "For more information, see the [glom"
                    "documentation](http://glom.readthedocs.io/).",
                    "title": "filter_spec",
                    "type": "string",
                },
                "request_id": {"type": "string"},
            },
            "required": ["request_id"],
            "type": "object",
        }
    },
)
async def get_cache_invalidation_tool(
    request_id: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Get the status of a cache invalidation request.

    Use the request ID from the purge call to check whether the purge
    is Pending or Completed.

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await get_cache_invalidation(
        request_id=request_id,
        filter_spec=filter_spec,
    )
