from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "files",
    "operation": "write",
    "tags": [],
    "http_method": "put",
    "http_path": "/v1/files/rename",
    "operation_id": "rename-file",
}


def _serialize_rename_result(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def rename_files(
    *,
    file_path: str,
    new_file_name: str,
    purge_cache: Optional[bool] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Rename a file and all of its versions.

    - Optionally purge cache for the old URL via purge_cache.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    body = {
        "file_path": file_path,
        "new_file_name": new_file_name,
        "purge_cache": purge_cache,
    }
    filtered_body = {k: v for k, v in body.items() if v is not None}

    raw = await CLIENT.files.rename(**filtered_body)
    response = _serialize_rename_result(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="rename_files",
    description=(
        "Rename an ImageKit file and all of its versions, with an option to "
        "purge cached URLs."
    ),
)
async def rename_files_tool(
    file_path: str,
    new_file_name: str,
    purge_cache: Optional[bool] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Rename a file and all of its versions.

    This tool renames an existing file in the ImageKit media library.
    All versions of the file are renamed as part of the operation.
    After renaming, old file URLs stop working, although cached CDN
    responses may continue to be served unless explicitly purged.

    When `purge_cache` is set to `True`, a wildcard CDN purge request
    is issued for the old file path and all of its versions. This purge
    request is counted against the monthly purge quota.

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec` to select only the fields required from
    the response.

    Args:
        file_path: Full path of the file to be renamed.
        new_file_name: New name for the file. Allowed characters include
            alphanumeric characters (including unicode), `.`, `_`, and `-`.
            Any other characters are replaced with underscores (`_`).
        purge_cache: Whether to purge CDN cache for old file URLs.
            Defaults to `False`.
        filter_spec: Optional glom-style filter specification used to
            reduce the response payload by selecting specific fields.
            Example: `.purgeRequestId`

    Returns:
        A dictionary containing rename operation metadata, typically:
            - purgeRequestId: Identifier of the CDN purge request, present
              only when cache purging is enabled.
    """
    return await rename_files(
        file_path=file_path,
        new_file_name=new_file_name,
        purge_cache=purge_cache,
        filter_spec=filter_spec,
    )
