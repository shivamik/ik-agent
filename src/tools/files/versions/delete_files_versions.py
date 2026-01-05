from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "files.versions",
    "operation": "write",
    "tags": [],
    "http_method": "delete",
    "http_path": "/v1/files/{file_id}/versions/{version_id}",
    "operation_id": "delete-file-version",
}


def _serialize_delete_version_result(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def delete_files_versions(
    *,
    version_id: str,
    file_id: Optional[str] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Delete a non-current file version permanently.

    - Deleting a version returns an empty response body.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    body = {}
    if file_id is not None:
        body["file_id"] = file_id

    raw = await CLIENT.files.versions.delete(version_id, **body)
    response = _serialize_delete_version_result(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="delete_files_versions",
    description=("Permanently delete a non-current version of an ImageKit file."),
)
async def delete_files_versions_tool(
    version_id: str,
    file_id: Optional[str] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Permanently delete a non-current file version.

    This tool deletes a specific non-current version of a file.
    The current (latest) version of the file cannot be deleted using
    this API. To delete all versions of a file, use the `delete_files`
    tool instead.

    The operation is destructive and irreversible, and the API
    returns an empty response on success.

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec`, even though the response is typically
    empty.

    Args:
        version_id: Unique identifier of the file version to delete.
        file_id: Optional identifier of the parent file. Provided for
            additional validation or disambiguation when required.
        filter_spec: Optional glom-style filter specification used to
            reduce the response payload.

    Returns:
        An empty dictionary, indicating the file version was deleted
        successfully.
    """
    return await delete_files_versions(
        version_id=version_id,
        file_id=file_id,
        filter_spec=filter_spec,
    )
