from __future__ import annotations

from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


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
    description="When using this tool, always use the `filter_spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nThis will move one folder into another. The selected folder, its nested folders, files, and their versions are moved in this operation. Note: If any file at the destination has the same name as the source file, then the source file and its versions will be appended to the destination file version history.\n\n\n# Response Schema\n```json\n{\n  type: 'object',\n  title: 'Async Bulk Job Response',\n  description: 'Job submitted successfully. A `jobId` will be returned.',\n  properties: {\n    jobId: {\n      type: 'string',\n      description: 'Unique identifier of the bulk job. This can be used to check the status of the bulk job.\\n'\n    }\n  },\n  required: [    'jobId'\n  ]\n}\n```",
    inputSchema={
        "json": {
            "properties": {
                "destination_path": {
                    "description": "Full path to the destination folder "
                    "where you want to move the source "
                    "folder into.\n",
                    "type": "string",
                },
                "filter_spec": {
                    "description": "A filter_spec to apply to the response to "
                    "include certain fields. Consult the "
                    "output schema in the tool description to "
                    "see the fields that are available.\n"
                    "\n"
                    "For example: to include only the `name` "
                    "field in every object of a results array, "
                    'you can provide ".results[].name".\n'
                    "\n"
                    "For more information, see the [jq "
                    "documentation](https://jqlang.org/manual/).",
                    "title": "filter_spec",
                    "type": "string",
                },
                "source_folder_path": {
                    "description": "The full path to the source folder "
                    "you want to move.\n",
                    "type": "string",
                },
            },
            "required": ["destination_path", "source_folder_path"],
            "type": "object",
        }
    },
)
async def move_folders_tool(
    destination_path: str,
    source_folder_path: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Move a folder and its contents to another folder.

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await move_folders(
        destination_path=destination_path,
        source_folder_path=source_folder_path,
        filter_spec=filter_spec,
    )
