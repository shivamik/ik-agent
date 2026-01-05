from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "files",
    "operation": "write",
    "tags": [],
    "http_method": "post",
    "http_path": "/v1/files/copy",
    "operation_id": "copy-file",
}


def _serialize_copy_result(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def copy_files(
    *,
    destination_path: str,
    source_file_path: str,
    include_file_versions: Optional[bool] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Copy a file from one folder to another.

    - When destination has the same name, versions may be appended.
    - include_file_versions copies all versions when true.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    body = {
        "destination_path": destination_path,
        "source_file_path": source_file_path,
        "include_file_versions": include_file_versions,
    }
    filtered_body = {k: v for k, v in body.items() if v is not None}

    raw = await CLIENT.files.copy(**filtered_body)
    response = _serialize_copy_result(raw)
    return maybe_filter(filter_spec, response)


from typing import Any, Dict, Optional

from strands import tool


@tool(
    name="copy_files",
    description=(
        "Copy an ImageKit file into another folder and optionally include "
        "all file versions."
    ),
)
async def copy_files_tool(
    destination_path: str,
    source_file_path: str,
    include_file_versions: Optional[bool] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Copy a file from one folder to another.

    This tool copies a file from the source path into the specified
    destination folder. If a file with the same name already exists
    at the destination, the source file and its versions are appended
    to the destination file’s version history instead of overwriting
    the file.

    By default, only the current version of the file is copied. When
    `include_file_versions` is set to `True`, all available versions
    of the file are copied.

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec` to select only the fields required from
    the response.

    Args:
        destination_path: Full path of the destination folder where the
            file will be copied.
        source_file_path: Full path of the file to be copied.
        include_file_versions: Whether to copy all versions of the file.
            Defaults to `False`.
        filter_spec: Optional glom-style filter specification used to
            reduce the response payload by selecting specific fields.
            Example: `.name`

    Returns:
        An empty dictionary, indicating the file was copied successfully.
    """
    return await copy_files(
        destination_path=destination_path,
        source_file_path=source_file_path,
        include_file_versions=include_file_versions,
        filter_spec=filter_spec,
    )
