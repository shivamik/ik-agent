from __future__ import annotations

from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "folders",
    "operation": "write",
    "tags": [],
    "http_method": "delete",
    "http_path": "/v1/folder",
    "operation_id": "delete-folder",
}


def _serialize_delete_folder_result(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def delete_folders(
    *,
    folder_path: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Delete a folder and all its contents permanently.

    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.folders.delete(
        folder_path=folder_path,
    )
    response = _serialize_delete_folder_result(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="delete_folders",
    description="When using this tool, always use the `filter_spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nThis will delete a folder and all its contents permanently. The API returns an empty response.\n\n\n# Response Schema\n```json\n{\n  type: 'object',\n  properties: {}\n}\n```",
    inputSchema={
        "json": {
            "type": "object",
            "properties": {
                "folderPath": {
                    "type": "string",
                    "description": "Full path to the folder you want to delete. For example `/folder/to/delete/`.\n",
                },
                "filter_spec": {
                    "type": "string",
                    "title": "filter_spec",
                    "description": 'A filter_spec to apply to the response to include certain fields. Consult the output schema in the tool description to see the fields that are available.\n\nFor example: to include only the `name` field in every object of a results array, you can provide ".results[].name".\n\nFor more information, see the [jq documentation](https://jqlang.org/manual/).',
                },
            },
            "required": ["folderPath"],
        }
    },
)
async def delete_folders_tool(
    folder_path: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Delete a folder and all its contents permanently.

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await delete_folders(
        folder_path=folder_path,
        filter_spec=filter_spec,
    )
