from typing import Any, Dict, Optional, Sequence

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "files.bulk",
    "operation": "write",
    "tags": [],
    "http_method": "post",
    "http_path": "/v1/files/batch/deleteByFileIds",
    "operation_id": "delete-multiple-files",
}


def _serialize_bulk_delete(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def delete_files_bulk(
    *,
    file_ids: Sequence[str],
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Delete multiple files and all their versions permanently.

    - Up to 100 file IDs can be specified per request.
    - Deleting a file does not purge cache; use cache invalidation separately.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.files.bulk.delete(file_ids=list(file_ids))
    response = _serialize_bulk_delete(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="delete_files_bulk",
    description=(
        "Permanently delete multiple ImageKit files and all of their versions "
        "in a single bulk operation."
    ),
)
async def delete_files_bulk_tool(
    file_ids: Sequence[str],
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Permanently delete multiple files and all of their versions.

    This tool deletes multiple files from the ImageKit media library.
    All versions of each file are deleted as part of the operation.
    The deletion is irreversible.

    Deleting files does not automatically purge cached URLs. If the files
    or their transformations were previously requested, cached responses
    may continue to be served until explicitly purged using the purge
    cache API.

    A maximum of 100 file IDs can be deleted in a single request.

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec` to select only the fields required from
    the response.

    Args:
        file_ids: Sequence of file IDs to delete.
            Maximum allowed is 100 file IDs per request.
        filter_spec: Optional glom-style filter specification used to
            reduce the response payload by selecting specific fields.
            Example: `.successfullyDeletedFileIds`

    Returns:
        A dictionary containing the bulk deletion result, typically:
            - successfullyDeletedFileIds: List of file IDs that were
              successfully deleted.
    """
    return await delete_files_bulk(
        file_ids=file_ids,
        filter_spec=filter_spec,
    )
