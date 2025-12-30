from __future__ import annotations

from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "cache.invalidation",
    "operation": "write",
    "tags": [],
    "http_method": "post",
    "http_path": "/v1/files/purge",
    "operation_id": "purge-cache",
}


def _serialize_invalidation_result(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def create_cache_invalidation(
    *,
    url: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Purge CDN and ImageKit cache for a URL.

    - Purge is asynchronous; use the returned request ID to track status.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.cache.invalidation.create({"url": url})
    response = _serialize_invalidation_result(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="create_cache_invalidation",
    description="When using this tool, always use the `jq_filter` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nThis API will purge CDN cache and ImageKit.io's internal cache for a file.  Note: Purge cache is an asynchronous process and it may take some time to reflect the changes.\n\n\n# Response Schema\n```json\n{\n  type: 'object',\n  properties: {\n    requestId: {\n      type: 'string',\n      description: 'Unique identifier of the purge request. This can be used to check the status of the purge request.\\n'\n    }\n  }\n}\n```",
    inputSchema={
        "json": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL of the file to be purged.\n",
                },
                "filter_spec": {
                    "type": "string",
                    "title": "jq filter_spec",
                    "description": 'A jq filter to apply to the response to include certain fields. Consult the output schema in the tool description to see the fields that are available.\n\nFor example: to include only the `name` field in every object of a results array, you can provide ".results[].name".\n\nFor more information, see the [jq documentation](https://jqlang.org/manual/).',
                },
            },
            "required": ["url"],
        }
    },
)
async def create_cache_invalidation_tool(
    url: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Purge CDN and ImageKit cache for a URL.

    This is an asynchronous operation. The response includes a request ID
    you can use to query purge status later.

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await create_cache_invalidation(url=url, filter_spec=filter_spec)
