from typing import Any, Dict

from strands import tool

from src.clients import CLIENT


METADATA: Dict[str, Any] = {
    "resource": "files",
    "operation": "write",
    "tags": [],
    "http_method": "delete",
    "http_path": "/v1/files/{file_id}",
    "operation_id": "delete-file",
}


async def delete_files(
    *,
    file_id: str,
) -> Any:
    """
    Delete a file and all its versions permanently.

    Note: Deleting a file does not purge cache; use cache invalidation separately.
    """
    return await CLIENT.files.delete(file_id)


from typing import Any

from strands import tool


@tool(
    name="delete_files",
    description=(
        "Permanently delete an ImageKit file and all of its versions.\n\n"
        "This operation does not automatically purge CDN cache."
    ),
)
async def delete_files_tool(
    file_id: str,
) -> Any:
    """Permanently delete a file and all its versions.

    This tool deletes a file and all of its historical versions.
    The operation is idempotent—repeating the request has no additional
    effect once the file is deleted.

    Deleting a file does not purge cached URLs. If the file or any of its
    transformations were previously requested, cached responses may
    continue to be served until explicitly purged using the purge cache API.

    Args:
        file_id: Unique identifier of the file to be deleted.

    Returns:
        An empty response indicating the file was deleted successfully.
    """
    return await delete_files(file_id=file_id)
