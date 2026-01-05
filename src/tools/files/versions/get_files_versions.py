from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "files.versions",
    "operation": "read",
    "tags": [],
    "http_method": "get",
    "http_path": "/v1/files/{file_id}/versions/{version_id}",
    "operation_id": "get-file-version-details",
}


def _serialize_version(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def get_files_versions(
    *,
    version_id: str,
    file_id: Optional[str] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Retrieve details for a specific file version.

    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    body = {}
    if file_id is not None:
        body["file_id"] = file_id

    raw = await CLIENT.files.versions.get(version_id, **body)
    response = _serialize_version(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="get_files_versions",
    description=(
        "Retrieve metadata and details for a specific version of an ImageKit file."
    ),
)
async def get_files_versions_tool(
    version_id: str,
    file_id: Optional[str] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Retrieve details for a specific file version.

    This tool returns metadata and attributes for a specific version of
    a file stored in the ImageKit media library. The response may include
    file properties, dimensions, tags, custom metadata, AI tags, and
    version-specific information.

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec` to select only the fields required from
    the response.

    Args:
        version_id: Unique identifier of the file version to retrieve.
        file_id: Optional identifier of the parent file. Provided for
            additional validation or disambiguation when required.
        filter_spec: Optional glom-style filter specification used to
            reduce the response payload by selecting specific fields.
            Example: `.name`, `.url`, `.versionInfo`

    Returns:
        A dictionary containing metadata for the requested file version,
        including (but not limited to):
            - fileId: Unique identifier of the file.
            - versionInfo: Details of the file version.
            - filePath: Path of the file.
            - url: URL of the file version.
            - size: File size in bytes.
            - width / height: Dimensions (if applicable).
            - tags / AITags: User-defined and auto-generated tags.
    """
    return await get_files_versions(
        version_id=version_id,
        file_id=file_id,
        filter_spec=filter_spec,
    )
