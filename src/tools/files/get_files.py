from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "files",
    "operation": "read",
    "tags": [],
    "http_method": "get",
    "http_path": "/v1/files/{file_id}/details",
    "operation_id": "get-file-details",
}


def _serialize_file(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def get_files(
    *,
    file_id: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Retrieve details for the current version of a file.

    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.files.get(file_id)
    response = _serialize_file(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="get_files",
    description=(
        "Retrieve metadata and details for the current version of an ImageKit file."
    ),
)
async def get_files_tool(
    file_id: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Retrieve details for the current version of a file.

    This tool returns metadata and attributes for the current version of
    a file stored in the ImageKit media library. The response can include
    information such as file path, size, dimensions, tags, custom metadata,
    AI tags, and version details.

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec` to select only the fields required from
    the response.

    Args:
        file_id: Unique identifier of the file whose details are to be retrieved.
        filter_spec: Optional glom-style filter specification used to reduce
            the response payload by selecting specific fields.
            Example: `.name`, `.url`, `.customMetadata`

    Returns:
        A dictionary containing metadata for the current file version,
        including (but not limited to):
            - fileId: Unique identifier of the file.
            - filePath: Path of the file in the media library.
            - url: URL of the file.
            - size: File size in bytes.
            - width / height: Dimensions of the file (if applicable).
            - tags / AITags: User-defined and auto-generated tags.
            - versionInfo: Details of the current file version.
    """
    return await get_files(
        file_id=file_id,
        filter_spec=filter_spec,
    )
