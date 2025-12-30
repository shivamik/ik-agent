from __future__ import annotations

from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


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
    description="When using this tool, always use the `filter_spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nThis API deletes a non-current file version permanently. The API returns an empty response.\n\nNote: If you want to delete all versions of a file, use the delete file API.\n\n\n# Response Schema\n```json\n{\n  type: 'object',\n  properties: {}\n}\n```",
    inputSchema={
        "json": {
            "type": "object",
            "properties": {
                "fileId": {
                    "type": "string",
                },
                "versionId": {
                    "type": "string",
                },
                "filter_spec": {
                    "type": "string",
                    "title": "filter_spec",
                    "description": 'A filter_spec to apply to the response to include certain fields. Consult the output schema in the tool description to see the fields that are available.\n\nFor example: to include only the `name` field in every object of a results array, you can provide ".results[].name".\n\nFor more information, see the [jq documentation](https://jqlang.org/manual/).',
                },
            },
            "required": ["fileId", "versionId"],
        }
    },
)
async def delete_files_versions_tool(
    version_id: str,
    file_id: Optional[str] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Delete a non-current file version permanently.

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await delete_files_versions(
        version_id=version_id,
        file_id=file_id,
        filter_spec=filter_spec,
    )
