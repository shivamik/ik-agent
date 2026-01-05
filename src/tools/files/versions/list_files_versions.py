from typing import Any, Dict, List, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "files.versions",
    "operation": "read",
    "tags": [],
    "http_method": "get",
    "http_path": "/v1/files/{file_id}/versions",
    "operation_id": "list-file-versions",
}


def _serialize_version(version: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(version, "model_dump"):
        return version.model_dump()
    if hasattr(version, "dict"):
        return version.dict()
    return dict(version)


async def list_files_versions(
    *,
    file_id: str,
    filter_spec: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """
    List all versions for a file.

    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw_versions = await CLIENT.files.versions.list(file_id)
    response = [_serialize_version(version) for version in raw_versions]
    return maybe_filter(filter_spec, response)


@tool(
    name="list_files_versions",
    description=("List all versions of an ImageKit file."),
)
async def list_files_versions_tool(
    file_id: str,
    filter_spec: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """List all versions of a file.

    This tool returns metadata and attributes for all versions of a file
    stored in the ImageKit media library, including the current and
    non-current versions.

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec` to select only the fields required from
    the response.

    Args:
        file_id: Unique identifier of the file whose versions are to be listed.
        filter_spec: Optional glom-style filter specification used to reduce
            the response payload by selecting specific fields.
            Example: `.versionInfo`, `.name`, `.url`

    Returns:
        A list of dictionaries, each representing a file version and
        containing metadata such as:
            - versionInfo: Details of the file version.
            - fileId: Unique identifier of the file.
            - filePath: Path of the file.
            - url: URL of the file version.
            - size: File size in bytes.
            - width / height: Dimensions (if applicable).
            - tags / AITags: User-defined and auto-generated tags.
    """
    return await list_files_versions(
        file_id=file_id,
        filter_spec=filter_spec,
    )
