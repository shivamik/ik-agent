from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "folders",
    "operation": "write",
    "tags": [],
    "http_method": "post",
    "http_path": "/v1/bulkJobs/copyFolder",
    "operation_id": "copy-folder",
}


def _serialize_copy_job(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def copy_folders(
    *,
    destination_path: str,
    source_folder_path: str,
    include_versions: Optional[bool] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Copy a folder and its contents to another folder.

    - Optionally include file versions with include_versions.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    body = {
        "destination_path": destination_path,
        "source_folder_path": source_folder_path,
        "include_versions": include_versions,
    }
    filtered_body = {k: v for k, v in body.items() if v is not None}

    raw = await CLIENT.folders.copy(**filtered_body)
    response = _serialize_copy_job(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="copy_folders",
    description=(
        "Copy an ImageKit folder into another folder and optionally include "
        "all file versions.\n\n"
        "This operation runs as an asynchronous bulk job and returns a job ID "
        "that can be used to track progress."
    ),
)
async def copy_folders_tool(
    destination_path: str,
    source_folder_path: str,
    include_versions: Optional[bool] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Copy a folder and all its nested contents to another folder.

    This tool copies a source folder into a destination folder. The source
    folder, its nested sub-folders, files, and their versions are duplicated
    as part of a single asynchronous bulk operation.

    If a file in the destination folder has the same name as a source file,
    the source file and its versions are appended to the destination file’s
    version history instead of overwriting the file.

    By default, only the current version of each file is copied. When
    `include_versions` is set to `True`, all available versions of each
    file are copied.

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec` to select only the fields required from
    the response.

    Args:
        destination_path: The full path of the destination folder where
            the source folder will be copied.
        source_folder_path: The full path of the folder to be copied.
        include_versions: Whether to copy all versions of files contained
            within the source folder. Defaults to `False`.
        filter_spec: Optional glom-style filter specification used to reduce
            the response payload by selecting specific fields.
            Example: `.jobId`

    Returns:
        A dictionary containing the submitted bulk job details, typically:
            - jobId: Unique identifier for the asynchronous bulk job, which
              can be used to query job status.
    """
    return await copy_folders(
        destination_path=destination_path,
        source_folder_path=source_folder_path,
        include_versions=include_versions,
        filter_spec=filter_spec,
    )
