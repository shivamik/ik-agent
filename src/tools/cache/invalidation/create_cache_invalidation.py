from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


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
    description="Purge CDN and ImageKit cache for a file URL.",
)
async def create_cache_invalidation_tool(
    url: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Invalidate cached content for a file URL.

    This tool purges both the CDN cache and ImageKit's internal cache for
    the specified file URL.

    Cache invalidation is an asynchronous operation. The API returns a
    purge request identifier that can be used to check the status of the
    purge operation later.

    To reduce response size and improve performance, it is recommended
    to use `filter_spec` to select only the required fields from the
    response.

    Args:
        url: Full URL of the file whose cache should be invalidated.
        filter_spec: Optional glom-style filter specification to reduce
            the response payload.
            Example: `.requestId`

    Returns:
        An object containing:
            - requestId: Unique identifier of the purge request.
    """
    return await create_cache_invalidation(
        url=url,
        filter_spec=filter_spec,
    )
