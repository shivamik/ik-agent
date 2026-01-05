from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


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
    description="Get the status of a cache invalidation request.",
)
async def get_cache_invalidation_tool(
    request_id: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Retrieve the status of a cache purge request.

    Use this tool to check whether a previously issued cache invalidation
    request has completed. Cache invalidation is asynchronous, and the
    status will transition from `Pending` to `Completed`.

    To reduce response size and improve performance, it is recommended
    to use `filter_spec` to select only the required fields from the
    response.

    Args:
        request_id: The request ID returned by the cache invalidation
            (purge) operation.
        filter_spec: Optional glom-style filter specification to reduce
            the response payload.
            Example: `.status`

    Returns:
        An object containing:
            - status: The current status of the purge request
              (`Pending` or `Completed`).
    """
    return await get_cache_invalidation(
        request_id=request_id,
        filter_spec=filter_spec,
    )
