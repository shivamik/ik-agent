import logging
from strands import tool
from urllib.parse import urlparse, unquote
from typing import Any, Dict, List, Optional

from src.utils.tool_utils import list_assets
from src.config import LOG_LEVEL

logger = logging.getLogger("tools.assets.list_assets")
logger.setLevel(LOG_LEVEL)


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
    keys_to_filter: List[str] = None,
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

        keys_to_filter:
            List of keys to include in the returned asset dictionaries.
            This helps reduce response size by returning only the
            fields you need.


    Returns:
        Output Keys: 'keys': {'file_path', 'tags', 'name', 'mime', 'custom_metadata',
        'height', 'type', 'created_at', 'size', 'url', 'is_private_file', 'version_info',
        'description', 'file_type', 'is_published', 'width', 'folder_path',
        'thumbnail', 'updated_at', 'selected_fields_schema', 'custom_coordinates',
        'folder_id', 'file_id', 'has_alpha', 'ai_tags'}}
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

    logger.info(f"keys_to_filter: {keys_to_filter}")
    # ---- Call underlying API ----
    results = await list_assets(
        file_type=file_type,
        limit=limit,
        path=path,
        search_query=resolved_search_query,
        skip=skip,
        sort=sort,
        type=type,
        keys_to_filter=keys_to_filter,
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
