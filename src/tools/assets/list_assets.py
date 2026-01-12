from typing import Any, Dict, List, Optional
from strands import tool
from urllib.parse import urlparse, unquote

from src.clients import CLIENT
from src.utils.utils import maybe_filter


def _extract_filename_from_url(file_url: str) -> str:
    """
    Extract and decode filename from an ImageKit URL.
    """
    parsed = urlparse(file_url)
    if not parsed.path:
        raise ValueError("Invalid file_url: missing path")

    filename = parsed.path.split("/")[-1]
    if not filename:
        raise ValueError("Invalid file_url: could not extract filename")

    return unquote(filename)


METADATA: Dict[str, Any] = {
    "resource": "assets",
    "operation": "read",
    "tags": [],
    "http_method": "get",
    "http_path": "/v1/files",
    "operation_id": "list-and-search-assets",
}


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
    filter_spec: Optional[Any] = None,
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

    return maybe_filter(filter_spec, response)


@tool(
    name="list_assets",
)
async def list_assets_tool(
    file_type: Optional[str] = None,
    file_url: Optional[str] = None,
    limit: Optional[int] = 10,
    path: Optional[str] = None,
    search_query: Optional[str] = None,
    skip: Optional[int] = None,
    sort: Optional[str] = None,
    type: Optional[str] = None,
    filter_spec: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """
    List and search assets in the ImageKit media library.
    You can search for files using file_url from imagekit DAM
    "https://ik.imagekit.io/your_imagekit_id/path/to/file.jpg".

    This tool returns files, file_id, file versions, and folders from ImageKit.
    And other file related details
    You can list all assets or narrow results using filters such as
    file type, asset type, folder path, sorting, pagination, or a
    Lucene-like search query.

    To improve performance and reduce response size, always prefer using
    `filter_spec` to select only the fields you need from each asset.

    Args:
        file_type:
            Filter results by file type.
            Allowed values:
            - "all" — include all file types
            - "image" — include only image files
            - "non-image" — include only non-image files (e.g., video, JS, CSS)

        file_url:
            Public URL of a specific file to look up. Copied from imagekit DAM.
            Example: "https://ik.imagekit.io/your_imagekit_id/path/to/file.jpg"

            When `file_url` is provided, the tool will attempt to find
            the exact file matching that URL.

        type:
            Filter results by asset type.
            Allowed values:
            - "file" — return only files
            - "file-version" — return specific file versions
            - "folder" — return only folders
            - "all" — return both files and folders (excludes file versions)

        path:
            Restrict results to a specific folder path.
            Example: "/sales-banner/" will only search within that folder.

        search_query:
            Advanced search query using a Lucene-like syntax.
            Example: createdAt > "7d"

            When `search_query` is provided, some other filters
            (such as tags, type, or name) may be ignored by the API.

        sort:
            Sort results by a supported field in ascending or descending order.
            Examples:
            - "ASC_NAME", "DESC_CREATED", "ASC_SIZE", "DESC_RELEVANCE"

        limit:
            Maximum number of results to return. Defaults to 10.

        skip:
            Number of results to skip before returning results
            (used for pagination).

        filter_spec:
            A glom specification used to project or reshape the response.
            This should be used to reduce payload size and improve performance.

            Examples:
            - "name"
            - ["name"]
            - [{"name": "name", "url": "url"}]

    Returns:
        A list of assets (files and  folders), optionally
        transformed using `filter_spec`.
    """
    resolved_search_query = search_query

    # ---- file_url handling ----
    if file_url:
        filename = _extract_filename_from_url(file_url)

        # Build name-based search
        file_url_query = f'name="{filename}"'

        # Merge with existing search_query if present
        if resolved_search_query:
            resolved_search_query = f"({resolved_search_query}) AND {file_url_query}"
        else:
            resolved_search_query = file_url_query

    # ---- Call underlying API ----
    results = await list_assets(
        file_type=file_type,
        limit=limit,
        path=path,
        search_query=resolved_search_query,
        skip=skip,
        sort=sort,
        type=type,
        filter_spec=filter_spec,
    )

    # ---- Post-filter for exact URL match ----
    if file_url:
        matched = [
            asset
            for asset in results
            if isinstance(asset, dict)
            and "url" in asset
            and asset["url"].startswith(file_url.split("?")[0])
        ]

        if not matched:
            raise ValueError(
                f"Could not find file details for the provided file_url: {file_url}"
            )

        return matched

    return results
