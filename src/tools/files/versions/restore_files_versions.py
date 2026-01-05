from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "files.versions",
    "operation": "write",
    "tags": [],
    "http_method": "put",
    "http_path": "/v1/files/{file_id}/versions/{version_id}/restore",
    "operation_id": "restore-file-version",
}


def _serialize_restored_version(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def restore_files_versions(
    *,
    version_id: str,
    file_id: Optional[str] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Restore a file version as the current version.

    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    body = {}
    if file_id is not None:
        body["file_id"] = file_id

    raw = await CLIENT.files.versions.restore(version_id, **body)
    response = _serialize_restored_version(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="restore_files_versions",
    description=(
        "Restore a specific version of an ImageKit file as the current version."
    ),
)
async def restore_files_versions_tool(
    version_id: str,
    file_id: Optional[str] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Restore a file version as the current version.

    This tool restores a specified non-current file version and promotes
    it to become the current (latest) version of the file. The restored
    version’s metadata and attributes become active immediately.

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec` to select only the fields required from
    the response.

    Args:
        version_id: Unique identifier of the file version to restore.
        file_id: Optional identifier of the parent file. Provided for
            additional validation or disambiguation when required.
        filter_spec: Optional glom-style filter specification used to
            reduce the response payload by selecting specific fields.
            Example: `.versionInfo`, `.url`, `.name`

    Returns:
        A dictionary containing metadata for the restored file version,
        now marked as the current version. The response typically
        includes:
            - fileId: Unique identifier of the file.
            - versionInfo: Details of the restored version.
            - filePath: Path of the file.
            - url: URL of the restored file.
            - updatedAt: Timestamp indicating when the restore occurred.
    """
    return await restore_files_versions(
        version_id=version_id,
        file_id=file_id,
        filter_spec=filter_spec,
    )
