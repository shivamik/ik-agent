from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "folders",
    "operation": "write",
    "tags": [],
    "http_method": "post",
    "http_path": "/v1/bulkJobs/moveFolder",
    "operation_id": "move-folder",
}


def _serialize_move_job(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def move_folders(
    *,
    destination_path: str,
    source_folder_path: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Move a folder and its contents to another folder.

    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.folders.move(
        destination_path=destination_path,
        source_folder_path=source_folder_path,
    )
    response = _serialize_move_job(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="move_folders",
)
async def move_folders_tool(
    destination_path: str,
    source_folder_path: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Move a folder and all its nested contents to another folder.

    This tool moves a source folder into a destination folder. The source
    folder, its nested sub-folders, files, and all file versions are moved
    as part of a single asynchronous bulk operation.

    If a file in the destination folder has the same name as a source file,
    the source file and its versions are appended to the destination file’s
    version history instead of overwriting the file.

    To reduce response size and improve performance, it is recommended to
    provide a `filter_spec` to select only the fields required from the
    response.

    Args:
        destination_path: The full path of the destination folder where the
            source folder will be moved.
        source_folder_path: The full path of the folder to be moved.
        filter_spec: Optional glom-style filter specification used to reduce
            the response payload by selecting specific fields.
            Example: `.jobId`

    Returns:
        A dictionary containing the submitted bulk job details, typically:
            - jobId: Unique identifier for the asynchronous bulk job, which
              can be used to query job status.
    """
    return await move_folders(
        destination_path=destination_path,
        source_folder_path=source_folder_path,
        filter_spec=filter_spec,
    )
