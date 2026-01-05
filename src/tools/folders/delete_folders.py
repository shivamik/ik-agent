from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "folders",
    "operation": "write",
    "tags": [],
    "http_method": "delete",
    "http_path": "/v1/folder",
    "operation_id": "delete-folder",
}


def _serialize_delete_folder_result(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def delete_folders(
    *,
    folder_path: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Delete a folder and all its contents permanently.

    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.folders.delete(
        folder_path=folder_path,
    )
    response = _serialize_delete_folder_result(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="delete_folders",
)
async def delete_folders_tool(
    folder_path: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Permanently delete a folder and all its nested contents.

    This tool deletes a folder, including all nested sub-folders, files,
    and file versions. The deletion is irreversible and results in an
    empty response from the API.

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec`, even though the response is typically
    empty.

    Args:
        folder_path: The full path of the folder to be deleted.
            Example: `/folder/to/delete/`
        filter_spec: Optional glom-style filter specification. Included
            for consistency with other tools, though the response
            payload is usually empty.

    Returns:
        An empty dictionary, indicating the folder was deleted
        successfully.
    """
    return await delete_folders(
        folder_path=folder_path,
        filter_spec=filter_spec,
    )
