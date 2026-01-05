from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "files",
    "operation": "write",
    "tags": [],
    "http_method": "post",
    "http_path": "/v1/files/move",
    "operation_id": "move-file",
}


def _serialize_move_result(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def move_files(
    *,
    destination_path: str,
    source_file_path: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Move a file and all its versions from one folder to another.

    - If destination has the same name, versions are appended.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.files.move(
        destination_path=destination_path,
        source_file_path=source_file_path,
    )
    response = _serialize_move_result(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="move_files",
    description=(
        "Move an ImageKit file into another folder, including all of its versions."
    ),
)
async def move_files_tool(
    destination_path: str,
    source_file_path: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Move a file and all its versions to another folder.

    This tool moves a file from the source path into the specified
    destination folder. All versions of the file are moved as part
    of the operation.

    If a file with the same name already exists at the destination,
    the source file and its versions are appended to the destination
    file rather than overwriting it.

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec` to select only the fields required from
    the response.

    Args:
        destination_path: Full path of the destination folder where
            the file will be moved.
        source_file_path: Full path of the file to be moved.
        filter_spec: Optional glom-style filter specification used to
            reduce the response payload by selecting specific fields.
            Example: `.name`

    Returns:
        An empty dictionary, indicating the file was moved successfully.
    """
    return await move_files(
        destination_path=destination_path,
        source_file_path=source_file_path,
        filter_spec=filter_spec,
    )
