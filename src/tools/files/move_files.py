from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "files",
    "operation": "write",
    "tags": [],
    "http_method": "post",
    "http_path": "/v1/files/move",
    "operation_id": "move-file",
}


def _serialize_move_result(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def move_files(
    *,
    destination_path: str,
    source_file_path: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Move a file and all its versions from one folder to another.

    - If destination has the same name, versions are appended.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.files.move(
        destination_path=destination_path,
        source_file_path=source_file_path,
    )
    response = _serialize_move_result(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="move_files",
    description="When using this tool, always use the `filter_spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nThis will move a file and all its versions from one folder to another. \n\nNote: If any file at the destination has the same name as the source file, then the source file and its versions will be appended to the destination file.\n\n\n# Response Schema\n```json\n{\n  type: 'object',\n  properties: {}\n}\n```",
    inputSchema={
        "json": {
            "properties": {
                "destination_path": {
                    "description": "Full path to the folder you want to "
                    "move the above file into.\n",
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
                    "For more information, see the [glom"
                    "documentation](http://glom.readthedocs.io/).",
                    "title": "filter_spec",
                    "type": "string",
                },
                "source_file_path": {
                    "description": "The full path of the file you want to move.\n",
                    "type": "string",
                },
            },
            "required": ["destination_path", "source_file_path"],
            "type": "object",
        }
    },
)
async def move_files_tool(
    destination_path: str,
    source_file_path: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Move a file and all its versions from one folder to another.

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await move_files(
        destination_path=destination_path,
        source_file_path=source_file_path,
        filter_spec=filter_spec,
    )
