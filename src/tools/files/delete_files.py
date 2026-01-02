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


@tool(
    name="delete_files",
    description="This API deletes the file and all its file versions permanently.\n\nNote: If a file or specific transformation has been requested in the past, then the response is cached. Deleting a file does not purge the cache. You can purge the cache using purge cache API.\n",
    inputSchema={
        "json": {
            "properties": {"file_id": {"type": "string"}},
            "required": ["file_id"],
            "type": "object",
        }
    },
)
async def delete_files_tool(
    file_id: str,
) -> Any:
    """
    Delete a file and all its versions permanently.

    This operation is idempotent. Deleting a file does not purge cache.
    """
    return await delete_files(file_id=file_id)
