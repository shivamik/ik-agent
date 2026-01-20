from typing import Any, Dict, List, Optional

from src.clients import CLIENT
from src.utils.utils import maybe_filter
from src.utils.filter_responses import filter_response


def _serialize_asset(asset: Any) -> Any:
    """
    Normalize SDK asset objects into plain dicts for filtering/returning.
    """
    if hasattr(asset, "model_dump"):
        return asset.model_dump()
    if hasattr(asset, "dict"):
        return asset.dict()
    return asset


async def list_assets(
    *,
    file_type: Optional[str] = None,
    limit: Optional[int] = None,
    path: Optional[str] = None,
    search_query: Optional[str] = None,
    skip: Optional[int] = None,
    sort: Optional[str] = None,
    type: Optional[str] = None,
    keys_to_filter: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """
    Low-level helper that calls the ImageKit SDK to list/search assets.

    - Returns files, file versions, and folders from ImageKit.
    - Applies `filter_spec` (glom spec) to shrink/reshape the response.
    - Drops `None` parameters so SDK defaults are preserved.

    Common filters:
    - file_type: all | image | non-image
    - type: file | file-version | folder | all
    - search_query: Lucene-like query (e.g., createdAt > "7d"); overrides tags/type/name
    - path: restrict results to a folder (use search_query for recursive searches)
    - sort: ASC/DESC on name, created/updated, height/width, size, relevance
    - limit/skip: pagination controls
    """
    body = {
        "file_type": file_type,
        "limit": limit,
        "path": path,
        "search_query": search_query,
        "skip": skip,
        "sort": sort,
        "type": type,
    }

    # Drop unset values so we don't override SDK defaults.
    filtered_body = {k: v for k, v in body.items() if v is not None}

    raw_assets = await CLIENT.assets.list(**filtered_body)
    response = [_serialize_asset(asset) for asset in raw_assets]

    return filter_response(response, key_names=keys_to_filter, tool_name="list_assets")
